"""
Unit tests for the BigQuery Export Service.

For more information about testing with pytest, see:
https://docs.pytest.org/en/stable/
"""

import pytest
import gzip
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from io import BytesIO

from app.services.export_service import BigQueryExportService
from app.utils.error_handlers import ExportError, ValidationError

@pytest.fixture
def export_service():
    """Create a test instance of the export service."""
    return BigQueryExportService(
        project_id="test-project",
        export_bucket="test-bucket"
    )

@pytest.fixture
def mock_blob():
    """Create a mock blob with common attributes."""
    blob = Mock()
    blob.name = "test/file.csv"
    return blob

@pytest.mark.asyncio
async def test_export_table_success(export_service):
    """Test successful table export."""
    # Mock BigQuery and Storage clients
    export_service.bq_client = Mock()
    export_service.storage_client = Mock()
    export_service.bucket = Mock()
    
    # Mock the extract job
    mock_job = Mock()
    mock_job.error_result = None
    mock_job.done.return_value = True
    
    export_service.bq_client.extract_table.return_value = mock_job
    
    # Mock storage listing
    mock_blob1 = Mock()
    mock_blob1.name = "exports/file1.csv"
    mock_blob2 = Mock()
    mock_blob2.name = "exports/file2.csv"
    
    export_service.bucket.list_blobs.return_value = [mock_blob1, mock_blob2]
    
    # Test the export
    result = await export_service.export_table(
        dataset_id="test_dataset",
        table_id="test_table"
    )
    
    # Verify the result
    assert result["status"] == "completed"
    assert len(result["files"]) == 2
    assert result["compression"] is True

@pytest.mark.asyncio
async def test_merge_csv_files_with_compression(export_service, mock_blob):
    """Test merging CSV files with compression enabled."""
    # Mock storage and blobs
    export_service.bucket = Mock()
    mock_blob.download_as_bytes.return_value = "header\ndata1\n".encode('utf-8')
    export_service.bucket.list_blobs.return_value = [mock_blob]
    
    # Mock the merged blob
    mock_merged = MagicMock()
    export_service.bucket.blob.return_value = mock_merged
    
    # Create a BytesIO to capture the compressed output
    output_buffer = BytesIO()
    mock_merged.open.return_value.__enter__.return_value = output_buffer
    
    # Test merging with compression
    result = await export_service.merge_csv_files(
        source_prefix="test/",
        destination_filename="merged.csv",
        compress_output=True
    )
    
    # Verify the result
    assert result["status"] == "completed"
    assert result["merged_file"] == "merged.csv.gz"
    assert result["compressed"] is True
    assert result["source_files_deleted"] is True

@pytest.mark.asyncio
async def test_merge_csv_files_without_compression(export_service, mock_blob):
    """Test merging CSV files without compression."""
    # Mock storage and blobs
    export_service.bucket = Mock()
    mock_blob.download_as_bytes.return_value = "header\ndata1\n".encode('utf-8')
    export_service.bucket.list_blobs.return_value = [mock_blob]
    
    # Mock the merged blob
    mock_merged = MagicMock()
    export_service.bucket.blob.return_value = mock_merged
    
    # Create a BytesIO to capture the uncompressed output
    output_buffer = BytesIO()
    mock_merged.open.return_value.__enter__.return_value = output_buffer
    
    # Test merging without compression
    result = await export_service.merge_csv_files(
        source_prefix="test/",
        destination_filename="merged.csv",
        compress_output=False
    )
    
    # Verify the result
    assert result["status"] == "completed"
    assert result["merged_file"] == "merged.csv"
    assert result["compressed"] is False
    assert result["source_files_deleted"] is True

@pytest.mark.asyncio
async def test_merge_csv_files_multiple_files(export_service):
    """Test merging multiple CSV files with header handling."""
    # Mock storage
    export_service.bucket = Mock()
    
    # Create multiple mock blobs with different content
    mock_blob1 = Mock()
    mock_blob1.name = "test/file1.csv"
    mock_blob1.download_as_bytes.return_value = "header\ndata1\n".encode('utf-8')
    
    mock_blob2 = Mock()
    mock_blob2.name = "test/file2.csv"
    mock_blob2.download_as_bytes.return_value = "header\ndata2\n".encode('utf-8')
    
    export_service.bucket.list_blobs.return_value = [mock_blob1, mock_blob2]
    
    # Mock the merged blob
    mock_merged = MagicMock()
    export_service.bucket.blob.return_value = mock_merged
    
    # Create a BytesIO to capture the output
    output_buffer = BytesIO()
    mock_merged.open.return_value.__enter__.return_value = output_buffer
    
    # Test the merge
    result = await export_service.merge_csv_files(
        source_prefix="test/",
        destination_filename="merged.csv"
    )
    
    # Verify the result
    assert result["status"] == "completed"
    assert result["merged_file"] == "merged.csv.gz"  # Default compression
    assert result["compressed"] is True
    assert result["source_files_deleted"] is True

@pytest.mark.asyncio
async def test_merge_csv_files_no_files_found(export_service):
    """Test merging when no files are found."""
    # Mock empty blob list
    export_service.bucket = Mock()
    export_service.bucket.list_blobs.return_value = []
    
    # Test the merge
    with pytest.raises(ValidationError) as exc_info:
        await export_service.merge_csv_files(
            source_prefix="test/",
            destination_filename="merged.csv"
        )
    
    assert "No files found with prefix" in str(exc_info.value)

def test_get_signed_url(export_service):
    """Test signed URL generation."""
    # Mock storage
    export_service.bucket = Mock()
    mock_blob = Mock()
    mock_blob.generate_signed_url.return_value = "https://test-url"
    export_service.bucket.blob.return_value = mock_blob
    
    # Test URL generation
    url = export_service.get_signed_url("test.csv")
    
    # Verify the result
    assert url == "https://test-url"
    mock_blob.generate_signed_url.assert_called_once() 