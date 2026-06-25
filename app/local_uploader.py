import os
import boto3
import uuid
from .config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, S3_BUCKET

class LocalUploader:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        )

    def upload_folder(self, folder_path="videos/"):
        uploaded = []

        for file in os.listdir(folder_path):
            if not file.endswith(".mp4"):
                continue

            local_path = os.path.join(folder_path, file)
            key = f"raw/{uuid.uuid4()}.mp4"

            print(f"Uploading {file} -> {key}")

            self.s3.upload_file(local_path, S3_BUCKET, key)

            # ✅ 关键修复：改成 https URL
            url = f"https://{S3_BUCKET}.s3.amazonaws.com/{key}"
            uploaded.append(url)

        return uploaded