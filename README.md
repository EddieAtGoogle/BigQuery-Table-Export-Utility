# BigQuery Table Export Utility

## Overview

The BigQuery Table Export Utility is a functional solution that solves a enterprise challenge: exporting large BigQuery tables to CSV format efficiently and securely. This project serves a dual purpose:

1. **Functional Use**: A fully functional application that:
   - Handles large-scale BigQuery table exports
   - Provides a powerful CLI interface
   - Implements recommended security practices
   - Manages file splitting and merging
   - Offers progress tracking and error handling

2. **Educational Resource**: A comprehensive learning tool for Google Cloud Platform, demonstrating:
   - Modern cloud-native architecture patterns
   - GCP service integration best practices
   - Security implementation in cloud applications
   - Infrastructure as Code with Terraform

The project showcases real-world implementation of several key Google Cloud services and concepts:
- Cloud Run for serverless deployment
- BigQuery data operations
- Cloud Storage for file management
- Cloud IAM for security
- Terraform for infrastructure

For teams and individuals looking to learn GCP, this project provides:
- Detailed documentation with explanations
- Best practice implementations
- Real-world usage patterns
- Security considerations
- Performance optimization techniques

## What You'll Learn

This project demonstrates enterprise-grade integration between Google Cloud services, specifically:
- Serverless application deployment with Cloud Run
- BigQuery data export operations
- Cloud Storage file management
- Google Cloud authentication and security
- Infrastructure as Code with Terraform

## Quick Start (15 minutes)

The fastest way to get started is using the Cloud Run proxy for local development:

1. Install prerequisites:
   ```bash
   # Install Google Cloud SDK
   brew install google-cloud-sdk  # macOS
   # See https://cloud.google.com/sdk/docs/install for other platforms
   
   # Install Python 3.9+
   brew install python@3.9  # macOS
   ```

2. Authenticate with Google Cloud:
   ```bash
   # Login to Google Cloud
   gcloud auth login
   gcloud auth application-default login
   ```

3. Clone and install the utility:
   ```bash
   # Clone repository
   git clone https://github.com/your-org/bq-table-to-csv.git
   cd bq-table-to-csv
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\\Scripts\\activate   # Windows
   
   # Install package
   pip install -e .
   ```

4. Start the Cloud Run proxy:
   ```bash
   # Get your project ID
   PROJECT_ID=$(gcloud config get-value project)
   
   # Start proxy
   gcloud run services proxy bq-export-app \
       --region=us-central1 \
       --project=$PROJECT_ID \
       --port=8080
   ```

5. Export your first table:
   ```bash
   # Set API URL to local proxy
   export BQ_EXPORT_API_URL="http://localhost:8080"
   
   # Start interactive export session
   bq-export interactive
   ```

## Step-by-Step Tutorials

### Development Environment Setup

#### Local Development with Cloud Run Proxy

The Cloud Run proxy provides the easiest way to develop and test locally:

1. Configure Google Cloud project:
   ```bash
   # Set default project
   gcloud config set project YOUR_PROJECT_ID
   
   # Enable required APIs
   gcloud services enable run.googleapis.com \\
       bigquery.googleapis.com \\
       storage.googleapis.com \\
       artifactregistry.googleapis.com \\
       cloudresourcemanager.googleapis.com \\
       iam.googleapis.com
   ```

2. Grant necessary permissions:
   ```bash
   # Get your user account
   USER_EMAIL=$(gcloud config get-value account)
   
   # Grant Cloud Run invoker role
   gcloud run services add-iam-policy-binding bq-export-app \\
       --member="user:$USER_EMAIL" \\
       --role="roles/run.invoker" \\
       --region=us-central1
   ```

3. Start local development:
   ```bash
   # Start Cloud Run proxy
   gcloud run services proxy bq-export-app \\
       --region=us-central1 \\
       --port=8080
   
   # In another terminal:
   export BQ_EXPORT_API_URL="http://localhost:8080"
   bq-export interactive
   ```

