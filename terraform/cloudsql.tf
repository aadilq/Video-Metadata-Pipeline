resource "google_sql_database_instance" "video_metadata_db" {
  name             = "video-metadata-db"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-f1-micro"
  }
}

resource "google_sql_database" "video_metadata" {
    name           = "video_metadata"
    instance       = google_sql_database_instance.video_metadata_db.name
}

resource "google_sql_user" "postgres" {
    name     = "postgres"
    instance = google_sql_database_instance.video_metadata_db.name
    password = var.db_password
}

