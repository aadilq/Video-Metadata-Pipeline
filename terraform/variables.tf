variable "project_id" {
    description = "GCP project ID"
    default = "video-metadata-pipeline"
}

variable "region" {
    description = "GCP region"
    default = "us-central1"
}

variable "db_password" {
    description = "Cloud SQL postgres password"
    sensitive   = true
}

variable "webhook_url" {
    description = "Webhook URL for downstream notifications"
    sensitive   = true
}

