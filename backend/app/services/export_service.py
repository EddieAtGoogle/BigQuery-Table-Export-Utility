"""
BigQuery Export Service

This module handles the export of BigQuery tables to CSV files in Cloud Storage.
For more information, see:
- https://cloud.google.com/bigquery/docs/exporting-data
- https://cloud.google.com/python/docs/reference/bigquery/latest
"""

import asyncio
import uuid
import gzip
import io
from datetime import datetime
from typing import List, Optional, Dict, Any

from google.cloud import bigquery
from google.cloud import storage
from structlog import get_logger

from app.utils.error_handlers import ExportError, ValidationError

logger = get_logger(__name__)

class BigQueryExportService:
    """Service for handling BigQuery table exports to CSV."""

    def __init__(self, project_id: str, export_bucket: str):
        """
        Initialize the export service.
        
        Args:
            project_id: Google Cloud project ID
            export_bucket: Name of the Cloud Storage bucket for exports
        """
        self.project_id = project_id
        self.export_bucket = export_bucket
        self.bq_client = bigquery.Client(project=project_id)
        self.storage_client = storage.Client(project=project_id)
        self.bucket = self.storage_client.bucket(export_bucket)

    def export_table(
        self,
        dataset_id: str,
        table_id: str,
        destination_prefix: Optional[str] = None,
        compression: bool = False
    ) -> Dict[str, Any]:
        """
        Export a BigQuery table to CSV files in Cloud Storage.
        
        Args:
            dataset_id: BigQuery dataset ID
            table_id: BigQuery table ID
            destination_prefix: Optional prefix for the exported files
            compression: Whether to compress the exported files
        
        Returns:
            Dict containing export job information and status
        """
        try:
            # Verify dataset exists
            dataset_ref = self.bq_client.dataset(dataset_id)
            try:
                self.bq_client.get_dataset(dataset_ref)
            except Exception as e:
                raise ValidationError(f"Dataset not found: {dataset_id}")

            # Verify table exists and get full table object
            table_ref = dataset_ref.table(table_id)
            try:
                table = self.bq_client.get_table(table_ref)
            except Exception as e:
                raise ValidationError(f"Table not found: {table_id} in dataset {dataset_id}")

            # Generate a unique export ID
            export_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            
            # Create the destination path
            base_path = f"{destination_prefix}/{timestamp}" if destination_prefix else timestamp
            destination_uris = [f"gs://{self.export_bucket}/{base_path}/export-*.csv"]
            if compression:
                destination_uris = [uri + ".gz" for uri in destination_uris]

            # Configure the export job
            job_config = bigquery.ExtractJobConfig()
            job_config.destination_format = bigquery.DestinationFormat.CSV
            job_config.compression = bigquery.Compression.GZIP if compression else None
            job_config.field_delimiter = ','
            job_config.print_header = True
            
            # Start the export job
            extract_job = self.bq_client.extract_table(
                table,  # Use full table object
                destination_uris,
                job_config=job_config
            )
            
            logger.info(
                "export_job_started",
                export_id=export_id,
                dataset=dataset_id,
                table=table_id,
                destination=destination_uris[0]
            )
            
            # Wait for the job to complete
            self._wait_for_job(extract_job)
            
            # Get the exported files
            prefix = f"{base_path}/export-"
            blobs = list(self.bucket.list_blobs(prefix=prefix))
            
            return {
                'export_id': export_id,
                'status': 'completed',
                'files': [blob.name for blob in blobs],
                'total_files': len(blobs),
                'destination_prefix': base_path,
                'compression': compression
            }
            
        except ValidationError:
            raise
        except Exception as e:
            logger.exception(
                "export_error",
                dataset=dataset_id,
                table=table_id,
                error=str(e)
            )
            raise ExportError(f"Export failed: {str(e)}")

    def _wait_for_job(self, job: bigquery.ExtractJob, timeout: int = 3600) -> None:
        """
        Wait for a BigQuery job to complete.
        
        Args:
            job: BigQuery job to monitor
            timeout: Maximum time to wait in seconds
        
        Raises:
            ExportError: If the job fails or times out
        """
        import time
        start_time = time.time()
        
        try:
            while True:
                job.reload()
                
                if job.error_result:
                    raise ExportError(
                        f"Export job failed: {job.error_result}",
                        details={'job_id': job.job_id}
                    )
                
                if job.done():
                    return
                
                if time.time() - start_time > timeout:
                    raise ExportError(
                        f"Export job timed out after {timeout} seconds",
                        details={'job_id': job.job_id}
                    )
                
                time.sleep(5)
                
        except Exception as e:
            if not isinstance(e, ExportError):
                raise ExportError(f"Job monitoring failed: {str(e)}")
            raise

    def merge_csv_files(
        self,
        source_prefix: str,
        destination_filename: str,
        delete_source_files: bool = True,
        compress_output: bool = True
    ) -> Dict[str, Any]:
        """
        Merge multiple CSV files into a single file.
        
        Args:
            source_prefix: Prefix of the source files in the bucket
            destination_filename: Name of the merged file
            delete_source_files: Whether to delete the source files after merging
            compress_output: Whether to compress the final merged file
        
        Returns:
            Dict containing information about the merged file
        """
        try:
            # List all source files
            blobs = list(self.bucket.list_blobs(prefix=source_prefix))
            if not blobs:
                raise ValidationError(f"No files found with prefix: {source_prefix}")
            
            # Create a new blob for the merged file
            final_filename = f"{destination_filename}.gz" if compress_output else destination_filename
            merged_blob = self.bucket.blob(final_filename)
            
            # Merge files
            is_first = True
            total_size = 0
            
            # Open the destination file with appropriate compression
            with merged_blob.open('wb') as raw_dest:
                # Wrap with gzip if compression is enabled
                dest = gzip.GzipFile(fileobj=raw_dest, mode='wb') if compress_output else raw_dest
                
                try:
                    for blob in sorted(blobs, key=lambda x: x.name):
                        # Download and process each source file
                        content = blob.download_as_bytes()
                        
                        # Handle the content
                        text_content = content.decode('utf-8')
                        lines = text_content.splitlines(keepends=True)
                        
                        # Skip header for all but first file
                        if not is_first:
                            lines = lines[1:]
                        
                        # Write lines to destination
                        for line in lines:
                            line_bytes = line.encode('utf-8')
                            dest.write(line_bytes)
                            total_size += len(line_bytes)
                        
                        is_first = False
                    
                    # Ensure gzip stream is properly closed
                    if compress_output:
                        dest.close()
                
                except Exception as e:
                    # Ensure cleanup in case of error
                    if compress_output:
                        dest.close()
                    raise e
            
            # Optionally delete source files
            if delete_source_files:
                for blob in blobs:
                    blob.delete()
            
            return {
                'status': 'completed',
                'merged_file': final_filename,
                'total_size_bytes': total_size,
                'source_files_deleted': delete_source_files,
                'compressed': compress_output
            }
            
        except Exception as e:
            logger.exception(
                "merge_error",
                source_prefix=source_prefix,
                destination=destination_filename,
                error=str(e)
            )
            raise ExportError(f"Merge failed: {str(e)}")

    def get_signed_url(self, blob_name: str, expiration: int = 3600) -> str:
        """
        Get a GCS URL for downloading a file.
        
        Args:
            blob_name: Name of the blob in the bucket
            expiration: Not used for GCS URLs
        
        Returns:
            GCS URL for downloading the file (requires authentication)
        """
        try:
            return f"https://storage.cloud.google.com/{self.export_bucket}/{blob_name}"
        except Exception as e:
            logger.exception("url_generation_error", blob=blob_name, error=str(e))
            raise ExportError(f"Failed to generate GCS URL: {str(e)}") 