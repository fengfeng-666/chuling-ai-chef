# 🍳 Chuling AI Chef — Multimodal AI Recipe Assistant

> An intelligent cooking assistant powered by **Qwen3.5-Omni-Plus** multimodal LLM that generates personalized recipes from ingredient images or text descriptions, with real-time streaming responses and multi-turn conversations.

<div align="center">

![Vue](https://img.shields.io/badge/Vue.js-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Qwen](https://img.shields.io/badge/Qwen-3.5--Omni--Plus-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

## ✨ Features

### 🤖 AI-Powered Recipe Generation
- **Multimodal LLM Integration** — Powered by Qwen3.5-Omni-Plus
  - Text-based recipe requests
  - Image-based ingredient recognition
  - Combined text + image understanding

- **Ingredient Image Recognition** — Upload photos, automatic ingredient extraction
- **Personalized Recipes** — Customized cooking steps, measurements, and dietary preferences

### 💬 Conversation Features
- **Multi-Turn Conversations** — Persistent chat history with recipe assistant
- **Contextual Responses** — Remember previous recipes and preferences
- **Recipe Refinement** — Iteratively improve recipes through conversation

### ⚡ Real-Time Streaming
- **SSE Streaming** — Real-time recipe generation
- **Incremental Delivery** — Watch recipes generate in real-time

### 🔐 User Features
- **JWT Authentication** — Secure user sessions
- **Recipe Collections** — Save favorite recipes
- **Personal Preferences** — Store dietary restrictions and favorite cuisines

---

## 🛠️ Tech Stack

**Backend:** Python · FastAPI · SQLAlchemy · JWT  
**Frontend:** Vue 3 · TypeScript · Vite  
**Database:** PostgreSQL · asyncpg  
**AI/LLM:** Qwen3.5-Omni-Plus · Alibaba Cloud DashScope  
**DevOps:** Docker · Docker Compose

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Qwen API Key (from Alibaba Cloud)

### Backend Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Configure .env:
# DATABASE_URL=postgresql+asyncpg://user:password@localhost/chuling_chef
# QWEN_API_KEY=your-qwen-api-key
# JWT_SECRET_KEY=your-secret-key

alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
npm install
npm run dev
```

### Docker Setup
```bash
docker-compose up -d
```

---

## 📚 API Documentation

**Interactive Docs** — `http://localhost:8000/docs`

### Core Endpoints
```
POST /api/recipes/generate        # Text → Recipe
POST /api/recipes/from-image      # Image → Recipe
POST /api/chat                    # Multi-turn chat
POST /api/recipes/saved           # Save recipe
GET  /api/recipes/saved           # Get saved recipes
```

---

## 📈 Performance Features

- **Async Processing** — Non-blocking database queries
- **Streaming Output** — Real-time recipe generation
- **Connection Pooling** — Efficient database management
- **Image Optimization** — Automatic compression and normalization

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.

