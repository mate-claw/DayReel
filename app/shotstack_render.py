import time, requests
from .config import SHOTSTACK_KEY,SHOTSTACK_BASE_URL
class ShotstackRenderer:
    def __init__(self):
        if not SHOTSTACK_KEY: raise ValueError("SHOTSTACK_KEY missing in .env")
        self.headers={"Content-Type":"application/json","Accept":"application/json","x-api-key":SHOTSTACK_KEY}
    def render(self,payload):
        last=None
        for attempt in range(1,4):
            try:
                r=requests.post(SHOTSTACK_BASE_URL.rstrip()+"/render",headers=self.headers,json=payload,timeout=60); data=r.json(); print("render response:",data)
                if isinstance(data.get("response"),dict) and data["response"].get("id"): return data["response"]["id"]
                last=data
            except Exception as e: last=e
            print(f"render retry {attempt}/3:",last); time.sleep(2*attempt)
        raise RuntimeError(f"Shotstack render failed: {last}")
    def wait(self,render_id):
        url=SHOTSTACK_BASE_URL.rstrip()+"/render/"+render_id
        while True:
            try:
                r=requests.get(url,headers=self.headers,timeout=45); data=r.json()
                if not isinstance(data.get("response"),dict): print("wait response:",data); time.sleep(5); continue
                status=data["response"].get("status"); print("status:",status)
                if status=="done": return data["response"].get("url")
                if status=="failed": raise RuntimeError(data)
            except Exception as e: print("wait retry:",e)
            time.sleep(5)
