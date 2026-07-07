import os
import httpx

def fire_webhook(bucket: str, object_name: str, duration_seconds: float, scene_count: int):
    url = os.environ["WEBHOOK_URL"]

    payload = {
        "bucket": bucket, 
        "object_name": object_name,
        "duration_seconds": duration_seconds,
        "scene_count": scene_count
    }

    with httpx.Client() as client:
        response = client.post(url, json=payload)
        response.raise_for_status()

        