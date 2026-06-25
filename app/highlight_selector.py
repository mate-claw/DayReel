from .config import TARGET_DURATION, MAX_CLIPS, MIN_CLIPS, DEFAULT_CLIP_SECONDS

class HighlightSelector:
    def select(self, videos):
        candidates = []

        for video in videos:
            stats = video.get("stats", {})
            video_boost = 0.25 * stats.get("energy", 0) + 0.20 * stats.get("aesthetic", 0)

            for segment in video.get("segments", []):
                score = segment.get("score", 0) + video_boost
                candidates.append({
                    "video_name": video["name"],
                    "url": video["url"],
                    "local_path": video["local_path"],
                    "start": segment["start"],
                    "length": segment["length"],
                    "cover_time": segment.get("cover_time", segment["start"] + segment["length"] / 2),
                    "score": round(score, 4),
                    "motion": segment.get("motion", stats.get("motion", 0)),
                    "energy": segment.get("energy", stats.get("energy", 0)),
                    "aesthetic": segment.get("aesthetic", stats.get("aesthetic", 0)),
                    "mood": stats.get("mood", "cinematic"),
                    "scene": stats.get("best_use", "build"),
                    "summary": stats.get("summary", ""),
                })

        if not candidates:
            # No usable analysis. Use whole uploaded videos as safe fallback.
            for video in videos:
                candidates.append({
                    "video_name": video["name"],
                    "url": video["url"],
                    "local_path": video["local_path"],
                    "start": 0,
                    "length": DEFAULT_CLIP_SECONDS,
                    "cover_time": 1,
                    "score": 0.3,
                    "motion": 0.3,
                    "energy": 0.3,
                    "aesthetic": 0.3,
                    "mood": "cinematic",
                    "scene": "build",
                    "summary": "fallback",
                })

        # Coverage: ensure every source video appears at least once if possible.
        selected = []
        used_names = set()
        for c in sorted(candidates, key=lambda x: x["score"], reverse=True):
            if c["video_name"] not in used_names:
                selected.append(c)
                used_names.add(c["video_name"])

        # Fill remaining by score while avoiding duplicate near-identical segments.
        for c in sorted(candidates, key=lambda x: x["score"], reverse=True):
            if len(selected) >= MAX_CLIPS:
                break
            if self._too_close(c, selected):
                continue
            selected.append(c)

        if len(selected) < MIN_CLIPS:
            pool = sorted(candidates, key=lambda x: x["score"], reverse=True)
            i = 0
            while len(selected) < MIN_CLIPS and pool:
                base = pool[i % len(pool)].copy()
                base["start"] = max(0, base["start"] + (i // len(pool)) * base["length"])
                selected.append(base)
                i += 1

        selected = sorted(selected, key=lambda x: x["score"], reverse=True)

        # Mark story position for editing rhythm.
        if selected:
            selected[0]["scene"] = "hook"
        if len(selected) > 2:
            selected[min(2, len(selected)-1)]["scene"] = "peak"
        if len(selected) > 1:
            selected[-1]["scene"] = "end"

        total = 0
        final = []
        for c in selected:
            if total >= TARGET_DURATION:
                break
            total += c["length"]
            final.append(c)

        return final

    def _too_close(self, candidate, selected):
        for s in selected:
            if s["video_name"] == candidate["video_name"] and abs(s["start"] - candidate["start"]) < 2.0:
                return True
        return False
