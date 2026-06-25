import json, os
from .config import VIDEOS_DIR,MUSIC_PATH,OUTPUT_DIR
from .uploader import S3Uploader
from .keyframes import KeyframeExtractor
from .qwen_client import QwenClient
from .template_loader import TemplateLoader
from .merge_builder import MergeBuilder
from .font_manager import FontManager
from .shotstack_render import ShotstackRenderer
class JsonQwenRenderPipeline:
    def run(self):
        os.makedirs(OUTPUT_DIR,exist_ok=True)
        print("1) upload local videos"); uploader=S3Uploader(); videos=uploader.upload_videos(VIDEOS_DIR)
        if not videos: raise RuntimeError("No videos found. Put .mp4 files into videos/")
        print("2) upload music"); music_url=uploader.upload_music(MUSIC_PATH)
        print("3) extract and upload keyframes"); extractor=KeyframeExtractor(); frames=extractor.extract(videos); cover_path=extractor.cover_from_first(videos)
        image_urls=[]
        for frame in frames:
            try: image_urls.append(uploader.upload_image(frame["path"]))
            except Exception as e: print("keyframe upload failed:",e)
        cover_url=uploader.upload_image(cover_path) if cover_path else None
        print("4) Qwen AI analyze"); qwen=QwenClient(); analysis=qwen.analyze_keyframes(image_urls)
        title=analysis.get("title") or "今日高光瞬间"; subtitle=analysis.get("subtitle") or analysis.get("summary") or "AI 自动生成的视频回忆"
        with open(os.path.join(OUTPUT_DIR,"qwen_analysis.json"),"w",encoding="utf-8") as f: json.dump(analysis,f,ensure_ascii=False,indent=2)
        print("AI title:",title); print("AI subtitle:",subtitle); print("AI summary:",analysis.get("summary"))
        print("5) load Shotstack JSON"); loader=TemplateLoader(); template=loader.load(); default_merge=loader.default_merge_map(template); placeholders=loader.placeholders(template)
        with open(os.path.join(OUTPUT_DIR,"template_placeholders.json"),"w",encoding="utf-8") as f: json.dump(placeholders,f,ensure_ascii=False,indent=2)
        print("placeholders:",placeholders)
        print("6) Qwen AI merge planning")
        assets={"title":title,"subtitle":subtitle,"summary":analysis.get("summary",subtitle),"animal":analysis.get("animal","animal"),"video_urls":[v["url"] for v in videos],"music_url":music_url,"cover_url":cover_url,"image_urls":image_urls,"default_merge":default_merge}
        ai_plan=qwen.generate_merge_plan(placeholders,assets,analysis)
        with open(os.path.join(OUTPUT_DIR,"qwen_merge_plan.json"),"w",encoding="utf-8") as f: json.dump(ai_plan,f,ensure_ascii=False,indent=2)
        print("7) build safe merge fields"); merge=MergeBuilder().build(placeholders,assets,default_merge=default_merge,ai_plan=ai_plan)
        with open(os.path.join(OUTPUT_DIR,"merge.json"),"w",encoding="utf-8") as f: json.dump(merge,f,ensure_ascii=False,indent=2)
        for item in merge: print(" ",item["find"],"=>",str(item["replace"])[:90])
        print("8) resolve JSON placeholders locally"); resolved=loader.resolve(template,merge)
        print("9) apply Chinese font fix"); resolved=FontManager().apply(resolved)
        payload_path=os.path.join(OUTPUT_DIR,"render_payload.json")
        with open(payload_path,"w",encoding="utf-8") as f: json.dump(resolved,f,ensure_ascii=False,indent=2)
        print("10) render with Shotstack /render"); renderer=ShotstackRenderer(); render_id=renderer.render(resolved); print("render id:",render_id)
        print("11) wait render"); video_url=renderer.wait(render_id)
        result={"title":title,"subtitle":subtitle,"analysis":analysis,"video_url":video_url,"music_url":music_url,"cover_url":cover_url,"image_urls":image_urls,"merge":merge,"payload_path":payload_path}
        result_path=os.path.join(OUTPUT_DIR,"result.json")
        with open(result_path,"w",encoding="utf-8") as f: json.dump(result,f,ensure_ascii=False,indent=2)
        print("\nJSON + QWEN DIRECT RENDER READY"); print("TITLE:",title); print("VIDEO:",video_url); print("RESULT:",result_path)
        return result
