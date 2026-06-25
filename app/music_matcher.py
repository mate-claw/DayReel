import os
import glob
from collections import Counter
from .config import MUSIC_DIR

class MusicMatcher:
    def choose(self, clips):
        mood = self.detect_mood(clips)

        candidates = []
        mood_dir = os.path.join(MUSIC_DIR, mood)
        if os.path.isdir(mood_dir):
            candidates = sorted(glob.glob(os.path.join(mood_dir, "*.mp3")))

        if not candidates:
            default = os.path.join(MUSIC_DIR, "bgm.mp3")
            if os.path.exists(default):
                return default, mood

        if not candidates:
            any_music = sorted(glob.glob(os.path.join(MUSIC_DIR, "**", "*.mp3"), recursive=True))
            if any_music:
                return any_music[0], mood

        return None, mood

    def detect_mood(self, clips):
        if not clips:
            return "cinematic"

        avg_energy = sum(c.get("energy", 0) for c in clips) / len(clips)
        avg_motion = sum(c.get("motion", 0) for c in clips) / len(clips)
        avg_aesthetic = sum(c.get("aesthetic", 0) for c in clips) / len(clips)

        labeled = [c.get("mood") for c in clips if c.get("mood")]
        if labeled:
            top_mood, count = Counter(labeled).most_common(1)[0]
            if count >= max(2, len(clips) // 3):
                return top_mood

        if avg_energy > 0.55 or avg_motion > 0.12:
            return "energetic"
        if avg_energy < 0.30 and avg_aesthetic > 0.45:
            return "calm"
        return "cinematic"
