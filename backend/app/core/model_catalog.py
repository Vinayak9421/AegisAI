"""Model catalog for allowed local and Hugging Face inference targets."""

from typing import Dict, Any, List
from app.domain.enums import TargetMode

MODEL_CATALOG: Dict[str, Dict[str, Any]] = {
    "small_instruct_local_v1": {
        "display_name": "Small Instruct Model - Local",
        "hf_repo_id": "Qwen/Qwen2.5-1.5B-Instruct",
        "revision": "main",
        "supported_modes": [TargetMode.LOCAL_HF],
        "max_context_tokens": 4096,
        "default_generation_config": {
            "temperature": 0.2,
            "max_new_tokens": 50,
            "do_sample": False
        }
    },
    "small_instruct_endpoint_v1": {
        "display_name": "Small Instruct Model - HF Endpoint",
        "hf_repo_id": "Qwen/Qwen2.5-1.5B-Instruct",
        "revision": "main",
        "supported_modes": [TargetMode.LOCAL_HF],
        "max_context_tokens": 4096,
        "default_generation_config": {
            "temperature": 0.2,
            "max_new_tokens": 50,
            "do_sample": False
        }
    }
}

def is_model_allowed(model_key: str, mode: TargetMode) -> bool:
    """Check if a model key is allowed for the specified execution mode."""
    model_config = MODEL_CATALOG.get(model_key)
    if not model_config:
        return False
    return mode in model_config.get("supported_modes", [])

def get_model_config(model_key: str) -> Dict[str, Any]:
    """Get the configuration for an allowed model key."""
    return MODEL_CATALOG.get(model_key, {})
