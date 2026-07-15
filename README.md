<div align="center">

# FastAPI AI Kit ⚡

**The FastAPI Agent Backend — multi-provider AI, MCP SSE, agent execution, session memory, and tool registry in one template**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/badge/⭐_Stars-1-blue?style=flat)](https://github.com/FreeAutomation-Tech/fastapi-ai-kit)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![CI](https://img.shields.io/badge/CI-Passing-4caf50?logo=githubactions&logoColor=white)](.github/workflows/ci.yml)

</div>

---

## ✨ Why FastAPI AI Kit?

Every AI agent needs a backend — chat completion, streaming, memory, tools, and the Model Context Protocol (MCP). This template gives you **all of it** in one production-ready FastAPI application. No more cobbling together separate services.

| Feature | Description |
|---------|-------------|
| 🤖 **Multi-provider AI** | OpenAI, Anthropic (Claude), and Ollama (local) out of the box |
| ⚡ **Streaming SSE** | Real-time streaming chat via Server-Sent Events |
| 🧠 **Session Memory** | Per-session conversation history with auto-expiry |
| 🔧 **Tool Registry** | Extensible tool system with calculator, web search, file reader |
| 🤖 **Agent Execution** | ReAct-style agent with tool-calling loop |
| 🔌 **MCP SSE Endpoint** | Model Context Protocol server for MCP-compatible clients |
| 🔐 **API Key Auth** | Optional bearer token authentication |
| 📦 **Docker Ready** | Multi-stage Docker build + docker-compose with Redis |
| 📚 **Auto Swagger Docs** | Interactive API docs at `/docs` and `/redoc` |

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/FreeAutomation-Tech/fastapi-ai-kit.git
cd fastapi-ai-kit

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env   # Add your API keys

# Run
uvicorn app.main:app --reload --port 8000
```

Visit **http://localhost:8000/docs** for interactive docs.

---

## 📡 API Reference

### Core AI Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/chat` | Chat completion |
| `POST` | `/api/v1/chat/stream` | Streaming chat (SSE) |
| `POST` | `/api/v1/embeddings` | Generate embeddings |
| `POST` | `/api/v1/embeddings/similarity` | Cosine similarity |

### Agent Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/agents/execute` | Execute agent with tool-calling loop |
| `POST` | `/api/v1/agents/stream` | Stream agent execution |

### Session Management

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/sessions` | Create a session |
| `GET` | `/api/v1/sessions` | List all sessions |
| `GET` | `/api/v1/sessions/{id}` | Get session details |
| `GET` | `/api/v1/sessions/{id}/messages` | Get session messages |
| `DELETE` | `/api/v1/sessions/{id}` | Delete a session |

### Tool & MCP Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/tools` | List registered tools |
| `GET` | `/api/v1/mcp/sse` | MCP SSE endpoint (server-sent events) |
| `POST` | `/api/v1/mcp/message` | MCP message endpoint (JSON-RPC) |

---

## 🧠 Agent Execution

The agent uses a ReAct pattern: it receives your message, decides whether to call a tool, executes it, and continues until it has a final answer.

```bash
# Create a session first
curl -X POST http://localhost:8000/api/v1/sessions

# Execute an agent
curl -X POST http://localhost:8000/api/v1/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "message": "What is 235 * 47?",
    "model": "gpt-4o"
  }'
```

### Available Tools

| Tool | Description |
|------|-------------|
| `calculator` | Evaluate mathematical expressions |
| `web_search` | Search the web for current information |
| `file_reader` | Read files from the workspace directory |

---

## 🔌 MCP Protocol

The MCP (Model Context Protocol) endpoint allows any MCP-compatible client to discover and call tools:

```bash
# Connect to SSE stream
curl -N http://localhost:8000/api/v1/mcp/sse

# Send JSON-RPC message (client_id from SSE endpoint event)
curl -X POST "http://localhost:8000/api/v1/mcp/message?client_id=abc123" \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list", "id": "1"}'
```

---

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | `""` | OpenAI API key |
| `ANTHROPIC_API_KEY` | `""` | Anthropic API key |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `API_KEY` | `""` | API key for auth (empty = disabled) |
| `DEFAULT_PROVIDER` | `openai` | Default AI provider |
| `AGENT_MAX_ITERATIONS` | `5` | Max tool-calling loops |
| `SESSION_TTL` | `3600` | Session expiry in seconds |
| `WORKSPACE_DIR` | `.` | Allowed directory for file_reader tool |
| `RATE_LIMIT_ENABLED` | `true` | Enable/disable rate limiting |
| `CACHE_ENABLED` | `true` | Enable/disable caching |
| `REDIS_URL` | `""` | Redis URL (optional) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins |

---

## 🐳 Docker

```bash
docker-compose up --build
```

---

## 📁 Project Structure

```
fastapi-ai-kit/
├── app/
│   ├── main.py                 # FastAPI app, middleware, lifespan
│   ├── config.py               # Pydantic settings
│   ├── routers/
│   │   ├── chat.py             # Chat & streaming
│   │   ├── embeddings.py       # Embeddings & similarity
│   │   ├── health.py           # Health check
│   │   ├── agents.py           # Agent execution & streaming
│   │   ├── sessions.py         # Session CRUD
│   │   ├── tools.py            # Tool registry listing
│   │   └── mcp.py              # MCP SSE + JSON-RPC
│   ├── models/
│   │   └── schemas.py          # All Pydantic models
│   ├── services/
│   │   ├── ai_service.py       # Abstract provider + factory
│   │   ├── openai_service.py   # OpenAI integration
│   │   └── anthropic_service.py# Anthropic integration
│   ├── agents/
│   │   ├── registry.py         # Tool registry
│   │   ├── executor.py         # ReAct agent executor
│   │   └── tools/
│   │       ├── base.py         # Abstract tool base
│   │       ├── calculator.py   # Math expression evaluator
│   │       ├── web_search.py   # Web search
│   │       └── file_reader.py  # Safe file reader
│   ├── memory/
│   │   └── store.py            # In-memory session store
│   └── core/
│       ├── auth.py             # API key auth
│       ├── rate_limiter.py     # Rate limiting
│       └── cache.py            # Response caching
├── tests/
│   └── test_chat.py            # 20+ tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── pyproject.toml
```

---

## 🧪 Testing

```bash
pip install pytest httpx
pytest tests/ -v
```

---

## 🔗 Ecosystem

This is part of the **FreeAutomation-Tech** ecosystem:

| Repo | Description |
|------|-------------|
| [agent-memory-kit](https://github.com/FreeAutomation-Tech/agent-memory-kit) | Memory patterns for AI agents (sliding-window, RAG, episodic) |
| [agent-security-kit](https://github.com/FreeAutomation-Tech/agent-security-kit) | Security toolkit for AI agents (guardrails, audit, MCP auth) |
| [agent-skill-kit](https://github.com/FreeAutomation-Tech/agent-skill-kit) | SKILL.md agent skill definitions |
| [awesome-mcp-servers](https://github.com/FreeAutomation-Tech/awesome-mcp-servers) | Curated MCP server collection |
| [claude-prompt-kit](https://github.com/FreeAutomation-Tech/claude-prompt-kit) | Prompt engineering toolkit |
| **fastapi-ai-kit** | **You are here** |

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

**Built with ❤️ for the AI agent community**

If this project helps you, consider giving it a ⭐!

</div>

---

*If you find this useful, please consider giving it a star ⭐ — it helps others discover it too!*

*Thank you for your support! 🙏*
