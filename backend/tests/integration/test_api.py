"""
Integration Tests for API Endpoints

These tests verify that our API endpoints work correctly
by making actual HTTP requests to a test instance of our application.
"""

import pytest
from unittest.mock import patch, Mock

@pytest.mark.asyncio
async def test_list_datasets(client):
    """Test the datasets listing endpoint."""
    # Mock the BigQuery client
    with patch('google.cloud.bigquery.Client') as mock_client:
        # Create mock datasets
        mock_dataset1 = Mock()
        mock_dataset1.dataset_id = "dataset1"
        mock_dataset1.friendly_name = "Test Dataset 1"
        mock_dataset1.location = "US"
        
        mock_dataset2 = Mock()
        mock_dataset2.dataset_id = "dataset2"
        mock_dataset2.friendly_name = "Test Dataset 2"
        mock_dataset2.location = "EU"
        
        # Configure mock to return our test datasets
        mock_client.return_value.list_datasets.return_value = [
            mock_dataset1,
            mock_dataset2
        ]
        
        # Make request to our endpoint
        response = await client.get('/api/v1/datasets')
        
        # Verify response
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['datasets']) == 2
        assert data['datasets'][0]['id'] == "dataset1"
        assert data['datasets'][1]['id'] == "dataset2"

@pytest.mark.asyncio
async def test_list_tables(client):
    """Test the tables listing endpoint."""
    dataset_id = "test_dataset"
    
    # Mock the BigQuery client
    with patch('google.cloud.bigquery.Client') as mock_client:
        # Mock dataset existence check
        mock_dataset = Mock()
        mock_dataset.exists.return_value = True
        mock_client.return_value.dataset.return_value = mock_dataset
        
        # Create mock tables
        mock_table1 = Mock()
        mock_table1.table_id = "table1"
        mock_table1.table_type = "TABLE"
        mock_table1.num_rows = 1000
        mock_table1.num_bytes = 1024
        
        mock_table2 = Mock()
        mock_table2.table_id = "table2"
        mock_table2.table_type = "TABLE"
        mock_table2.num_rows = 2000
        mock_table2.num_bytes = 2048
        
        # Configure mock to return our test tables
        mock_client.return_value.list_tables.return_value = [
            mock_table1,
            mock_table2
        ]
        
        # Make request to our endpoint
        response = await client.get(f'/api/v1/datasets/{dataset_id}/tables')
        
        # Verify response
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['tables']) == 2
        assert data['tables'][0]['id'] == "table1"
        assert data['tables'][1]['id'] == "table2"

@pytest.mark.asyncio
async def test_export_table(client):
    """Test the table export endpoint."""
    # Prepare test request data
    request_data = {
        "dataset_id": "test_dataset",
        "table_id": "test_table",
        "destination_prefix": "exports",
        "compression": True
    }
    
    # Mock both BigQuery and Storage clients
    with patch('google.cloud.bigquery.Client') as mock_bq_client, \
         patch('google.cloud.storage.Client') as mock_storage_client:
        
        # Mock the export job
        mock_job = Mock()
        mock_job.error_result = None
        mock_job.done.return_value = True
        mock_bq_client.return_value.extract_table.return_value = mock_job
        
        # Mock storage operations
        mock_blob = Mock()
        mock_blob.name = "exports/test.csv"
        mock_storage_client.return_value.bucket.return_value.list_blobs.return_value = [mock_blob]
        
        # Make request to our endpoint
        response = await client.post('/api/v1/export', json=request_data)
        
        # Verify response
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == "completed"
        assert len(data['files']) == 1
        assert data['compression'] is True

@pytest.mark.asyncio
async def test_merge_files(client):
    """Test the file merge endpoint."""
    # Prepare test request data
    request_data = {
        "source_prefix": "exports/",
        "destination_filename": "merged.csv",
        "delete_source_files": True,
        "compress_output": True
    }
    
    # Mock the Storage client
    with patch('google.cloud.storage.Client') as mock_client:
        # Mock source files
        mock_blob1 = Mock()
        mock_blob1.name = "exports/file1.csv"
        mock_blob1.download_as_bytes.return_value = "header\ndata1\n".encode('utf-8')
        
        mock_blob2 = Mock()
        mock_blob2.name = "exports/file2.csv"
        mock_blob2.download_as_bytes.return_value = "header\ndata2\n".encode('utf-8')
        
        # Configure mock to return our test blobs
        mock_client.return_value.bucket.return_value.list_blobs.return_value = [
            mock_blob1,
            mock_blob2
        ]
        
        # Mock the merged blob
        mock_merged = Mock()
        mock_client.return_value.bucket.return_value.blob.return_value = mock_merged
        
        # Make request to our endpoint
        response = await client.post('/api/v1/merge', json=request_data)
        
        # Verify response
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == "completed"
        assert data['merged_file'] == "merged.csv.gz"
        assert data['compressed'] is True

@pytest.mark.asyncio
async def test_get_download_url(client):
    """Test the download URL generation endpoint."""
    blob_name = "test.csv"
    
    # Mock the Storage client
    with patch('google.cloud.storage.Client') as mock_client:
        # Mock the blob
        mock_blob = Mock()
        mock_blob.generate_signed_url.return_value = "https://test-url"
        mock_client.return_value.bucket.return_value.blob.return_value = mock_blob
        
        # Make request to our endpoint
        response = await client.get(f'/api/v1/download/{blob_name}')
        
        # Verify response
        assert response.status_code == 200
        data = response.get_json()
        assert data['signed_url'] == "https://test-url"
        assert data['expires_in'] == 3600 