resource "google_cloud_run_v2_service" "video_metadata_service" {
  name     = "video-metadata-service"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/video-metadata-repo/video-metadata-app:latest"

      env {
        name  = "DB_NAME"
        value = "video_metadata"
      }

      env {
        name  = "DB_USER"
        value = "postgres" 
      }

      env {
        name  = "DB_PASSWORD"
        value = var.db_password
      }

      env {
        name  = "DB_HOST"
        value = "/cloudsql/${var.project_id}:${var.region}:video-metadata-db"
      }

      env {
        name  = "WEBHOOK_URL"
        value = var.webhook_url
      }
    }
  

  volumes {
    name = "cloudsql" 
    cloud_sql_instance {
        instances = ["${var.project_id}:${var.region}:video-metadata-db"]
    }
  }
}
}