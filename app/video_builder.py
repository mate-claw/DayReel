from .config import TARGET_DURATION

class VideoBuilder:
    def build(self, clips, music_url=None, title=None):
        timeline_clips = []
        total = 0.0

        for c in clips:
            duration = self._duration_for(c)

            if total + duration > TARGET_DURATION:
                duration = max(1.2, TARGET_DURATION - total)

            if duration <= 0:
                break

            timeline_clips.append({
                "asset": {
                    "type": "video",
                    "src": c["url"],
                    "trim": c["start"],
                },
                "start": "auto",
                "length": round(duration, 2),
                "transition": {
                    "in": "fade",
                    "out": "fade",
                },
            })

            total += duration
            if total >= TARGET_DURATION:
                break

        timeline = {"tracks": [{"clips": timeline_clips}]}

        if music_url:
            timeline["soundtrack"] = {
                "src": music_url,
                "volume": 0.28,
                "effect": "fadeOut",
            }

        return {
            "timeline": timeline,
            "output": {
                "format": "mp4",
                "resolution": "1080",
            },
        }

    def _duration_for(self, clip):
        scene = clip.get("scene", "build")
        score = clip.get("score", 0.5)

        if scene == "hook":
            return 1.6
        if scene == "peak":
            return 1.8
        if scene == "end":
            return 3.8
        if score > 0.75:
            return 2.0
        if score > 0.5:
            return 2.8
        return 3.6
