import boto3
from .config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, S3_BUCKET

class S3Client:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        )

    def list_videos(self, prefix="raw/"):
        res = self.s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)

        if "Contents" not in res:
            return []

        return [
            f"s3://{S3_BUCKET}/{obj['Key']}"
            for obj in res["Contents"]
            if obj["Key"].endswith(".mp4")
        ]
