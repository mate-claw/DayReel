import os
import cv2
from .config import OUTPUT_DIR

class CoverGenerator:
    def generate(self, clips, title: str = ""):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, "cover.jpg")

        if not clips:
            return None

        best = sorted(clips, key=lambda x: x.get("score", 0), reverse=True)[0]
        path = best["local_path"]
        cover_time = best.get("cover_time", best.get("start", 0) + best.get("length", 2) / 2)

        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            return None

        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(max(0, cover_time) * fps))
        ok, frame = cap.read()
        cap.release()

        if not ok:
            return None

        frame = self._resize_cover(frame)
        frame = self._add_gradient(frame)

        if title:
            self._put_text(frame, title)

        cv2.imwrite(output_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        return output_path

    def _resize_cover(self, frame):
        # 9:16 cover, 1080x1920
        h, w = frame.shape[:2]
        target_w, target_h = 1080, 1920
        scale = max(target_w / w, target_h / h)
        resized = cv2.resize(frame, (int(w * scale), int(h * scale)))
        rh, rw = resized.shape[:2]
        x = max(0, (rw - target_w) // 2)
        y = max(0, (rh - target_h) // 2)
        return resized[y:y + target_h, x:x + target_w]

    def _add_gradient(self, frame):
        h, w = frame.shape[:2]
        overlay = frame.copy()
        for y in range(int(h * 0.55), h):
            alpha = (y - h * 0.55) / (h * 0.45)
            overlay[y, :] = overlay[y, :] * (1 - 0.45 * alpha)
        return overlay

    def _put_text(self, frame, title):
        h, w = frame.shape[:2]
        text = title[:24]
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.8
        thickness = 4
        x = 70
        y = h - 220

        cv2.putText(frame, text, (x, y), font, font_scale, (0, 0, 0), thickness + 5, cv2.LINE_AA)
        cv2.putText(frame, text, (x, y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
