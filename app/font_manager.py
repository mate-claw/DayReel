from .config import FORCE_CJK_FONT,CUSTOM_FONT_URL,CUSTOM_FONT_FAMILY
class FontManager:
    def apply(self,payload):
        if not FORCE_CJK_FONT: return payload
        tl=payload.setdefault("timeline",{}); fonts=tl.setdefault("fonts",[])
        if not any(isinstance(f,dict) and f.get("src")==CUSTOM_FONT_URL for f in fonts): fonts.append({"src":CUSTOM_FONT_URL})
        self._walk(payload); return payload
    def _walk(self,value):
        if isinstance(value,dict):
            if value.get("type") in ("text","rich-text"):
                font=value.setdefault("font",{})
                if isinstance(font,dict): font["family"]=CUSTOM_FONT_FAMILY
            for v in value.values(): self._walk(v)
        elif isinstance(value,list):
            for i in value: self._walk(i)
