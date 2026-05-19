import os
from dotenv import load_dotenv

load_dotenv()

# AI
QWEN_API_KEY = os.environ["QWEN_API_KEY"]
QWEN_API_URL = os.environ.get("QWEN_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
QWEN_MODEL = os.environ.get("QWEN_MODEL", "qwen3.5-omni-plus")

# Auth
CHULING_SECRET = os.environ.get("CHULING_SECRET")
if not CHULING_SECRET:
    raise RuntimeError("CHULING_SECRET environment variable is required")

# Database
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./chuling.db")

# Server
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", os.path.join(os.path.dirname(__file__), "uploads"))
MAX_UPLOAD_SIZE = int(os.environ.get("MAX_UPLOAD_SIZE", str(10 * 1024 * 1024)))
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

# Rate limiting
RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "10"))
