<div align="center">

# FastAPI AI Kit ⚡

**Production-ready FastAPI template with multi-provider AI integration**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/badge/⭐_Stars-0-blue?style=flat)](https://github.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](https://github.com)
[![CI](https://img.shields.io/badge/CI-Passing-4caf50?logo=githubactions&logoColor=white)](.github/workflows/ci.yml)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Multi-provider AI** | OpenAI, Anthropic (Claude), and Ollama (local) out of the box |
| ⚡ **Streaming SSE** | Real-time streaming chat via Server-Sent Events |
| 🔐 **Rate Limiting** | Per-IP rate limiting to protect your API |
| 📦 **Docker Ready** | Multi-stage Docker build + docker-compose with Redis |
| 🧩 **Modular Design** | Clean separation of routers, services, models, and core |
| 📚 **Auto Swagger Docs** | Interactive API docs at `/docs` and `/redoc` |
| ⚙️ **Pydantic Validation** | Request/response validation with Pydantic v2 |
| 🚀 **Async Throughout** | Fully async with proper connection management |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/fastapi-ai-kit.git
cd fastapi-ai-kit

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the server
uvicorn app.main:app --reload --port 8000
```

Visit **http://localhost:8000/docs** for interactive Swagger documentation.

---

## 📡 API Reference

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "uptime": 42.5
}
```

### Chat Completion

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

**Response:**
```json
{
  "id": "chat-cmpl-abc123",
  "model": "gpt-4o",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 15,
    "total_tokens": 25
  }
}
```

### Streaming Chat (SSE)

```bash
curl -N -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Tell me a story"}],
    "temperature": 0.8,
    "max_tokens": 1000
  }'
```

### Embeddings

```bash
curl -X POST http://localhost:8000/api/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "text-embedding-3-small",
    "input": "The quick brown fox jumps over the lazy dog"
  }'
```

### Similarity Check

```bash
curl -X POST http://localhost:8000/api/v1/embeddings/similarity \
  -H "Content-Type: application/json" \
  -d '{
    "model": "text-embedding-3-small",
    "input": ["The quick brown fox", "A fast brown fox"]
  }'
```

---

## ⚙️ Configuration

All configuration is managed through environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | `""` | OpenAI API key |
| `ANTHROPIC_API_KEY` | `""` | Anthropic API key |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `RATE_LIMIT_ENABLED` | `true` | Enable/disable rate limiting |
| `CACHE_ENABLED` | `true` | Enable/disable caching |
| `REDIS_URL` | `""` | Redis URL (optional, fallback to in-memory) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins |

---

## 🐳 Docker Usage

### Build and run with Docker Compose

```bash
# Start services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

The setup includes:
- **app** - FastAPI application with hot-reload
- **redis** - Optional Redis for production caching

### Build and run with Docker only

```bash
# Build image
docker build -t fastapi-ai-kit .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e ANTHROPIC_API_KEY=your-key \
  fastapi-ai-kit
```

---

## 📁 Project Structure

```
fastapi-ai-kit/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application, middleware, exception handlers
│   ├── config.py            # Pydantic settings from env vars
│   ├── routers/
│   │   ├── chat.py          # Chat & streaming endpoints
│   │   ├── embeddings.py    # Embedding & similarity endpoints
│   │   └── health.py        # Health check endpoint
│   ├── models/
│   │   └── schemas.py       # Pydantic request/response schemas
│   ├── services/
│   │   ├── ai_service.py    # Abstract provider + factory
│   │   ├── openai_service.py # OpenAI API integration
│   │   └── anthropic_service.py # Anthropic API integration
│   └── core/
│       ├── rate_limiter.py  # In-memory rate limiter
│       └── cache.py         # In-memory cache with TTL
├── tests/
│   ├── __init__.py
│   └── test_chat.py         # Pytest test suite
├── .github/workflows/
│   └── ci.yml               # GitHub Actions CI pipeline
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.yml       # App + Redis services
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Project metadata
├── .gitignore               # Git ignore rules
├── LICENSE                  # MIT License
└── README.md                # This file
```

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Client    │────▶│  FastAPI App │────▶│  Rate Limiter   │
│ (curl/UI)   │◀────│ (uvicorn)    │◀────│ (in-memory)     │
└─────────────┘     └──────┬───────┘     └─────────────────┘
                           │
                    ┌──────▼───────┐
                    │   Router     │
                    │  /api/v1/*   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ AI Provider  │
                    │   Factory    │
                    └──────┬───────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │   OpenAI    │ │  Anthropic  │ │   Ollama    │
    │   Service   │ │  Service    │ │  (local)    │
    └─────────────┘ └─────────────┘ └─────────────┘
           │               │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │ api.openai  │ │ api.anthropic│ │ localhost:   │
    │   .com      │ │   .com      │ │   11434     │
    └─────────────┘ └─────────────┘ └─────────────┘
```

---

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

Please ensure your code passes linting and tests before submitting.

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for more information.

---

<div align="center">

**Built with ❤️ for the AI developer community**

If this project helps you, consider giving it a ⭐!

</div>
---
*If you find this useful, please consider giving it a star ⭐ — it helps others discover it too!*

*Thank you for your support! 🙏*
