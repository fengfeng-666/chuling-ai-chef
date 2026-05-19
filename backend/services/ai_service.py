import base64
import json
import httpx

from config import QWEN_API_KEY, QWEN_API_URL, QWEN_MODEL

SYSTEM_PROMPT = """你是一个专业的厨师和食材识别专家。用户会提供一张食材图片。

请完成以下任务：
1. 识别图片中的所有食材
2. 根据这些食材推荐 2-3 道可以制作的菜品
3. 每道菜提供详细的做法步骤

请严格按照以下 JSON 格式返回，不要包含其他内容：
{
  "ingredients": ["食材1", "食材2", ...],
  "recipes": [
    {
      "name": "菜名",
      "description": "简短描述",
      "difficulty": "简单/中等/困难",
      "cooking_time": "预估时间",
      "ingredients_needed": ["所需食材1", "所需食材2", ...],
      "steps": [
        {"step": 1, "description": "步骤描述"},
        {"step": 2, "description": "步骤描述"}
      ]
    }
  ]
}

注意：
- 识别食材时，只列出图片中实际看到的食材
- 推荐菜谱时，优先推荐以识别到的食材为主的菜品
- ingredients_needed 中应包含识别到的食材，以及可能需要的基础调味料
- 步骤要详细实用，每步讲清楚操作要点
- 如果图片不包含食材或无法识别，ingredients 返回空数组，recipes 返回空数组
"""


async def analyze_ingredients(image_bytes: bytes, mime_type: str) -> dict:
    """将图片发送给 Qwen 模型，返回识别的食材和推荐菜谱。"""
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{image_base64}"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": data_url}},
                {"type": "text", "text": "请识别这张图片中的食材，并推荐可以制作的菜品。"},
            ],
        },
    ]

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            QWEN_API_URL,
            headers={
                "Authorization": f"Bearer {QWEN_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": QWEN_MODEL,
                "messages": messages,
                "max_tokens": 4096,
                "temperature": 0.7,
            },
        )
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"]
    return _parse_json_response(content)


QUIZ_PROMPT = """你是一个专业的厨师和美食推荐专家。用户做了一系列口味偏好选择题，请根据用户的答案推荐 3 道最适合的菜品。

请严格按照以下 JSON 格式返回，不要包含其他内容：
{
  "recommend_reason": "基于用户选择的一两句话总结推荐理由",
  "recipes": [
    {
      "name": "菜名",
      "description": "简短描述",
      "difficulty": "简单/中等/困难",
      "cooking_time": "预估时间",
      "ingredients_needed": ["所需食材1", "所需食材2", ...],
      "steps": [
        {"step": 1, "description": "步骤描述"},
        {"step": 2, "description": "步骤描述"}
      ]
    }
  ]
}

注意：
- 推荐理由要结合用户的具体偏好
- 推荐的 3 道菜尽量风格多元但都符合用户口味
- 步骤要详细实用，每步讲清楚操作要点
- 只返回 JSON，不要有其他内容
"""


async def quiz_recommend(answers: dict) -> dict:
    """根据用户的选择题答案，调用 AI 推荐菜谱。"""
    answers_text = "\n".join(
        f"- {q}: {a}" for q, a in answers.items()
    )

    user_message = f"""用户的饮食偏好如下：
{answers_text}

请根据以上偏好推荐 3 道最合适的菜品，并给出详细做法。"""

    messages = [
        {"role": "system", "content": QUIZ_PROMPT},
        {"role": "user", "content": user_message},
    ]

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            QWEN_API_URL,
            headers={
                "Authorization": f"Bearer {QWEN_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": QWEN_MODEL,
                "messages": messages,
                "max_tokens": 4096,
                "temperature": 0.8,
            },
        )
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"]
    return _parse_json_response(content)


CHAT_PROMPT = """你叫"厨灵"，是一个热情的 AI 厨师助手。你可以通过文字和图片与用户交流，帮他们解决做菜相关的问题。

你的能力包括：
1. 根据用户描述的口味、心情、场景推荐菜品
2. 识别食材图片，推荐可以制作的菜品
3. 回答烹饪技巧问题（火候、调味、食材处理等）
4. 对任何菜品给出详细的做法步骤

回复规范：
- 语气热情友好，像一位经验丰富的厨师朋友
- 如果推荐了菜品，一定要附带完整的做法步骤
- 如果用户上传了食材图片，先告诉用户你看到了哪些食材

输出格式（非常重要）：

第一步：先输出自然语言回复
直接写你的回复内容，就像和朋友聊天一样。语气热情友好，口语化。
这部分会实时显示给用户，请自然地从头开始写。

第二步：输出结构化数据
在自然语言回复写完之后，单独另起一行输出分隔符：
%%RECIPES%%

然后在下一行输出以下 JSON 格式的数据（只输出 JSON，不要加任何说明文字）：
{
  "recipes": [
    {
      "name": "菜名",
      "description": "简短描述",
      "difficulty": "简单/中等/困难",
      "cooking_time": "预估时间",
      "ingredients_needed": ["所需食材1", "所需食材2", ...],
      "steps": [
        {"step": 1, "description": "步骤描述"},
        {"step": 2, "description": "步骤描述"}
      ]
    }
  ],
  "ingredients": ["识别到的食材1", "食材2"]
}

注意：
- 自然语言回复是必须的，一定要先写完整的回复
- 如果没有任何菜品推荐，%%RECIPES%% 之后输出：{"recipes": [], "ingredients": []}
- recipes 不要超过 3 道菜
- ingredients 只在有识别到食材时返回
- %%RECIPES%% 分隔符必须单独占一行，前后不要有其他内容
- 只输出一次 %%RECIPES%%
"""


