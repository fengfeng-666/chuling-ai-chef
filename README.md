# 厨灵 — AI 智能菜谱推荐系统

基于通义千问 (Qwen3.5-Omni-Plus) 的 AI 菜谱助手。拍个食材照片或说句话，自动生成菜谱和步骤。

## 功能

- AI 对话式菜谱推荐，支持流式输出
- 拍照识别食材，自动匹配菜谱
- 菜谱收藏、烹饪步骤勾选
- 用户注册/登录，聊天记录持久化
- Markdown 渲染、消息复制/重新生成
- 单容器 Docker 部署

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 (Composition API) + Vite + Vue Router |
| 后端 | FastAPI (Python 3.12) |
| AI | 通义千问 Qwen3.5-Omni-Plus (DashScope API) |
| 数据库 | SQLite (开发/简配) / PostgreSQL (生产) |
| 部署 | Docker + Docker Compose |

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/fengfeng-666/-AI-.git
cd -AI-
```

### 2. 配置环境变量

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env`，填入你的 API 密钥：

```ini
QWEN_API_KEY=sk-你的阿里云百炼API密钥
QWEN_MODEL=qwen3.5-omni-plus
CHULING_SECRET=随便写一段随机字符串（至少32位）
```

> QWEN_API_KEY 在 [阿里云百炼控制台](https://bailian.console.aliyun.com/) 获取

### 3. 安装依赖

**后端：**

```bash
cd backend
pip install -r requirements.txt
```

**前端：**

```bash
cd frontend
npm install
```

### 4. 启动开发环境

**后端**（终端 1）：

```bash
cd backend
python main.py
# 运行在 http://localhost:8000
```

**前端**（终端 2）：

```bash
cd frontend
npm run dev
# 运行在 http://localhost:5173
```

打开浏览器访问 `http://localhost:5173`。

### 5. Docker 部署

```bash
docker compose -f docker-compose.simple.yml up -d --build
# 访问 http://localhost:8000
```

## 项目结构

```
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 环境变量配置
│   ├── database.py          # 数据库连接
│   ├── auth.py              # JWT 认证
│   ├── middleware.py         # 限流 & 日志中间件
│   ├── models.py            # SQLAlchemy 模型
│   ├── routers/
│   │   ├── recipe.py        # 菜谱 & 聊天 API
│   │   ├── auth_router.py   # 注册/登录 API
│   │   └── sessions_router.py  # 会话管理 API
│   └── services/
│       └── ai_service.py    # Qwen API 调用 & SSE 流式
├── frontend/
│   └── src/
│       ├── views/           # 页面组件
│       ├── components/      # UI 组件
│       ├── composables/     # 组合式函数
│       └── api/             # API 请求封装
├── deploy/
│   ├── Dockerfile.simple    # 单容器构建
│   ├── Dockerfile           # 多容器构建 (PostgreSQL+Nginx)
│   └── docker-compose.yml   # 多容器编排
├── docker-compose.simple.yml  # 单容器编排
└── .dockerignore
```

## API 概览

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/register` | 用户注册 |
| POST | `/api/login` | 用户登录 |
| GET | `/api/me` | 获取当前用户 |
| GET | `/api/sessions` | 聊天会话列表 |
| POST | `/api/sessions` | 创建新会话 |
| DELETE | `/api/sessions/{id}` | 删除会话 |
| GET | `/api/sessions/{id}/messages` | 获取会话消息 |
| POST | `/api/chat/stream` | SSE 流式聊天（支持图片） |
| GET | `/api/health` | 健康检查 |

## License

MIT
