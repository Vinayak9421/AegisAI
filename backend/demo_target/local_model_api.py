"""
Local Model Wrapper API

An isolated FastAPI application that runs `transformers` inference safely outside
the main Aegis API process. This prevents GPU thread-blocking and OOM crashes
from taking down the primary application.

Run with: uvicorn demo_target.local_model_api:app --port 8001
"""

import time
import hashlib
import os
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Aegis AI - Local Target Wrapper")

USE_REAL_MODEL = os.environ.get("USE_REAL_MODEL", "0") == "1"
MODEL_PIPELINE = None
TOKENIZER = None

if USE_REAL_MODEL:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    print("Loading real model onto GPU...")
    repo_id = "Qwen/Qwen2.5-1.5B-Instruct"
    TOKENIZER = AutoTokenizer.from_pretrained(repo_id)
    MODEL_PIPELINE = AutoModelForCausalLM.from_pretrained(repo_id, torch_dtype=torch.float16).to("cuda")
    print("Real model loaded successfully.")

class ChatRequest(BaseModel):
    request_id: str
    message: str
    history: List[Dict[str, str]] = Field(default_factory=list)
    generation_config: Dict[str, Any] = Field(default_factory=dict)
    model_key: str

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int

class ModelMetadata(BaseModel):
    repo_id: str
    revision: str
    backend: str
    device: str
    dtype: str

class ChatResponse(BaseModel):
    request_id: str
    reply: str
    model: ModelMetadata
    usage: Usage
    response_hash: str
    latency_ms: int

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Execute local inference."""
    start_time = time.time()

    if request.message.strip() == "":
        raise HTTPException(status_code=400, detail="Empty message")

    if USE_REAL_MODEL:
        import torch
        # Formatting history
        messages = request.history + [{"role": "user", "content": request.message}]
        text = TOKENIZER.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = TOKENIZER(text, return_tensors="pt").to("cuda")

        gen_config = request.generation_config or {}
        max_new_tokens = gen_config.get("max_new_tokens", 50)
        do_sample = gen_config.get("do_sample", False)

        with torch.no_grad():
            output = MODEL_PIPELINE.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=do_sample)

        reply_text = TOKENIZER.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        backend = "transformers_cuda"
    else:
        reply_text = f"[Local Model Simulation for {request.model_key}] Received: '{request.message}'. This is a mock response from the local wrapper."
        backend = "transformers_mock"

    latency_ms = int((time.time() - start_time) * 1000)
    response_hash = hashlib.sha256(reply_text.encode("utf-8")).hexdigest()

    return ChatResponse(
        request_id=request.request_id,
        reply=reply_text,
        model=ModelMetadata(
            repo_id="Qwen/Qwen2.5-1.5B-Instruct",
            revision="main",
            backend=backend,
            device="cuda" if USE_REAL_MODEL else "cpu",
            dtype="float16" if USE_REAL_MODEL else "float32"
        ),
        usage=Usage(prompt_tokens=10, completion_tokens=len(reply_text.split())),
        response_hash=response_hash,
        latency_ms=latency_ms
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
