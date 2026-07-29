
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

## Phase 2

Within GCP, the first resource that we set up was the storage bucket because the first action in our pipeline consists of uploading a video to a Cloud Storage bucket. However, a notification is sent only to the pub/sub when the object (video) has finished being written and is fully durable in the bucket. This gurantees that the pipeline never starts processing a video that's still mid-upload. Last but not least, we specify the payload format to be `JSON_API_V1` which produces the JSON shape that is shown in the Claude.md data flow example. 

## Phase 3

Phase 3 starts with us creating the `metadata_analysis` Pub/Sub topic as it recieves the JSON message from the Google Cloud Storage bucket. However, the Pub/Sub topic itself does nothing else - it doesn't know or care who's listening, it doesn't push anywhere or encode anything. 

This is where `metadata_analysis_sub` comes in. the `metadata_analysis_sub` is a separate resource attached to the `metadata_analysis` Pub/Sub topic that will listen to the topic and actually deliver the message somewhere. 

In our case, the delivery is configured as a push subscription, meaning Pub/Sub itself will make an outbound HTTP post to a specified url - here, <cloud-run-url>/analyze. 

So the accurate chain is: GCS → publishes JSON into the topic → the subscription(which is watching that topic) picks it up and pushes it as an HTTP POST to your Cloud Run /analyze endpoint.

## Phase 4

In Phase 4, we focus on setting up the Cloud SQL component of the pipeline. There is a three-layer hierarchy made up of three distinct resources and levels. 

1. The instance (video-metadata-db) - this is the actual postgres server, version 15, sized at db-f1-micro (smallest low-cost database tier, meant for light dev workloads). 

2. The database (video_metadata) - a logical database inside that server. One instance can host multiple database. We have one. 

3. The user (postgres) - the SQL role that our app authenticates as.. 

Note mentioning - the one piece of information that is not listed is the actual table itself and that is because we chose not to manage the schema in Terraform. the `videos` table was created manually, outside of Iac. 

the last bit is that our app never talks to Postgres directly; it hands the request to the proxy through a local connection (a unix socket), the proxy handles encryption and authentication with the actual database.