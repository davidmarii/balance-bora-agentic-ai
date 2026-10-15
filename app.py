from contextlib import AsyncExitStack, asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from balance_bora_agent import (
    agent,
    nutrient_server,
    price_server,
    assessment_server,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="Balance Bora Agent API",
    description="Feed nutrient, price and livestock advisory tools.",
    version="1.0.0",
    lifespan=lifespan,
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=3, max_length=2000)


@app.get("/")
async def home():
    return {
        "name": "Balance Bora Agent API",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        result = await agent.run(request.message)
        return {"reply": str(result.output)}
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="The advisory agent could not process this request. "
                   "Check model configuration and MCP server logs.",
        ) from exc
