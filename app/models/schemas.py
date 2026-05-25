from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[Message] = Field(min_length=1)
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=500, ge=1, le=128000)
    stream: bool = False


class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    id: str
    model: str
    choices: list[Choice]
    usage: Usage


class EmbeddingRequest(BaseModel):
    model: str
    input: str | list[str]


class EmbeddingResponse(BaseModel):
    model: str
    embeddings: list[list[float]]
    usage: Usage


class SimilarityRequest(BaseModel):
    model: str
    input: list[str] = Field(min_length=2)


class SimilarityResponse(BaseModel):
    similarity: float
    embeddings: list[list[float]]


class HealthResponse(BaseModel):
    status: str
    version: str
    uptime: float
