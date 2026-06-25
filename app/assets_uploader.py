import os
import boto3
import uuid
from .config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, S3_BUCKET

class AssetUploader:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        )

    def upload_videos(self, folder="videos/"):
        urls = []

        if not os.path.exists(folder):
            return urls

        for f in os.listdir(folder):
            if not f.endswith(".mp4"):
                continue

            path = os.path.join(folder, f)
            key = f"raw/{uuid.uuid4()}.mp4"

            print(f"Uploading video {f} -> {key}")
            self.s3.upload_file(path, S3_BUCKET, key)

            urls.append(f"https://{S3_BUCKET}.s3.amazonaws.com/{key}")

        return urls

    def upload_music(self, file_path="music/bgm.mp3"):
        if not os.path.exists(file_path):
            print("No bgm found, skip music")
            return None

        key = f"music/{uuid.uuid4()}.mp3"

        print(f"Uploading music -> {key}")
        self.s3.upload_file(file_path, S3_BUCKET, key)

        return f"https://{S3_BUCKET}.s3.amazonaws.com/{key}"