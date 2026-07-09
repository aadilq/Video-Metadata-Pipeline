resource "google_pubsub_topic" "metadata_analysis" {
    name = "metadata_analysis"
}

resource "google_pubsub_subscription" "metadata_analysis_sub" {
    name  = "metadata_analysis_sub"
    topic = google_pubsub_topic.metadata_analysis.id


    push_config {
        push_endpoint = "${google_cloud_run_v2_service.video_metadata_service.uri}/analyze"
    }
}

