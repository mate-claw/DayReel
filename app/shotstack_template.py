import json
import re
import time
import requests
from .config import SHOTSTACK_KEY, SHOTSTACK_ENV

class ShotstackTemplateClient:
    def __init__(self):
        if not SHOTSTACK_KEY:
            raise ValueError("SHOTSTACK_KEY missing in .env")
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": SHOTSTACK_KEY,
        }
        env = SHOTSTACK_ENV.strip("/")
        self.template_bases = [
            f"https://api.shotstack.io/{env}",
            f"https://api.shotstack.io/edit/{env}",
        ]
        self.render_bases = [
            f"https://api.shotstack.io/{env}",
            f"https://api.shotstack.io/edit/{env}",
        ]

    def get_template(self, template_id):
        last = None
        for base in self.template_bases:
            try:
                url = f"{base}/templates/{template_id}"
                r = requests.get(url, headers=self.headers, timeout=45)
                data = r.json()
                if r.status_code < 400:
                    print("template base:", base)
                    return data
                last = data
            except Exception as e:
                last = e
            print("get template failed:", base, last)
        raise RuntimeError(f"Cannot get template {template_id}: {last}")

    def placeholders(self, template_response):
        text = json.dumps(template_response, ensure_ascii=False)
        return sorted(set(re.findall(r"\{\{\s*([A-Za-z0-9_\-\.]+)\s*\}\}", text)))

    def render_template(self, template_id, merge):
        payload = {"id": template_id, "merge": merge}
        last = None
        for base in self.template_bases:
            try:
                url = f"{base}/templates/render"
                r = requests.post(url, headers=self.headers, json=payload, timeout=45)
                data = r.json()
                print("template render response:", data)
                if isinstance(data.get("response"), dict) and data["response"].get("id"):
                    return data["response"]["id"]
                last = data
            except Exception as e:
                last = e
            print("render template failed:", base, last)
        raise RuntimeError(f"Template render failed: {last}")

    def wait(self, render_id):
        while True:
            for base in self.render_bases:
                try:
                    url = f"{base}/render/{render_id}"
                    r = requests.get(url, headers=self.headers, timeout=45)
                    data = r.json()
                    if not isinstance(data.get("response"), dict):
                        continue
                    status = data["response"].get("status")
                    print("status:", status)
                    if status == "done":
                        return data["response"].get("url")
                    if status == "failed":
                        raise RuntimeError(data)
                    break
                except Exception as e:
                    print("wait retry:", e)
            time.sleep(5)
