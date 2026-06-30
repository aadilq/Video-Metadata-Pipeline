import os
import psycopg2
from datetime import datetime, timezone

def get_connection():
    return psycopg2.connect(
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
    )

def save_metadata(bucket: str, object_name: str, duration_seconds: float, scene_count: int):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO videos (bucket, object_name, duration_seconds, scene_count, processed_at)
                VALUES (%s, %s, %s, %s, %s)
                """
                (bucket, object_name, duration_seconds, scene_count, datetime.now(timezone.etc))
            )
            connection.commit()
    finally:
        connection.close()
