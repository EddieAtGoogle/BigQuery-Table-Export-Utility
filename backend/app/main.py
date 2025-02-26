"""
BigQuery Table Export Service - Main Application

This module provides a simple Flask application for exporting BigQuery tables to CSV.
For more information, see: https://cloud.google.com/bigquery/docs/exporting-data
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from structlog import get_logger
from google.auth.transport import requests as auth_requests
from google.oauth2 import id_token

from app.config.settings import AppConfig
from app.services.export_service import BigQueryExportService
from app.utils.error_handlers import register_error_handlers, ValidationError, AuthenticationError

# Initialize logger
logger = get_logger(__name__)

def verify_auth_token(request) -> None:
    """Verify the authentication token from the request."""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        logger.error("auth_header_missing")
        raise AuthenticationError("No authorization header")
        
    try:
        # Extract token from Bearer header
        if not auth_header.startswith('Bearer '):
            logger.error("invalid_auth_header_format", header=auth_header)
            raise AuthenticationError("Invalid authorization header format")
            
        token = auth_header.split('Bearer ')[1]
        
        # Log token info (first/last 4 chars only for security)
        token_preview = f"{token[:4]}...{token[-4:]}"
        logger.debug(
            "verifying_token",
            token_preview=token_preview,
            token_length=len(token)
        )
        
        # Verify the token using Google's tokeninfo endpoint
        auth_req = auth_requests.Request()
        resp = auth_req.session.get(
            f'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={token}'
        )
        
        if resp.status_code != 200:
            logger.error(
                "token_verification_failed",
                status_code=resp.status_code,
                response=resp.text
            )
            raise AuthenticationError("Invalid token")
            
        token_info = resp.json()
        
        # Verify token has required scope
        required_scope = 'https://www.googleapis.com/auth/cloud-platform'
        if required_scope not in token_info.get('scope', '').split(' '):
            logger.error(
                "insufficient_scope",
                required=required_scope,
                provided=token_info.get('scope')
            )
            raise AuthenticationError("Token does not have required scope")
        
        logger.info(
            "token_verified",
            email=token_info.get('email'),
            expires_in=token_info.get('expires_in'),
            scope=token_info.get('scope')
        )
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.exception("auth_verification_error", error=str(e))
        raise AuthenticationError("Authentication failed")

def create_export_service(app):
    """Create and initialize the export service."""
    return BigQueryExportService(
        project_id=app.config['PROJECT_ID'],
        export_bucket=app.config['EXPORT_BUCKET']
    )

def create_app(config_class=None):
    """
    Create and configure the Flask application.
    
    Args:
        config_class: Optional configuration class to use instead of default AppConfig
    
    Returns:
        Flask application instance
    """
    # Create Flask app
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # Load configuration
    app.config.from_object(config_class or AppConfig())

    # Register error handlers
    register_error_handlers(app)

    # Initialize the export service
    app.export_service = create_export_service(app)
    
    # Add authentication middleware
    @app.before_request
    def authenticate():
        """Verify authentication for all API endpoints."""
        # Skip authentication for non-API endpoints
        if not request.path.startswith('/api/'):
            return
            
        logger.debug(
            "authenticating_request",
            path=request.path,
            method=request.method,
            headers={k: v for k, v in request.headers.items() if k.lower() != 'authorization'}
        )
        
        verify_auth_token(request)

    # Register routes
    @app.route('/api/v1/datasets', methods=['GET'])
    def list_datasets():
        """List available BigQuery datasets."""
        try:
            datasets = []
            for dataset_list_item in app.export_service.bq_client.list_datasets():
                # Get full dataset to access all properties
                dataset_ref = app.export_service.bq_client.dataset(dataset_list_item.dataset_id)
                dataset = app.export_service.bq_client.get_dataset(dataset_ref)
                datasets.append({
                    'id': dataset.dataset_id,
                    'friendly_name': dataset.friendly_name or dataset.dataset_id,
                    'location': dataset.location
                })
            return jsonify({'datasets': datasets})
        except Exception as e:
            logger.exception("list_datasets_error", error=str(e))
            raise

    @app.route('/api/v1/datasets/<dataset_id>/tables', methods=['GET'])
    def list_tables(dataset_id: str):
        """List tables in a BigQuery dataset."""
        try:
            # Get dataset reference and verify existence
            dataset_ref = app.export_service.bq_client.dataset(dataset_id)
            try:
                app.export_service.bq_client.get_dataset(dataset_ref)
            except Exception:
                raise ValidationError(f"Dataset not found: {dataset_id}")
            
            # List tables and get full table objects
            tables = []
            for table_list_item in app.export_service.bq_client.list_tables(dataset_ref):
                try:
                    # Get full table object to access all properties
                    table = app.export_service.bq_client.get_table(table_list_item.reference)
                    tables.append({
                        'id': table.table_id,
                        'type': table.table_type,
                        'num_rows': table.num_rows if hasattr(table, 'num_rows') else None,
                        'size_bytes': table.num_bytes if hasattr(table, 'num_bytes') else None,
                        'created': table.created.isoformat() if hasattr(table, 'created') else None,
                        'modified': table.modified.isoformat() if hasattr(table, 'modified') else None
                    })
                except Exception as e:
                    logger.warning(
                        "table_metadata_error",
                        table=table_list_item.table_id,
                        error=str(e)
                    )
                    # Include basic information if full table metadata is unavailable
                    tables.append({
                        'id': table_list_item.table_id,
                        'type': 'UNKNOWN',
                        'num_rows': None,
                        'size_bytes': None
                    })
            
            return jsonify({'tables': tables})
            
        except ValidationError:
            raise
        except Exception as e:
            logger.exception("list_tables_error", dataset=dataset_id, error=str(e))
            raise

    @app.route('/api/v1/export', methods=['POST'])
    def export_table():
        """Export a BigQuery table to CSV."""
        try:
            data = request.get_json()
            result = app.export_service.export_table(
                dataset_id=data['dataset_id'],
                table_id=data['table_id'],
                destination_prefix=data.get('destination_prefix'),
                compression=data.get('compression', False)
            )
            return jsonify(result)
        except Exception as e:
            logger.exception("export_error", request=request.json, error=str(e))
            raise

    @app.route('/api/v1/merge', methods=['POST'])
    def merge_files():
        """Merge multiple CSV files into a single file."""
        try:
            data = request.get_json()
            result = app.export_service.merge_csv_files(
                source_prefix=data['source_prefix'],
                destination_filename=data['destination_filename'],
                delete_source_files=data.get('delete_source_files', True),
                compress_output=data.get('compress_output', True)
            )
            return jsonify(result)
        except Exception as e:
            logger.exception("merge_error", request=request.json, error=str(e))
            raise

    @app.route('/api/v1/download/<path:blob_name>', methods=['GET'])
    def get_download_url(blob_name: str):
        """Generate a signed URL for downloading a file."""
        try:
            url = app.export_service.get_signed_url(blob_name)
            return jsonify({
                'signed_url': url,
                'expires_in': 3600  # 1 hour
            })
        except Exception as e:
            logger.exception("download_url_error", blob=blob_name, error=str(e))
            raise

    # Log application startup
    logger.info(
        "application_startup",
        export_bucket=app.config['EXPORT_BUCKET'],
        environment=app.config['ENVIRONMENT']
    )

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port) 