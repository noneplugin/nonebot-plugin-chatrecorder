from nonebot_plugin_localstore import get_cache_dir

CACHE_DIR = get_cache_dir("nonebot_plugin_chatrecorder")

IMAGE_CACHE_DIR = CACHE_DIR / "images"
RECORD_CACHE_DIR = CACHE_DIR / "records"
VIDEO_CACHE_DIR = CACHE_DIR / "videos"

IMAGE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
RECORD_CACHE_DIR.mkdir(parents=True, exist_ok=True)
VIDEO_CACHE_DIR.mkdir(parents=True, exist_ok=True)
