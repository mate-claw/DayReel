import random
from .config import TARGET_DURATION

class Planner:
    def build(self, clips):
        timeline = []
        total = 0

        for c in clips:
            score = c["motion"] + c["energy"]

            if score > 1.5:
                d = random.uniform(1.5, 2.5)
            else:
                d = random.uniform(2.5, 4.5)

            if total + d > TARGET_DURATION:
                break

            timeline.append({
                "asset": {"type": "video", "src": c["url"]},
                "start": "auto",
                "length": d
            })

            total += d

        return timeline
