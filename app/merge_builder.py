import json, os
from .config import TEST_TITLE,TEST_SUBTITLE,TEST_DURATION,TEST_TRIM,FONT_COLOR,SHAPE_COLOR,BACKGROUND_COLOR_2
class MergeBuilder:
    VIDEO_EXTS=(".mp4",".m4v",".mov",".webm",".mkv",".avi",".3gp",".flv")
    IMAGE_EXTS=(".jpg",".jpeg",".png",".webp")
    AUDIO_EXTS=(".mp3",".wav",".m4a",".aac",".ogg")
    def build(self,placeholders,assets,default_merge=None,ai_plan=None):
        default_merge=default_merge or {}; mp={}; video_i=0; image_i=0
        for field in placeholders:
            replace=None
            if ai_plan and field in ai_plan and self._valid_for_field(field,ai_plan[field]): replace=ai_plan[field]
            elif ai_plan and field in ai_plan: print(f"AI merge ignored for {field}: invalid asset type -> {str(ai_plan[field])[:80]}")
            if replace in (None,""):
                replace,video_i,image_i=self._heuristic(field,video_i,image_i,assets,default_merge)
            mp[field]=replace
        manual=self._load_manual()
        if manual: mp.update(manual)
        return [{"find":k,"replace":v} for k,v in mp.items()]
    def _load_manual(self):
        path="manual_merge.json"
        if not os.path.exists(path): return None
        with open(path,"r",encoding="utf-8") as f: data=json.load(f)
        print("using manual_merge.json overrides")
        if isinstance(data,dict): return data
        if isinstance(data,list): return {str(i["find"]):i["replace"] for i in data if isinstance(i,dict) and "find" in i and "replace" in i}
        return None
    def _heuristic(self,field,video_i,image_i,assets,default_merge):
        f=field.upper(); video_urls=assets.get("video_urls",[]); image_urls=assets.get("image_urls",[]); music_url=assets.get("music_url"); cover_url=assets.get("cover_url")
        title=assets.get("title") or TEST_TITLE; subtitle=assets.get("subtitle") or assets.get("summary") or TEST_SUBTITLE
        if self._is_video_field(field):
            if video_urls: return video_urls[video_i % len(video_urls)], video_i+1, image_i
            return default_merge.get(field,""), video_i, image_i
        if self._is_audio_field(field): return music_url or default_merge.get(field,""), video_i, image_i
        if self._is_image_field(field):
            if cover_url: return cover_url,video_i,image_i
            if image_urls: return image_urls[image_i % len(image_urls)],video_i,image_i+1
            return default_merge.get(field,""),video_i,image_i
        if field=="Title" or f=="TITLE": return title,video_i,image_i
        if field=="Subtitle" or f=="SUBTITLE": return subtitle,video_i,image_i
        if any(k in f for k in ["DESCRIPTION","DESC","BODY"]): return subtitle,video_i,image_i
        if any(k in f for k in ["FONT_COLOR","TEXT_COLOR"]): return FONT_COLOR or default_merge.get(field,"#000000"),video_i,image_i
        if "SHAPE_COLOR" in f: return SHAPE_COLOR or default_merge.get(field,"#ffffff"),video_i,image_i
        if "BACKGROUND_COLOR_2" in f or "BG_COLOR" in f: return BACKGROUND_COLOR_2 or default_merge.get(field,"#ffffff"),video_i,image_i
        if any(k in f for k in ["DURATION","LENGTH"]): return TEST_DURATION,video_i,image_i
        if any(k in f for k in ["TRIM","START","OFFSET"]): return TEST_TRIM,video_i,image_i
        if field=="animal": return assets.get("animal") or default_merge.get(field,"animal"),video_i,image_i
        if field=="name": return default_merge.get(field,"World"),video_i,image_i
        return default_merge.get(field,title),video_i,image_i
    def _valid_for_field(self,field,value):
        if value is None: return False
        if isinstance(value,(int,float)): return True
        if not isinstance(value,str): return False
        value=value.strip()
        if self._is_video_field(field): return self._looks_like_ext(value,self.VIDEO_EXTS)
        if self._is_audio_field(field): return value=="" or self._looks_like_ext(value,self.AUDIO_EXTS)
        if self._is_image_field(field): return value=="" or self._looks_like_ext(value,self.IMAGE_EXTS)
        return True
    def _looks_like_ext(self,url,exts): return url.split("?")[0].split("#")[0].lower().endswith(exts)
    def _is_video_field(self,field):
        f=field.upper(); compact=f.replace("_","").replace("-","").replace(" ","")
        if compact.startswith("VIDEO") and compact[5:].isdigit(): return True
        if any(k in f for k in ["VIDEO","CLIP","FOOTAGE"]): return not any(k in f for k in ["MUSIC","AUDIO","BGM","IMAGE","PHOTO","COVER","THUMB","POSTER"])
        if any(k in f for k in ["URL","SRC","MEDIA"]): return not any(k in f for k in ["MUSIC","AUDIO","BGM","IMAGE","PHOTO","COVER","THUMB","POSTER"])
        return False
    def _is_audio_field(self,field): return any(k in field.upper() for k in ["MUSIC","AUDIO","BGM","SOUND"])
    def _is_image_field(self,field): return any(k in field.upper() for k in ["IMAGE","PHOTO","COVER","THUMB","POSTER"])
