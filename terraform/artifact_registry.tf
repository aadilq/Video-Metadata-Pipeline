resource "google_artifact_registry_repository" "video_metadata_repo" {
  location      = var.region
  repository_id = "video_metadata_repo""
  format        = "DOCKER"
}