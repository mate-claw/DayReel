import os, uuid, time, requests, boto3
from .config import AWS_ACCESS_KEY,AWS_SECRET_KEY,AWS_REGION,S3_BUCKET
class S3Uploader:
    def __init__(self):
        if not S3_BUCKET: raise ValueError("S3_BUCKET missing in .env")
        self.s3=boto3.client("s3",aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key=AWS_SECRET_KEY,region_name=AWS_REGION)
    def public_url(self,key): return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"
    def upload_file(self,path,prefix,content_type=None):
        if not os.path.exists(path): raise FileNotFoundError(path)
        key=f"{prefix.strip('/')}/{uuid.uuid4()}{os.path.splitext(path)[1].lower()}"
        params={"Bucket":S3_BUCKET,"Key":key}
        if content_type: params["ContentType"]=content_type
        signed=self.s3.generate_presigned_url("put_object",Params=params,ExpiresIn=3600)
        headers={}
        if content_type: headers["Content-Type"]=content_type
        last=None
        for attempt in range(1,4):
            try:
                with open(path,"rb") as f: r=requests.put(signed,data=f,headers=headers,timeout=120)
                if r.status_code in (200,201): return self.public_url(key)
                last=RuntimeError(f"S3 upload failed {r.status_code}: {r.text[:200]}")
            except Exception as e: last=e
            print(f"S3 upload retry {attempt}/3:",last); time.sleep(2*attempt)
        raise RuntimeError(f"S3 upload failed: {path}: {last}")
    def upload_videos(self,folder):
        items=[]
        if not os.path.isdir(folder): return items
        for name in sorted(os.listdir(folder)):
            if not name.lower().endswith((".mp4",".mov",".m4v",".webm",".mkv",".avi")): continue
            path=os.path.join(folder,name); print("upload video:",name)
            items.append({"name":name,"path":path,"url":self.upload_file(path,"json_qwen/videos","video/mp4")})
        return items
    def upload_music(self,path):
        if not path or not os.path.exists(path): return None
        print("upload music:",path); return self.upload_file(path,"json_qwen/music","audio/mpeg")
    def upload_image(self,path):
        if not path or not os.path.exists(path): return None
        return self.upload_file(path,"json_qwen/images","image/jpeg")
