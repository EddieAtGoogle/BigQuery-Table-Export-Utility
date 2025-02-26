variable "project_id" {
  description = "The Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "The Google Cloud region to deploy resources to"
  type        = string
  default     = "us-central1"
}

variable "container_image" {
  description = "The container image to deploy to Cloud Run"
  type        = string
} 