from .qwen_client import QwenClient

class SemanticEnricher:
    def __init__(self):
        self.qwen = QwenClient()

    def enrich(self, analyzed_videos):
        enriched = []

        for video in analyzed_videos:
            stats = video.get("stats", {})
            try:
                ai = self.qwen.analyze_video(video["url"], stats)
            except Exception as e:
                print("Qwen analyze fallback:", e)
                ai = {
                    "summary": "local_cv_only",
                    "motion": stats.get("motion", 0.4),
                    "energy": stats.get("energy", 0.4),
                    "aesthetic": stats.get("aesthetic", 0.4),
                    "mood": stats.get("mood", "cinematic"),
                    "best_use": "build",
                    "reason": "fallback to local computer vision",
                }

            merged_stats = {
                "motion": self._mix(stats.get("motion", 0), ai.get("motion", 0.5)),
                "energy": self._mix(stats.get("energy", 0), ai.get("energy", 0.5)),
                "aesthetic": self._mix(stats.get("aesthetic", 0), ai.get("aesthetic", 0.5)),
                "mood": ai.get("mood") or stats.get("mood", "cinematic"),
                "best_use": ai.get("best_use", "build"),
                "summary": ai.get("summary", ""),
                "reason": ai.get("reason", ""),
            }

            enriched.append({**video, "stats": {**stats, **merged_stats}})
        return enriched

    def _mix(self, local_value, ai_value):
        try:
            local_value = float(local_value)
            ai_value = float(ai_value)
            return max(0.0, min(1.0, 0.55 * local_value + 0.45 * ai_value))
        except Exception:
            return local_value
