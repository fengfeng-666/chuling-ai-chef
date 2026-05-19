import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import CORS_ORIGINS, UPLOAD_DIR
from database import engine, Base
from middleware import RateLimitMiddleware, LoggingMiddleware
from models import User, ChatSession, Message
from routers.recipe import router as recipe_router
from routers.auth_router import router as auth_router
from routers.sessions_router import router as sessions_router

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="厨灵 - AI 智能菜谱推荐系统", version="2.0.0")

# 中间件顺序：日志 → 限流 → CORS（后添加的先执行）
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)

os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(recipe_router)
app.include_router(auth_router)
app.include_router(sessions_router)


@app.get("/")
async def root():
    return {"message": "厨灵 API", "version": "2.0.0"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
