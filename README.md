# Video-Metadata-Pipeline

A cloud-native pipeline that automatically extracts metadata from uploaded videos.
When a user uploads a video to Google Cloud Storage, the upload event triggers a
Pub/Sub message that fans out to a FastAPI service running on Cloud Run. The service
uses FFmpeg to analyze the video (duration, scene count), writes results to Cloud SQL
(Postgres), and fires a webhook to notify downstream consumers that processing is done.