# BigQuery Table Export Utility

<div align="center">

![Google Cloud Platform](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)

*Enterprise-grade solution for BigQuery table exports with seamless Cloud integration*

[Key Features](#key-features) •
[Quick Start](#quick-start-15-minutes) •
[Documentation](#documentation) •
[Architecture](#technical-architecture) •
[Security](#security-and-compliance)

</div>

---

## Overview

The BigQuery Table Export Utility delivers a production-ready solution for a critical enterprise challenge: efficiently and securely exporting large BigQuery tables to CSV format. This solution exemplifies modern cloud architecture while serving as a comprehensive reference implementation.

### Key Features

<table>
<tr>
<td width="50%">

#### 🚀 Production Features
- Large-scale BigQuery table exports
- Intelligent file splitting and merging
- Real-time progress tracking
- Comprehensive error handling
- Production-grade CLI interface

</td>
<td>

#### 📚 Implementation Showcase
- Cloud-native architecture patterns
- GCP service integration
- Security best practices
- Infrastructure as Code
- Observability patterns

</td>
</tr>
</table>

### Technology Stack

<table>
<tr>
<td width="33%">

#### Core Services
- Google Cloud Run
- BigQuery
- Cloud Storage
- Cloud IAM

</td>
<td width="33%">

#### Development
- Python 3.9+
- Terraform
- Docker
- Git

</td>
<td>

#### Security
- Native GCP Auth
- IAM Role Management
- Audit Logging
- Encryption in Transit

</td>
</tr>
</table>

## Quick Start (15 minutes)

### Prerequisites

\`\`\`bash
# Install Google Cloud SDK
brew install google-cloud-sdk  # macOS
# See https://cloud.google.com/sdk/docs/install for other platforms

# Install Python 3.9+
brew install python@3.9  # macOS
\`\`\`

### Authentication

\`\`\`bash
# Configure Google Cloud credentials
gcloud auth login
gcloud auth application-default login
\`\`\`

### Installation

\`\`\`bash
# Clone and setup
git clone https://github.com/EddieAtGoogle/BigQuery-Table-Export-Utility.git
cd BigQuery-Table-Export-Utility

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\\Scripts\\activate   # Windows

# Install package
pip install -e .
\`\`\`

### Development Environment

\`\`\`bash
# Configure local proxy
PROJECT_ID=$(gcloud config get-value project)
gcloud run services proxy bq-export-app \\
    --region=us-central1 \\
    --project=$PROJECT_ID \\
    --port=8080

# In a new terminal:
export BQ_EXPORT_API_URL="http://localhost:8080"
bq-export interactive
\`\`\`

## Technical Architecture

### Component Overview

\`\`\`mermaid
graph TD
    A[Client Layer] -->|Authentication| B[Cloud Run Service]
    B -->|Export Request| C[BigQuery API]
    C -->|Export Job| D[Cloud Storage]
    B -->|Monitor Job| C
    B -->|Generate URL| D
    E[IAM & Auth] -->|Authenticate| B
    E -->|Authorize| C
    E -->|Authorize| D
\`\`\`

### Security and Compliance

<table>
<tr>
<td width="33%">

#### Authentication
- Native GCP authentication
- Token-based access
- Role-based authorization

</td>
<td width="33%">

#### Data Protection
- In-transit encryption
- At-rest encryption
- Secure file transfers

</td>
<td>

#### Monitoring
- Audit logging
- Access tracking
- Security alerts

</td>
</tr>
</table>

## Configuration Reference

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `BQ_EXPORT_API_URL` | Cloud Run service URL | Yes | None |
| `GOOGLE_CLOUD_PROJECT` | GCP Project ID | No | From gcloud |
| `LOG_LEVEL` | Logging verbosity | No | INFO |

### Runtime Options

| Option | Description | Default |
|--------|-------------|---------|
| `compression` | Enable file compression | `False` |
| `delete_source_files` | Delete temporary files | `True` |
| `max_concurrent_exports` | Maximum concurrent exports | `5` |

## Best Practices

### Performance Optimization

- Utilize Cloud Run proxy for development
- Enable compression for large tables
- Monitor resource utilization
- Implement parallel processing

### Cost Management

- Clean up temporary files
- Use appropriate service tiers
- Monitor usage metrics
- Implement lifecycle policies

### Error Handling

- Monitor BigQuery job logs
- Track Cloud Run metrics
- Implement structured logging
- Enable error alerting

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

*Built with precision and expertise for enterprise-grade deployments*

</div> 