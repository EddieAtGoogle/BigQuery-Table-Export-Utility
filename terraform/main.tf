# Configure Terraform to use the Google Cloud provider
# This block specifies which providers are required for this configuration
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"  # Official Google Cloud provider
      version = "~> 4.84.0"         # Pin to 4.84.x version for stability
    }
  }
}

# Configure the Google Cloud provider with project and region
# These values are supplied through variables defined in terraform.tfvars
provider "google" {
  project = var.project_id  # Your Google Cloud Project ID
  region  = var.region     # Your preferred Google Cloud region
}

# Enable necessary Google Cloud APIs for the project
# This ensures all required services are available before creating resources
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",                    # Required for Cloud Run
    "bigquery.googleapis.com",               # Required for BigQuery operations
    "storage.googleapis.com",                # Required for Cloud Storage
    "cloudresourcemanager.googleapis.com",   # Required for IAM and project management
    "iam.googleapis.com"                     # Required for service accounts and permissions
  ])
  
  service = each.key
  disable_dependent_services = true          # Disable dependent services when this API is disabled
}

# Create a Cloud Storage bucket for storing exported CSV files
# This bucket will maintain versions of files to prevent accidental deletion
resource "google_storage_bucket" "export_storage" {
  name          = "${var.project_id}-bq-exports"     # Bucket name must be globally unique
  location      = var.region                         # Same region as other resources for better performance
  force_destroy = false                              # Protect against accidental deletion

  # Enable uniform bucket-level access for better security
  uniform_bucket_level_access = true

  # Enable versioning to maintain file history and prevent accidental deletions
  versioning {
    enabled = true
  }

  # Optional: Configure public access prevention
  public_access_prevention = "enforced"
}

# Create a service account for the application
# This provides a dedicated identity for the Cloud Run service
resource "google_service_account" "app_service_account" {
  account_id   = "bq-export-app"
  display_name = "BigQuery Export Application Service Account"
  description  = "Service account for the BigQuery Export application running on Cloud Run"
}

# Grant BigQuery data viewer permissions to the service account
# This allows the application to read from BigQuery tables
resource "google_project_iam_member" "bigquery_viewer_permissions" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.app_service_account.email}"
}

# Grant BigQuery job user permissions to the service account
# This allows the application to create and manage export jobs
resource "google_project_iam_member" "bigquery_job_permissions" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.app_service_account.email}"
}

# Grant Storage Object Admin permissions to the service account
# This allows the application to read/write files in Cloud Storage
resource "google_project_iam_member" "storage_permissions" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"  # Updated to allow full file management
  member  = "serviceAccount:${google_service_account.app_service_account.email}"
}

# Deploy the application to Cloud Run
# This creates a serverless container environment for the application
resource "google_cloud_run_service" "app" {
  name     = "bq-export-app"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.app_service_account.email
      
      containers {
        image = var.container_image
        
        # Configure resource limits for the container
        resources {
          limits = {
            cpu    = "1000m"  # 1 vCPU
            memory = "2Gi"    # 2 GB RAM
          }
        }

        # Pass environment variables to the container
        env {
          name  = "EXPORT_BUCKET"
          value = google_storage_bucket.export_storage.name
        }

        # Add additional environment variables if needed
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
      }
    }
  }

  # Configure traffic to always use the latest revision
  traffic {
    percent         = 100
    latest_revision = true
  }

  # Ensure APIs are enabled before deploying
  depends_on = [
    google_project_service.required_apis
  ]
}

# Configure public access to the Cloud Run service
# This allows users to access the web application
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_service.app.location
  service  = google_cloud_run_service.app.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Output the service URL for easy access
output "service_url" {
  description = "The URL of the deployed Cloud Run service"
  value       = google_cloud_run_service.app.status[0].url
}

# Output the export bucket name for reference
output "export_bucket" {
  description = "The name of the Cloud Storage bucket for CSV exports"
  value       = google_storage_bucket.export_storage.name
} 