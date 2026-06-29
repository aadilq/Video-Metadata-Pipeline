import os
from google.cloud import storage ## GCS client library

def download_video(bucket_name: str, object_name: str) -> str:
    client = storage.Client() ## creates an authenticated GCS client using the environment's credentials
    bucket = client.bucket(bucket_name) ## gets a reference to our GCS bucket
    blob = bucket.blob(object_name) ## gets a reference to the specific file inside the bucket

    filename = os.path.basename(object_name) ## strips folder prefix e.g.
  ## "uploads/vacation.mp4" → "vacation.mp4"
    local_path = f"/tmp/{filename}" ## builds the local path where the file will be saved inside of the container

    blob.download_to_filename(local_path) ## downloads the filepath from GCS to the file path

    return local_path ## returns the path where the video is held so FFmpeg knows where to find it
