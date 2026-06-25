import time
import requests
from .config import SHOTSTACK_KEY, SHOTSTACK_BASE_URL

class Shotstack:
    def render(self, payload):
        if not SHOTSTACK_KEY:
            raise ValueError("SHOTSTACK_KEY missing in .env")

        last_error = None
        for attempt in range(1, 4):
            try:
                response = requests.post(
                    SHOTSTACK_BASE_URL.rstrip("/") + "/render",
                    json=payload,
                    headers={
                        "x-api-key": SHOTSTACK_KEY,
                        "Content-Type": "application/json",
                    },
                    timeout=45,
                )
                data = response.json()
                print("shotstack:", data)
                if data.get("success") is False:
                    raise RuntimeError(data)
                response_obj = data.get("response")
                if isinstance(response_obj, dict) and response_obj.get("id"):
                    return response_obj["id"]
                raise RuntimeError(data)
            except Exception as e:
                last_error = e
                print(f"Shotstack render retry {attempt}/3:", e)
                time.sleep(2 * attempt)

        raise RuntimeError(f"Shotstack render failed: {last_error}")

    def wait(self, render_id):
        url = SHOTSTACK_BASE_URL.rstrip("/") + "/render/" + render_id

        while True:
            try:
                response = requests.get(
                    url,
                    headers={"x-api-key": SHOTSTACK_KEY},
                    timeout=45,
                )
                data = response.json()
                status = data["response"]["status"]
                print("status:", status)

                if status == "done":
                    return data["response"]["url"]

                if status == "failed":
                    raise RuntimeError(data)

            except Exception as e:
                print("Shotstack wait retry:", e)

            time.sleep(5)
