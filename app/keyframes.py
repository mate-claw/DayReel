import os, cv2
from .config import OUTPUT_DIR,QWEN_MAX_IMAGES
class KeyframeExtractor:
    def extract(self,videos):
        os.makedirs(OUTPUT_DIR,exist_ok=True); frame_dir=os.path.join(OUTPUT_DIR,"keyframes"); os.makedirs(frame_dir,exist_ok=True)
        frames=[]
        for item in videos:
            frames.extend(self._extract_from_video(item,frame_dir))
            if len(frames)>=QWEN_MAX_IMAGES: break
        return frames[:QWEN_MAX_IMAGES]
    def cover_from_first(self,videos):
        if not videos: return None
        frames=self._extract_from_video(videos[0],OUTPUT_DIR,max_count=1)
        return frames[0]["path"] if frames else None
    def _extract_from_video(self,item,frame_dir,max_count=2):
        path=item["path"]; cap=cv2.VideoCapture(path)
        if not cap.isOpened(): return []
        fps=cap.get(cv2.CAP_PROP_FPS) or 25; total=cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0; duration=total/fps if fps else 0
        times=[0.5] if duration<=2 else [duration*0.20,duration*0.55,duration*0.82]
        result=[]; base=os.path.splitext(os.path.basename(path))[0]
        for i,t in enumerate(times[:max_count]):
            cap.set(cv2.CAP_PROP_POS_FRAMES,int(max(0,t)*fps)); ok,frame=cap.read()
            if not ok: continue
            frame=self._resize(frame); out=os.path.join(frame_dir,f"{base}_{i}.jpg")
            cv2.imwrite(out,frame,[int(cv2.IMWRITE_JPEG_QUALITY),88]); result.append({"video_name":item["name"],"path":out,"time":round(t,2)})
        cap.release(); return result
    def _resize(self,frame):
        h,w=frame.shape[:2]; max_side=1024; scale=min(1.0,max_side/max(h,w))
        return cv2.resize(frame,(int(w*scale),int(h*scale))) if scale<1.0 else frame
