import json, re, time, requests
from .config import QWEN_API_KEY,QWEN_BASE_URL,QWEN_VL_MODEL,QWEN_TEXT_MODEL,MOCK_QWEN,QWEN_TIMEOUT_SECONDS,TEST_TITLE,TEST_SUBTITLE
class QwenClient:
    def enabled(self): return (not MOCK_QWEN) and bool(QWEN_API_KEY) and bool(QWEN_BASE_URL)
    def _headers(self): return {"Authorization":f"Bearer {QWEN_API_KEY}","Content-Type":"application/json"}
    def _extract_json(self,text):
        if not text: raise ValueError("empty qwen content")
        text=text.strip(); text=re.sub(r"^```json\s*","",text); text=re.sub(r"^```\s*","",text); text=re.sub(r"\s*```$","",text)
        try: return json.loads(text)
        except Exception:
            m=re.search(r"\{.*\}",text,re.S)
            if m: return json.loads(m.group(0))
            raise
    def analyze_keyframes(self,image_urls):
        if not self.enabled(): return self._fallback_analysis()
        content=[{"type":"image_url","image_url":{"url":u}} for u in image_urls]
        prompt='''你是短视频剪辑导演。请根据这些关键帧判断视频风格，并返回 JSON，不要 markdown。
返回格式：
{"summary":"一句话中文描述内容","mood":"energetic|calm|cinematic","energy":0到1,"motion":0到1,"aesthetic":0到1,"template_style":"fast_reels|daily_vlog|cinematic|product|travel|wildlife","title":"12字以内中文标题","subtitle":"20字以内中文副标题","animal":"一个英文动物关键词，例如 lion/elephant/monkey"}
'''
        content.append({"type":"text","text":prompt})
        payload={"model":QWEN_VL_MODEL,"messages":[{"role":"user","content":content}],"temperature":0.2}
        last=None
        for attempt in range(1,3):
            try:
                r=requests.post(QWEN_BASE_URL.rstrip()+"/chat/completions",headers=self._headers(),json=payload,timeout=QWEN_TIMEOUT_SECONDS)
                data=r.json(); return self._extract_json(data["choices"][0]["message"]["content"])
            except Exception as e:
                last=e; print(f"Qwen VL retry {attempt}/2:",e); time.sleep(2*attempt)
        print("Qwen VL fallback:",last); return self._fallback_analysis()
    def generate_merge_plan(self,placeholders,assets,analysis):
        if not self.enabled(): return None
        prompt=f'''你是 Shotstack JSON merge 字段映射助手。
模板占位符：{json.dumps(placeholders,ensure_ascii=False)}
可用素材：{json.dumps(assets,ensure_ascii=False)}
视频分析：{json.dumps(analysis,ensure_ascii=False)}
请返回 JSON 对象，key 是占位符名字，value 是应该替换的值。
强规则：
- VIDEO/VIDEO_1/URL/SRC/CLIP/FOOTAGE/MEDIA 这类视频字段只能使用 video_urls 里的视频 URL。
- 严禁把 image_urls 或 cover_url 填到 VIDEO_* 字段。
- AUDIO/MUSIC/BGM 字段使用 music_url 或 default_merge 默认音乐。
- IMAGE/COVER/THUMB/PHOTO/POSTER 字段使用 cover_url 或 image_urls。
- Title 使用 title。
- Subtitle 使用 subtitle 或 summary。
只返回 JSON。'''
        payload={"model":QWEN_TEXT_MODEL,"messages":[{"role":"user","content":prompt}],"temperature":0.1}
        try:
            r=requests.post(QWEN_BASE_URL.rstrip()+"/chat/completions",headers=self._headers(),json=payload,timeout=QWEN_TIMEOUT_SECONDS)
            parsed=self._extract_json(r.json()["choices"][0]["message"]["content"])
            return parsed if isinstance(parsed,dict) else None
        except Exception as e:
            print("Qwen merge plan fallback:",e); return None
    def _fallback_analysis(self):
        return {"summary":TEST_SUBTITLE,"mood":"cinematic","energy":0.5,"motion":0.5,"aesthetic":0.5,"template_style":"daily_vlog","title":TEST_TITLE,"subtitle":TEST_SUBTITLE,"animal":"animal"}
