import os
from dotenv import load_dotenv
load_dotenv()

def bool_env(name, default=False):
    v=os.getenv(name)
    if v is None: return default
    return v.strip().lower() in ("1","true","yes","y","on")
def int_env(name, default):
    try: return int(os.getenv(name, default))
    except Exception: return default
def float_env(name, default):
    try: return float(os.getenv(name, default))
    except Exception: return default
AWS_ACCESS_KEY=os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY=os.getenv("AWS_SECRET_KEY")
AWS_REGION=os.getenv("AWS_REGION","us-east-1")
S3_BUCKET=os.getenv("S3_BUCKET")
SHOTSTACK_KEY=os.getenv("SHOTSTACK_KEY")
SHOTSTACK_BASE_URL=os.getenv("SHOTSTACK_BASE_URL","https://api.shotstack.io/v1")
QWEN_API_KEY=os.getenv("QWEN_API_KEY")
QWEN_BASE_URL=os.getenv("QWEN_BASE_URL","https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_VL_MODEL=os.getenv("QWEN_VL_MODEL","qwen-vl-plus")
QWEN_TEXT_MODEL=os.getenv("QWEN_TEXT_MODEL","qwen-plus")
MOCK_QWEN=bool_env("MOCK_QWEN",False)
QWEN_TIMEOUT_SECONDS=int_env("QWEN_TIMEOUT_SECONDS",35)
QWEN_MAX_IMAGES=int_env("QWEN_MAX_IMAGES",6)
TEMPLATE_JSON_PATH=os.getenv("TEMPLATE_JSON_PATH","template/shotstack_edit.json")
FORCE_CJK_FONT=bool_env("FORCE_CJK_FONT",True)
CUSTOM_FONT_URL=os.getenv("CUSTOM_FONT_URL","https://github.com/notofonts/noto-cjk/raw/main/Sans/Variable/OTF/NotoSansCJKsc-VF.otf")
CUSTOM_FONT_FAMILY=os.getenv("CUSTOM_FONT_FAMILY","NotoSansCJKsc-VF")
FONT_COLOR=os.getenv("FONT_COLOR","#000000")
SHAPE_COLOR=os.getenv("SHAPE_COLOR","#ffffff")
BACKGROUND_COLOR_2=os.getenv("BACKGROUND_COLOR_2","#ffffff")
TEST_TITLE=os.getenv("TEST_TITLE","今日高光瞬间")
TEST_SUBTITLE=os.getenv("TEST_SUBTITLE","AI 自动生成的视频回忆")
TEST_DURATION=float_env("TEST_DURATION",10)
TEST_TRIM=float_env("TEST_TRIM",0)
VIDEOS_DIR="videos"
MUSIC_PATH="music/bgm.mp3"
OUTPUT_DIR="output"
