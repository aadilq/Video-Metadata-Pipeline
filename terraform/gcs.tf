resource "google_storage_bucket" "video_uploads" {
    name     = "video-metadata-uploads-myproject123"
    location = var.region
}

resource "google_storage_notification" "video_upload_notification" {
    bucket         = google_storage_bucket.video_uploads.name
    payload_format = "JSON_API_V1"
    topic          = google_pubsub_topic.metadata_analysis.id
    event_types    = ["OBJECT_FINALIZE"]
}

