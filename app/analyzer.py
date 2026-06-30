import subprocess ## a Python standard library module that lets your Python code run external command-line programs — the same way you'd type a command in your terminal
import json

def analyze_videos(local_path: str) -> dict:
    duration = get_duration(local_path)
    scene_count = get_scene_count(local_path)
    return {"duration": duration, "scene_count": scene_count}


def get_duration(local_path: str) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", local_path],
        capture_output=True, text=True, check=True
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])

def get_scene_count(local_path: str) -> int:
    result = subprocess.run(
        ["ffmpeg", "-i", local_path, "-vf", "select=gt(scene\\,0.4),metadata=print:file=-", "-f", "null", "-"],
        capture_output=True, text=True
    )
    return result.stdout.count("scene_score")
