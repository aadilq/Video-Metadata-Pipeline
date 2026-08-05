
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

## Phase 5


### 5.1
Phase 5 begins with us creating the FastAPI project structure. We start off with writing out the `analyze` endpoint which takes in the Pub/Sub payload, and extracting the GCS object info. 

### 5.2
We start off with defining two pydantic model classes. These two classes define the exact shape FastAPI should expect the incoming push request (see Phase 3). This allows FastAPI to validate the incoming JSON and rejecting it a 422 automatically if its malformed. 

Within the Pub/Sub message, `data` is the only field carrying the real event payload — everything else in the envelope is Pub/Sub's own metadata about the delivery, so it's the only thing that needs unwrapping. We unwrap it into raw JSON data then parse it into a Python dict, from there getting the bucket and file name. 

### 5.3
we take the bucket and file name, pass it into the download_video function. The function gets into contact with the GCS and gets references to both the GCS bucket and the specific file inside the bucket. We strip the folder prefix of the file (e.g "uploads/vacation.mp4" → "vacation.mp4"), build the local path where the file will be saved inside of the container, download the video, and return the local path.

### 5.4
once the video is downloaded to the tmp folder on our cloud run container, we run it through the FFmpeg analysis. Every time analyze_videos() runs,
it spawns ffprobe and ffmpeg as short-lived child processes — each one starts, does its one job (read duration / detect scenes), exits, and hands its output back — while the parent Python process keeps running the whole service.

`result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", local_path],
        capture_output=True, text=True, check=True
    )`

In order for FFmpeg to work at all, we install the real compiled binary via the OS package manager in our docker file which is why later on, we specify: 

`apt-get install -y ffmpeg`

### 5.5
Next up, we write out the FFmpeg analysis results to the Cloud SQL. cloudDb.py takes care of two things: opening a connection to Postgres, and using that connection to insert one rows into the `video_metadata` database. 

For opening a connection to our postgres database, we set up a function `get_connection` that uses the psycopg2 library to allow our python code talk to our PostgreSQL database. we use `psycopg2.connect` to open a live session to the database using four env vars and return a connection object representing that open session. 

The `save_metadata` function is where we combine the function above with a sql statement to insert the data (bucket, object_name, duration_seconds, scene_count) in the videos table. 

`save_metadata(bucket, object_name, results["duration_seconds"], results["scene_count"])` 
is called after analyze_videos() - so the row is written to postgres before anything is pushed downstream. 

### 5.6
Now that our data has been written to the Postgres, we can add a webhook fire logic to send the results to whoever needs them. in webhook.py, we set up a function `fire_webhook` that reads the webhook URL from an environment variable. we set up a variable `payload` with all of the data in json format. we send one HTTP POST request to the webhook URL, with payload automatically serialized as the JSON body, and the server's reply is stored in  response.

### 5.8
last but not least, we write up a dockerfile that packages all of our requirements and code into an image which we can deploy and use on cloud run. we specify the base image to be `python:3.11-slim` upon which we build upon. we run `apt-get update` which downloads the newest list of available apps and updates but does not actually install any software. next we run `apt-get install -y ffmpeg` which automatically downloads and installs ffmpeg. the rest of the dockerfile is pretty standard code of just setting up our working directory, copying everything over from requirements.txt and our code and setting up the command that will run once the container boots up. 