### Cloud Deployment

#### Infrastructure Setup

1. Configure Terraform:
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   
   # Edit terraform.tfvars with your values:
   # project_id = "your-project-id"
   # region = "us-central1"
   ```

2. Create Artifact Registry repository:
   ```bash
   gcloud artifacts repositories create bq-export-app \\
       --repository-format=docker \\
       --location=us-central1 \\
       --description="Repository for BigQuery Export Application"
   ```

3. Deploy infrastructure:
   ```bash
   # Initialize Terraform
   terraform init
   
   # Review changes
   terraform plan
   
   # Apply changes
   terraform apply
   ```

4. Build and deploy application:
   ```bash
   cd ../backend
   
   # Build container
   docker build --platform linux/amd64 \\
       -t us-central1-docker.pkg.dev/$PROJECT_ID/bq-export-app/backend:latest .
   
   # Push to Artifact Registry
   docker push us-central1-docker.pkg.dev/$PROJECT_ID/bq-export-app/backend:latest
   ```

## Technical Deep Dives

### Authentication & Security

The application uses Google Cloud's native authentication:

1. **Development Authentication**:
   - Uses Cloud Run proxy for automatic authentication
   - Leverages gcloud credentials
   - No manual token management needed

2. **Production Authentication**:
   - IAM-based access control
   - Role-based permissions
   - Token validation and verification

3. **Security Best Practices**:
   - No stored credentials
   - Least privilege principle
   - Encrypted data transfer
   - Audit logging

### BigQuery Integration

The export process follows these steps:

1. **Export Initialization**:
   ```mermaid
   sequenceDiagram
       participant User
       participant CLI
       participant Backend
       participant BigQuery
       participant Storage
       
       User->>CLI: Select table
       CLI->>Backend: Request export
       Backend->>BigQuery: Create export job
       BigQuery->>Storage: Export data
       Storage->>Backend: Export complete
       Backend->>CLI: Return status
       CLI->>User: Show progress
   ```

2. **File Management**:
   - Automatic file splitting for large tables
   - Compression options
   - Cleanup of temporary files

3. **Performance Optimization**:
   - Parallel processing
   - Streaming downloads
   - Resource management

### Cloud Run Architecture

The serverless architecture provides several benefits:

1. **Scalability**:
   - Automatic scaling based on load
   - Resource optimization
   - Cost efficiency

2. **Deployment**:
   - Container-based deployment
   - Infrastructure as Code
   - Zero-downtime updates

3. **Monitoring**:
   - Built-in metrics
   - Structured logging
   - Error tracking

## Reference Guide

### CLI Commands

```bash
# Start interactive session
bq-export interactive

# View help
bq-export --help
```

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| BQ_EXPORT_API_URL | Cloud Run service URL | Yes | None |
| GOOGLE_CLOUD_PROJECT | GCP Project ID | No | From gcloud |
| LOG_LEVEL | Logging verbosity | No | INFO |

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| compression | Enable file compression | False |
| delete_source_files | Delete temporary files | True |
| max_concurrent_exports | Maximum concurrent exports | 5 |

## Best Practices

### Performance
- Use the Cloud Run proxy for development
- Enable compression for large tables
- Monitor resource usage

### Cost Management
- Clean up temporary files
- Use appropriate service tiers
- Monitor usage metrics

### Error Handling
- Check BigQuery job logs
- Monitor Cloud Run logs
- Use structured logging

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   ```bash
   # Refresh credentials
   gcloud auth login
   gcloud auth application-default login
   ```

2. **Permission Errors**:
   - Verify IAM roles
   - Check project permissions
   - Review audit logs

3. **Export Failures**:
   - Check BigQuery job logs
   - Verify storage permissions
   - Monitor Cloud Run logs

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Important Notice

This software is provided under the MIT License "AS IS", without warranty of any kind. The authors and contributors are not responsible for any damages or liability arising from the use of this software. See the [LICENSE](LICENSE) file for details. 