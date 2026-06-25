import os
import cv2
import numpy as np
from .config import SAMPLE_EVERY_SECONDS, DEFAULT_CLIP_SECONDS

class LocalVideoAnalyzer:
    '''
    Non-random high-light detection using OpenCV.

    It scores sampled frames using:
    - motion: frame-to-frame difference
    - sharpness: Laplacian variance
    - brightness balance: avoid too dark/too bright
    - colorfulness: visual richness
    '''

    def analyze_video(self, item):
        path = item["local_path"]
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            print("cannot open video:", path)
            return {
                **item,
                "duration": 0,
                "segments": [],
                "stats": {"motion": 0, "energy": 0, "aesthetic": 0, "mood": "cinematic"},
            }

        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
        duration = total_frames / fps if fps else 0

        step_frames = max(1, int(fps * SAMPLE_EVERY_SECONDS))
        prev_gray = None
        samples = []
        frame_idx = 0

        while True:
            ok, frame = cap.read()
            if not ok:
                break

            if frame_idx % step_frames != 0:
                frame_idx += 1
                continue

            ts = frame_idx / fps
            small = cv2.resize(frame, (320, 180))
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

            if prev_gray is None:
                motion = 0.0
            else:
                diff = cv2.absdiff(gray, prev_gray)
                motion = float(np.mean(diff) / 255.0)

            sharpness = float(min(cv2.Laplacian(gray, cv2.CV_64F).var() / 500.0, 1.0))
            brightness_raw = float(np.mean(gray) / 255.0)
            brightness = max(0.0, 1.0 - abs(brightness_raw - 0.55) / 0.55)

            b, g, r = cv2.split(small.astype("float"))
            rg = np.abs(r - g)
            yb = np.abs(0.5 * (r + g) - b)
            colorfulness = float(min((np.std(rg) + np.std(yb)) / 80.0, 1.0))

            energy = min(1.0, motion * 4.0)
            aesthetic = 0.45 * sharpness + 0.35 * brightness + 0.20 * colorfulness
            score = 0.50 * energy + 0.30 * aesthetic + 0.20 * motion

            samples.append({
                "time": ts,
                "motion": motion,
                "energy": energy,
                "sharpness": sharpness,
                "brightness": brightness,
                "colorfulness": colorfulness,
                "aesthetic": aesthetic,
                "score": score,
            })

            prev_gray = gray
            frame_idx += 1

        cap.release()

        segments = self._build_segments(samples, duration)
        stats = self._aggregate_stats(samples)
        stats["mood"] = self._mood(stats)

        return {
            **item,
            "duration": duration,
            "segments": segments,
            "stats": stats,
        }

    def analyze(self, uploaded_items):
        return [self.analyze_video(item) for item in uploaded_items]

    def _build_segments(self, samples, duration):
        if not samples:
            return []

        ranked = sorted(samples, key=lambda x: x["score"], reverse=True)
        selected = []

        for sample in ranked:
            start = max(0.0, sample["time"] - 0.75)
            length = min(DEFAULT_CLIP_SECONDS, max(1.0, duration - start))
            if length <= 0:
                continue

            overlaps = False
            for s in selected:
                if abs(start - s["start"]) < DEFAULT_CLIP_SECONDS:
                    overlaps = True
                    break
            if overlaps:
                continue

            selected.append({
                "start": round(start, 2),
                "length": round(length, 2),
                "score": round(sample["score"], 4),
                "motion": round(sample["motion"], 4),
                "energy": round(sample["energy"], 4),
                "aesthetic": round(sample["aesthetic"], 4),
                "cover_time": round(sample["time"], 2),
            })

            if len(selected) >= 5:
                break

        return sorted(selected, key=lambda x: x["start"])

    def _aggregate_stats(self, samples):
        if not samples:
            return {"motion": 0, "energy": 0, "aesthetic": 0, "score": 0}

        top = sorted(samples, key=lambda x: x["score"], reverse=True)[: max(1, min(5, len(samples)))]
        return {
            "motion": float(np.mean([x["motion"] for x in top])),
            "energy": float(np.mean([x["energy"] for x in top])),
            "aesthetic": float(np.mean([x["aesthetic"] for x in top])),
            "score": float(np.mean([x["score"] for x in top])),
        }

    def _mood(self, stats):
        if stats["energy"] >= 0.55 or stats["motion"] >= 0.12:
            return "energetic"
        if stats["energy"] <= 0.25 and stats["aesthetic"] >= 0.45:
            return "calm"
        return "cinematic"
