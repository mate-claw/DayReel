import json
from .qwen_client import QwenClient

class Vision:
    def __init__(self):
        self.qwen = QwenClient()

    def analyze(self, videos):
        out = []

        for v in videos:
            try:
                res = self.qwen.analyze_video(v)
                content = res["choices"][0]["message"]["content"]
                data = json.loads(content)

                out.append({
                    "url": v,
                    "motion": data["motion"],
                    "energy": data["energy"],
                    "aesthetic": data["aesthetic"],
                    "scene": data["scene"]
                })

            except Exception as e:
                print("fallback:", e)
                out.append({
                    "url": v,
                    "motion": 0.5,
                    "energy": 0.5,
                    "aesthetic": 0.5,
                    "scene": "build"
                })

        return out
