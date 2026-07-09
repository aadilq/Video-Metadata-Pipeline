output "cloud_run_url" {
    description = "Cloud Run service URL"
    value       = google_cloud_run_v2_service.video_metadata_service.uri
}

output "bucket_name" {
    description = "GCS bucket name"
    value       = google_storage_bucket.video_uploads.name
}

output "db_connection_name" {
    description = "Cloud SQL connection name"
    value       = google_sql_database_instance.video_metadata_db.connection_name
  }