HISTORY_MAX = 20
MARKER = "%%RECIPES%%"


def _marker_prefix_len(text: str) -> int:
    """如果 text 的末尾是 MARKER 的前缀，返回前缀长度，否则返回 0。"""
    for i in range(len(MARKER) - 1, 0, -1):
        if text.endswith(MARKER[:i]):
            return i
    return 0


async def chat_with_ai(message: str, image_bytes: bytes = None, mime_type: str = None, history: list[dict] | None = None) -> dict:
    """与 AI 对话，支持文字、可选图片和对话历史。"""
    user_content = []

    if image_bytes:
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{image_base64}"
        user_content.append({"type": "image_url", "image_url": {"url": data_url}})
        user_content.append({"type": "text", "text": f"我上传了一张食材图片，请先告诉我你看到了什么食材，然后根据这些食材推荐菜品。我额外想说：{message}" if message else "我上传了一张食材图片，请先告诉我你看到了什么食材，然后根据这些食材推荐菜品。"})
    else:
        user_content = message

    messages = [{"role": "system", "content": CHAT_PROMPT}]

    # 插入对话历史（截断到最近 N 条，避免超出 token 限制）
    if history:
        recent = history[-HISTORY_MAX:]
        for h in recent:
            role = "assistant" if h.get("role") == "ai" else h.get("role", "user")
            messages.append({"role": role, "content": h.get("content", "")})

    messages.append({"role": "user", "content": user_content})

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            QWEN_API_URL,
            headers={
                "Authorization": f"Bearer {QWEN_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": QWEN_MODEL,
                "messages": messages,
                "max_tokens": 4096,
                "temperature": 0.8,
            },
        )
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"]
    return _parse_json_response(content)


async def chat_with_ai_stream(
    message: str,
    image_bytes: bytes = None,
    mime_type: str = None,
    history: list[dict] | None = None,
):
    """异步生成器，流式调用 Qwen API，逐块 yield (event_type, data)。"""
    # 构建 user content（与 chat_with_ai 相同逻辑）
    user_content = []
    if image_bytes:
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{image_base64}"
        user_content.append({"type": "image_url", "image_url": {"url": data_url}})
        user_content.append({"type": "text", "text": f"我上传了一张食材图片，请先告诉我你看到了什么食材，然后根据这些食材推荐菜品。我额外想说：{message}" if message else "我上传了一张食材图片，请先告诉我你看到了什么食材，然后根据这些食材推荐菜品。"})
    else:
        user_content = message

    messages = [{"role": "system", "content": CHAT_PROMPT}]
    if history:
        recent = history[-HISTORY_MAX:]
        for h in recent:
            role = "assistant" if h.get("role") == "ai" else h.get("role", "user")
            messages.append({"role": role, "content": h.get("content", "")})
    messages.append({"role": "user", "content": user_content})

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                QWEN_API_URL,
                headers={
                    "Authorization": f"Bearer {QWEN_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": QWEN_MODEL,
                    "messages": messages,
                    "max_tokens": 4096,
                    "temperature": 0.8,
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()

                full_text = ""
                yielded_until = 0
                marker_found_at = -1

                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    payload = line[6:]
                    if payload == "[DONE]":
                        break

                    try:
                        chunk = json.loads(payload)
                        delta = chunk["choices"][0].get("delta", {}).get("content", "")
                        if not delta:
                            continue
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue

                    full_text += delta

                    if marker_found_at >= 0:
                        continue  # 已过 marker，继续缓存

                    pos = full_text.find(MARKER)
                    if pos >= 0:
                        marker_found_at = pos
                        before_marker = full_text[yielded_until:pos]
                        if before_marker:
                            yield ("text", before_marker)
                        yielded_until = len(full_text)
                    else:
                        new_text = full_text[yielded_until:]
                        prefix_len = _marker_prefix_len(new_text)
                        if prefix_len > 0:
                            safe_text = new_text[:-prefix_len]
                            if safe_text:
                                yield ("text", safe_text)
                            yielded_until = len(full_text) - prefix_len
                        else:
                            if new_text:
                                yield ("text", new_text)
                            yielded_until = len(full_text)

                # 流结束 — 解析 structured data
                if marker_found_at >= 0:
                    json_str = full_text[marker_found_at + len(MARKER):].strip()
                    if json_str.startswith("```"):
                        lines = json_str.split("\n")
                        json_str = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
                    try:
                        data = json.loads(json_str)
                        yield ("recipes", {
                            "recipes": data.get("recipes", []),
                            "ingredients": data.get("ingredients", []),
                        })
                    except json.JSONDecodeError:
                        remaining = full_text[marker_found_at + len(MARKER):].strip()
                        if remaining:
                            yield ("text", remaining)
                else:
                    remaining = full_text[yielded_until:]
                    if remaining:
                        yield ("text", remaining)

                yield ("done", {})

    except httpx.HTTPStatusError as e:
        yield ("error", f"AI 服务请求失败 (HTTP {e.response.status_code})")
    except httpx.TimeoutException:
        yield ("error", "AI 响应超时，请重试")
    except Exception as e:
        yield ("error", f"AI 服务异常: {str(e)}")


def _parse_json_response(content: str) -> dict:
    """从 AI 返回的内容中解析 JSON。"""
    content = content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "ingredients": [],
            "recipes": [],
            "recommend_reason": "",
            "raw_response": content,
        }
