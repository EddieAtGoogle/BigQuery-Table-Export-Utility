"""
API Client for BigQuery Export Service

This module handles all communication with the Cloud Run backend service.
"""

from typing import List, Dict, Any, Optional
import requests
from google.auth import default
from google.auth.transport import requests as auth_requests
from structlog import get_logger

from .auth import SCOPES

# Initialize logger
logger = get_logger(__name__)

class APIError(Exception):
    """Custom exception for API-related errors."""
    pass

class APIClient:
    """Client for interacting with the BigQuery Export Service API."""
    
    def __init__(self, base_url: str):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the Cloud Run service
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        logger.info("api_client_initialized", base_url=self.base_url)
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token."""
        try:
            credentials, project = default(scopes=SCOPES)
            auth_req = auth_requests.Request()
            
            logger.debug(
                "token_refresh_attempt",
                scopes=SCOPES,
                project=project,
                token_expired=getattr(credentials, 'expired', None),
                token_valid=getattr(credentials, 'valid', None)
            )
            
            credentials.refresh(auth_req)
            
            headers = {
                'Authorization': f'Bearer {credentials.token}',
                'Content-Type': 'application/json'
            }
            
            # Log token info (first/last 4 chars only for security)
            token = credentials.token
            if token:
                token_preview = f"{token[:4]}...{token[-4:]}"
                logger.debug(
                    "auth_headers_generated",
                    token_preview=token_preview,
                    token_type=type(token).__name__,
                    token_length=len(token)
                )
            else:
                logger.error("auth_token_missing")
                
            return headers
            
        except Exception as e:
            logger.exception(
                "auth_header_generation_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            raise APIError(f"Failed to generate authentication headers: {str(e)}")
    
    def _handle_error(self, response: requests.Response) -> None:
        """Handle error responses from the API."""
        try:
            error_data = response.json()
            message = error_data.get('error', str(response.status_code))
            details = error_data.get('details', {})
            
            logger.error(
                "api_error_response",
                status_code=response.status_code,
                message=message,
                details=details,
                headers=dict(response.request.headers),
                url=response.request.url
            )
            
            raise APIError(f"{message}: {details}")
        except ValueError:
            logger.error(
                "api_error_parsing_failed",
                status_code=response.status_code,
                response_text=response.text,
                headers=dict(response.request.headers),
                url=response.request.url
            )
            raise APIError(f"HTTP {response.status_code}: {response.text}")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make an authenticated request to the API."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        logger.debug(
            "making_api_request",
            method=method,
            url=url,
            headers={k: v for k, v in headers.items() if k != 'Authorization'}
        )
        
        response = self.session.request(method, url, headers=headers, **kwargs)
        
        logger.debug(
            "api_response_received",
            method=method,
            url=url,
            status_code=response.status_code,
            response_length=len(response.content) if response.content else 0
        )
        
        if response.status_code != 200:
            self._handle_error(response)
            
        return response
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """List available BigQuery datasets."""
        response = self._make_request('GET', '/api/v1/datasets')
        return response.json()['datasets']
    
    def list_tables(self, dataset_id: str) -> List[Dict[str, Any]]:
        """List tables in a BigQuery dataset."""
        response = self._make_request('GET', f'/api/v1/datasets/{dataset_id}/tables')
        return response.json()['tables']
    
    def export_table(
        self,
        dataset_id: str,
        table_id: str,
        destination_prefix: Optional[str] = None,
        compression: bool = False
    ) -> Dict[str, Any]:
        """Export a BigQuery table to CSV."""
        data = {
            'dataset_id': dataset_id,
            'table_id': table_id,
            'compression': compression
        }
        
        if destination_prefix:
            data['destination_prefix'] = destination_prefix
            
        response = self._make_request('POST', '/api/v1/export', json=data)
        return response.json()
    
    def merge_files(
        self,
        source_prefix: str,
        destination_filename: str,
        delete_source_files: bool = True,
        compress_output: bool = True
    ) -> Dict[str, Any]:
        """Merge multiple CSV files into a single file."""
        data = {
            'source_prefix': source_prefix,
            'destination_filename': destination_filename,
            'delete_source_files': delete_source_files,
            'compress_output': compress_output
        }
        
        response = self._make_request('POST', '/api/v1/merge', json=data)
        return response.json()
    
    def get_download_url(self, blob_name: str, expiration_seconds: int = 3600) -> str:
        """
        Get a GCS URL for downloading a file.
        
        Args:
            blob_name: Name of the blob to download
            expiration_seconds: Not used for GCS URLs
            
        Returns:
            str: GCS URL for downloading the file (requires authentication)
        """
        response = self._make_request('GET', f'/api/v1/download/{blob_name}')
        return response.json()['signed_url']  # This will now be a GCS URL 