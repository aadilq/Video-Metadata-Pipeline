from fastapi import FastAPI, HTTPException
import base64 ##Decode the base 64 encoding from Pub/Sub push
import json ##converts valid JSON-formatted string into a dictionary
from pydantic import BaseModel ##define the models that we will be recieving
import os

from storage import download_video
from analyzer import analyze_videos
from cloudDb import save_metadata
from webhook import fire_webhook

app = FastAPI()

class PubSubMessage(BaseModel):
    data: str
    messageId : str
    publishTime : str

class PubSubPush(BaseModel):
    message : PubSubMessage
    subscription : str

@app.post('/analyze')
async def analyze(payload: PubSubPush):
    try:
        data = json.loads(base64.b64decode(payload.message.data).decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Pub/Sub message")

    bucket = data["bucket"]
    object_name = data["name"]

    local_path = download_video(bucket, object_name)

    try:
        results = analyze_videos(local_path)
        save_metadata(bucket, object_name, results["duration_seconds"], results["scene_count"])
        fire_webhook(bucket, object_name, results["duration_seconds"], results["scene_count"])
    finally:
        os.remove(local_path)
    return {"status": "recieved", "bucket": bucket, "object_name": object_name}



@app.get('/health')
async def health():
    return {"status": "health"}