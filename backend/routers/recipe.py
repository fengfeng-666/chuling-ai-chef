import os
import uuid
import json
import aiofiles
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from config import UPLOAD_DIR, MAX_UPLOAD_SIZE
from services.ai_service import analyze_ingredients, quiz_recommend, chat_with_ai, chat_with_ai_stream
from database import get_db
from models import User, ChatSession, Message
from auth import get_current_user, get_optional_user

router = APIRouter(prefix="/api")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


class QuizAnswers(BaseModel):
    answers: dict


@router.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    if file.content_type and file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"不支持的图片格式: {file.content_type}")

    image_bytes = await file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="上传的图片为空")
    if len(image_bytes) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail=f"图片大小不能超过 {MAX_UPLOAD_SIZE // (1024*1024)}MB")

    ext = os.path.splitext(file.filename or "image.jpg")[1] or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filepath = os.path.join(UPLOAD_DIR, filename)
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(image_bytes)

    mime_type = file.content_type or "image/jpeg"
    try:
        result = await analyze_ingredients(image_bytes, mime_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 分析失败: {str(e)}")

    return {"success": True, "image_url": f"/uploads/{filename}", **result}


@router.post("/quiz-recommend")
async def quiz_recommend_endpoint(body: QuizAnswers):
    if not body.answers:
        raise HTTPException(status_code=400, detail="答题结果不能为空")
    try:
        result = await quiz_recommend(body.answers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 推荐失败: {str(e)}")
    return {"success": True, **result}


@router.post("/chat")
async def chat_endpoint(
    message: str = Form(""),
    session_id: int = Form(None),
    file: UploadFile = File(None),
    history_json: str = Form(None),
    user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    if not message and not file:
        raise HTTPException(status_code=400, detail="消息和图片不能同时为空")

    # 处理图片上传
    image_url = ""
    image_bytes = None
    mime_type = None
    if file is not None:
        if file.content_type and file.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail=f"不支持的图片格式: {file.content_type}")
        image_bytes = await file.read()
        mime_type = file.content_type or "image/jpeg"
        if len(image_bytes) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail=f"图片大小不能超过 {MAX_UPLOAD_SIZE // (1024*1024)}MB")

        ext = os.path.splitext(file.filename or "image.jpg")[1] or ".jpg"
        filename = f"{uuid.uuid4()}{ext}"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filepath = os.path.join(UPLOAD_DIR, filename)
        async with aiofiles.open(filepath, "wb") as f:
            await f.write(image_bytes)
        image_url = f"/uploads/{filename}"

    # 收集对话历史
    history = None
    if user and session_id:
        db_msgs = (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(20)
            .all()
        )
        history = [{"role": m.role, "content": m.content} for m in reversed(db_msgs)]
    elif history_json:
        try:
            history = json.loads(history_json)
        except json.JSONDecodeError:
            pass

    # 调用 AI（无论是否登录都执行）
    try:
        result = await chat_with_ai(message, image_bytes, mime_type, history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 对话失败: {str(e)}")

    reply = result.get("reply", "")
    ingredients = result.get("ingredients", [])
    recipes = result.get("recipes", [])

    response_data = {
        "success": True,
        "reply": reply,
        "ingredients": ingredients,
        "recipes": recipes,
    }

    # 已登录用户：保存消息到数据库
    if user:
        session = None
        if session_id:
            session = db.query(ChatSession).filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user.id,
            ).first()
            if not session:
                raise HTTPException(status_code=404, detail="会话不存在")

        if not session:
            session = ChatSession(user_id=user.id)
            db.add(session)
            db.commit()
            db.refresh(session)

        user_msg = Message(
            session_id=session.id,
            role="user",
            content=message or "帮我看看这些食材能做什么菜",
            image_url=image_url,
        )
        db.add(user_msg)
        db.commit()

        ai_msg = Message(
            session_id=session.id,
            role="ai",
            content=reply,
            ingredients_json=json.dumps(ingredients, ensure_ascii=False),
            recipes_json=json.dumps(recipes, ensure_ascii=False),
        )
        db.add(ai_msg)

        if session.title == "新对话" and reply:
            title = reply[:20].strip()
            if len(reply) > 20:
                title += "…"
            session.title = title

        db.commit()
        response_data["session_id"] = session.id

    return response_data


@router.post("/chat/stream")
async def chat_stream_endpoint(
    message: str = Form(""),
    session_id: int = Form(None),
    file: UploadFile = File(None),
    history_json: str = Form(None),
    user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    if not message and not file:
        raise HTTPException(status_code=400, detail="消息和图片不能同时为空")

    # 处理图片上传
    image_url = ""
    image_bytes = None
    mime_type = None
    if file is not None:
        if file.content_type and file.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail=f"不支持的图片格式: {file.content_type}")
        image_bytes = await file.read()
        mime_type = file.content_type or "image/jpeg"
        if len(image_bytes) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail=f"图片大小不能超过 {MAX_UPLOAD_SIZE // (1024*1024)}MB")
        ext = os.path.splitext(file.filename or "image.jpg")[1] or ".jpg"
        filename = f"{uuid.uuid4()}{ext}"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filepath = os.path.join(UPLOAD_DIR, filename)
        async with aiofiles.open(filepath, "wb") as f:
            await f.write(image_bytes)
        image_url = f"/uploads/{filename}"

    # 收集对话历史
    history = None
    if user and session_id:
        db_msgs = (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(20)
            .all()
        )
        history = [{"role": m.role, "content": m.content} for m in reversed(db_msgs)]
    elif history_json:
        try:
            history = json.loads(history_json)
        except json.JSONDecodeError:
            pass

    async def event_generator():
        full_reply = ""
        saved_recipes = []
        saved_ingredients = []
        saved_session = None
        saved_session_id = None
        db_error = False

        # 已登录：先保存用户消息
        if user:
            try:
                session_obj = None
                if session_id:
                    session_obj = db.query(ChatSession).filter(
                        ChatSession.id == session_id,
                        ChatSession.user_id == user.id,
                    ).first()

                if not session_obj:
                    session_obj = ChatSession(user_id=user.id)
                    db.add(session_obj)
                    db.commit()
                    db.refresh(session_obj)

                saved_session = session_obj
                saved_session_id = session_obj.id

                user_msg = Message(
                    session_id=session_obj.id,
                    role="user",
                    content=message or "帮我看看这些食材能做什么菜",
                    image_url=image_url,
                )
                db.add(user_msg)
                db.commit()
            except Exception:
                db_error = True
                yield f"data: {json.dumps({'type': 'error', 'message': '保存消息失败'}, ensure_ascii=False)}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                return

        # 流式调用 AI
        try:
            async for event_type, data in chat_with_ai_stream(message, image_bytes, mime_type, history):
                if event_type == "text":
                    full_reply += data
                    yield f"data: {json.dumps({'type': 'text', 'content': data}, ensure_ascii=False)}\n\n"
                elif event_type == "recipes":
                    saved_recipes = data.get('recipes', [])
                    saved_ingredients = data.get('ingredients', [])
                    yield f"data: {json.dumps({'type': 'recipes', 'recipes': saved_recipes, 'ingredients': saved_ingredients}, ensure_ascii=False)}\n\n"
                elif event_type == "error":
                    yield f"data: {json.dumps({'type': 'error', 'message': data}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'流式响应异常: {str(e)}'}, ensure_ascii=False)}\n\n"

        # 已登录：保存 AI 回复
        if user and saved_session and not db_error and full_reply:
            try:
                ai_msg = Message(
                    session_id=saved_session.id,
                    role="ai",
                    content=full_reply,
                    ingredients_json=json.dumps(saved_ingredients, ensure_ascii=False),
                    recipes_json=json.dumps(saved_recipes, ensure_ascii=False),
                )
                db.add(ai_msg)

                if saved_session.title == "新对话":
                    title = full_reply[:20].strip()
                    if len(full_reply) > 20:
                        title += "…"
                    saved_session.title = title

                db.commit()
            except Exception:
                pass  # 非致命错误

        yield f"data: {json.dumps({'type': 'done', 'session_id': saved_session_id}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
