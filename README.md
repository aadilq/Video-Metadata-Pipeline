
# Video-Metadata-Pipeline

An event-driven pipeline on Google Cloud Platform - uploading a video to Cloud Storage triggers a Pub/Sub message to FastAPI service on Cloud Run which runs FFmpeg to extract duration and scene count, persists the results to Cloud SQL and fires a webhook to notify downstream consumers. 



## Phase 1
Phase 1 of building out the pipeline started with creating the project within Google Cloud Platform (GCP). Once we created the project in GCP, we enabled the specific APIs which served a specific purpose in the project. Each API had to be explicity enabled. The APIs that we enabled were:

    - Cloud Storage
    - Pub/Sub
    - Cloud Run
    - Cloud SQL
    - Artifact Registry

After enabling each API, we had to install gcloud CLI locally so running `brew update && brew install --cask gcloud-cli`. After installing the CLI, we had to run two authentication commands.

    1. gcloud auth login - logs us in as a human so that the gcloud 
    cli runs commands on our behalf from the terminal without us
    going into GCP. 

    2. gcloud auth application-default login - writes a credential
    file and stores it on our laptop 

Most of the GCP resources that we use (Cloud Run, Cloud SQL, GCS buckets) are regional, meaning that in the project they are being pinned to one location: `us-central1`. This keeps physically close together for lower-latency but at the cost of failover if the region goes down. 

Last thing to note is that when the project was created, GCP automatically created a compute service account for us which acts as the identity for our application and by default, it's the identity that the cloud run services run by but we had to grant it permissions to connect with Cloud SQL.