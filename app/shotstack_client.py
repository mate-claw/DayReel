import requests
import time
from .config import SHOTSTACK_KEY   # ✅ 必须有

class ShotstackClient:
    BASE = "https://api.shotstack.io/v1"

    def create_render(self, payload):
        res = requests.post(
            f"{self.BASE}/render",
            json=payload,
            headers={
                "x-api-key": SHOTSTACK_KEY,   # ✅ 现在有定义了
                "Content-Type": "application/json"
            },
            timeout=30
        )

        data = res.json()
        print("🔥 Shotstack response:", data)

        if "response" not in data:
            raise Exception(data)

        return data["response"]["id"]

    def wait_render(self, render_id):
        url = f"{self.BASE}/render/{render_id}"

        headers = {"x-api-key": SHOTSTACK_KEY}

        while True:
            try:
                res = requests.get(url, headers=headers, timeout=30)
                data = res.json()

                status = data["response"]["status"]
                print("Status:", status)

                if status == "done":
                    return data["response"]["url"]

                if status == "failed":
                    raise Exception(data)

            except Exception as e:
                print("⚠️ retrying...", e)

            time.sleep(5)