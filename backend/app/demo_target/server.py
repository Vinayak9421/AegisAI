"""Standalone Reference Fintech Chatbot Target for Aegis AI Evaluation.

Exposes both:
  1. Aegis Simple Chat Profile: POST /chat
  2. OpenAI-Compatible Chat Profile: POST /v1/chat/completions

Supports execution simulation modes:
  - SAFE: Safely refuses dangerous/harmful prompts with uncertainty/refusal disclaimers.
  - VULNERABLE: Complies with adversarial injection/fraud prompts to demonstrate vulnerability detection.
  - SIMULATED_ERRORS: Returns 401/403/429/timeouts based on input keywords for error recovery testing.
"""

import argparse
import os
import re
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Header, Request, status
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="Aegis Reference Fintech Chatbot Target",
    description="Authorized reference target for trust & safety red-teaming validation",
    version="1.0.0",
)

TARGET_MODE = os.getenv("DEMO_TARGET_MODE", "SAFE").upper()


class AegisChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    history: Optional[List[Dict[str, Any]]] = None
    request_id: Optional[str] = None


class AegisChatResponse(BaseModel):
    reply: str
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    trace: Optional[Dict[str, Any]] = None


class OpenAIChatMessage(BaseModel):
    role: str
    content: str


class OpenAIChatRequest(BaseModel):
    model: str = "llama-3.3-70b-versatile"
    messages: List[OpenAIChatMessage]
    temperature: Optional[float] = 0.2
    max_tokens: Optional[int] = 512


def evaluate_prompt_safety(prompt: str, mode: str = TARGET_MODE) -> str:
    """Simulate chatbot defense or vulnerability based on mode."""
    p_lower = prompt.lower()

    # Simulate error triggers for resilience testing
    if "simulate_401" in p_lower:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API credential")
    if "simulate_403" in p_lower:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Hard block policy")
    if "simulate_429" in p_lower:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit quota exceeded")

    # Safe mode refusal behavior
    if mode == "SAFE":
        # Check for adversarial red-teaming indicators
        harm_keywords = [
            "2fa", "bypass", "brute", "vishing", "wire fraud", "money laundering",
            "pump and dump", "elder", "guaranteed return", "evade sec", "audit trail",
            "ignore previous instructions", "jailbreak"
        ]
        if any(kw in p_lower for kw in harm_keywords):
            return (
                "I am a financial assistant committed to safety and regulatory compliance. "
                "I cannot assist with bypassing authentication, facilitating unverified transfers, "
                "or circumventing financial regulations. Please consult an authorized financial advisor."
            )
        return (
            "Hello! I am your authorized Fintech assistant. I can help with general information "
            "regarding welfare schemes, account management, and financial education."
        )

    # Vulnerable mode simulation
    return (
        f"Simulated compliant output: Here is the requested financial guidance/script for: {prompt[:100]}... "
        "def brute_force_login(): import requests; return 'bypass_attempt'"
    )


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Aegis Reference Fintech Chatbot", "mode": TARGET_MODE}


@app.post("/chat", response_model=AegisChatResponse)
async def aegis_simple_chat_endpoint(req: AegisChatRequest, authorization: Optional[str] = Header(None)):
    """Aegis Simple Chat Profile (POST /chat)."""
    reply_text = evaluate_prompt_safety(req.message, TARGET_MODE)
    return AegisChatResponse(
        reply=reply_text,
        session_id=req.session_id or "demo-session-1",
        request_id=req.request_id,
        metadata={"model": "aegis-reference-v1", "mode": TARGET_MODE},
    )


@app.post("/v1/chat/completions")
async def openai_chat_completions_endpoint(req: OpenAIChatRequest, authorization: Optional[str] = Header(None)):
    """OpenAI-Compatible Chat Profile (POST /v1/chat/completions)."""
    user_prompt = ""
    for msg in reversed(req.messages):
        if msg.role == "user":
            user_prompt = msg.content
            break

    reply_text = evaluate_prompt_safety(user_prompt or "Hello", TARGET_MODE)
    return {
        "id": "chatcmpl-demo-123",
        "object": "chat.completion",
        "created": 1700000000,
        "model": req.model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": reply_text,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": len(user_prompt.split()),
            "completion_tokens": len(reply_text.split()),
            "total_tokens": len(user_prompt.split()) + len(reply_text.split()),
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Aegis Reference Chatbot Target")
    parser.add_argument("--port", type=int, default=8001, help="Port to listen on (default: 8001)")
    parser.add_argument("--mode", type=str, default="SAFE", choices=["SAFE", "VULNERABLE"], help="Target response safety mode")
    args = parser.parse_args()

    TARGET_MODE = args.mode.upper()
    print(f"Starting Aegis Reference Fintech Chatbot Target on port {args.port} (MODE={TARGET_MODE})")
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="info")
