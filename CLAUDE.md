# Video Metadata Pipeline

## Project Overview

A cloud-native pipeline that automatically extracts metadata from uploaded videos.
When a user uploads a video to Google Cloud Storage, the upload event triggers a
Pub/Sub message that fans out to a FastAPI service running on Cloud Run. The service
uses FFmpeg to analyze the video (duration, scene count), writes results to Cloud SQL
(Postgres), and fires a webhook to notify downstream consumers that processing is done.

**Stack:** GCS · Pub/Sub · Cloud Run · FastAPI · FFmpeg · Cloud SQL (Postgres)

---

## Data Flow

```
User
 │
 │  1. Upload video
 ▼
GCS Bucket (videos/)
 │
 │  2. GCS emits storage notification → Pub/Sub topic: `metadata_analysis`
 ▼
Pub/Sub Topic: metadata_analysis
 │
 │  3. Fan-out to subscription(s)
 ▼
Pub/Sub Subscription: metadata_analysis_sub
 │
 │  4. Push delivery to Cloud Run endpoint /analyze
 ▼
Cloud Run: FastAPI service
 │
 ├─ 5a. Download video from GCS into ephemeral /tmp
 ├─ 5b. Run FFmpeg → extract duration + scene count
 ├─ 5c. Write results to Cloud SQL (Postgres)  ──► Cloud SQL (videos table)
 └─ 5d. POST webhook → notify downstream consumer
```

---

## Build Roadmap

### Phase 1 — GCP Project Setup
- [ ] 1.1 Create or confirm GCP project and note the project ID
- [ ] 1.2 Enable required APIs: Cloud Storage, Pub/Sub, Cloud Run, Cloud SQL, Artifact Registry
- [ ] 1.3 Install and authenticate `gcloud` CLI locally

### Phase 2 — GCS Bucket
- [ ] 2.1 Create a GCS bucket for video uploads
- [ ] 2.2 Configure a GCS Pub/Sub notification on the bucket (fires on object finalize)

### Phase 3 — Pub/Sub Topic & Subscription
- [ ] 3.1 Create the `metadata_analysis` topic
- [ ] 3.2 Create a push subscription pointed at the Cloud Run `/analyze` endpoint

### Phase 4 — Cloud SQL
- [ ] 4.1 Create a Postgres Cloud SQL instance
- [ ] 4.2 Create a database and `videos` table (id, bucket, object_name, duration_seconds, scene_count, processed_at)
- [ ] 4.3 Note the connection string / Cloud SQL instance connection name

### Phase 5 — FastAPI Service
- [ ] 5.1 Scaffold the FastAPI project structure
- [ ] 5.2 Implement `/analyze` endpoint — parse Pub/Sub push message, extract GCS object info
- [ ] 5.3 Add GCS download logic (stream video to `/tmp`)
- [ ] 5.4 Add FFmpeg analysis logic (duration + scene count)
- [ ] 5.5 Add Cloud SQL write logic (insert results row)
- [ ] 5.6 Add webhook fire logic (POST to configured URL)
- [ ] 5.7 Add `/health` endpoint for Cloud Run health checks
- [ ] 5.8 Write Dockerfile (include FFmpeg)

### Phase 6 — Cloud Run Deployment
- [ ] 6.1 Build and push Docker image to Artifact Registry
- [ ] 6.2 Deploy image to Cloud Run, set env vars (DB connection, webhook URL)
- [ ] 6.3 Copy the deployed Cloud Run URL back into the Pub/Sub push subscription

### Phase 7 — End-to-End Test
- [ ] 7.1 Upload a test video to the GCS bucket
- [ ] 7.2 Confirm Pub/Sub message was received by Cloud Run (check logs)
- [ ] 7.3 Confirm metadata row appears in Cloud SQL
- [ ] 7.4 Confirm webhook fired (check downstream consumer / request bin)

### Phase 8 — Terraform (post-MVP)
- [ ] 8.1 Write Terraform configs for GCS, Pub/Sub, Cloud SQL, Cloud Run, Artifact Registry
- [ ] 8.2 `terraform plan` against existing infrastructure, reconcile drift
- [ ] 8.3 `terraform apply` — hand off resource management to Terraform

---

## Key Decisions
- **Manual setup first, Terraform later** — build understanding before codifying
- **No auth between components** — keeping it simple for initial build
- **Webhook URL is fixed** — configured as an env var on Cloud Run, not per-upload
- **FFmpeg runs inside Cloud Run** — bundled in the Docker image, processes in `/tmp`
