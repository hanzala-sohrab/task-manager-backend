from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import ollama
import json
from app.config import settings
from app.auth import get_current_user

router = APIRouter()


# Pydantic models for requests and responses
class ChatMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    stream: bool = False
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None


class CompletionRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None


class LLMResponse(BaseModel):
    content: str
    model: str
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    eval_count: Optional[int] = None


class ModelInfo(BaseModel):
    name: str
    size: int
    digest: str
    modified_at: str


@router.get("/models", response_model=List[ModelInfo])
async def list_models(current_user: dict = Depends(get_current_user)):
    """List available Ollama models"""
    try:
        response = ollama.list()

        # Handle the ListResponse object - access models attribute directly
        if hasattr(response, "models"):
            models_data = response.models
        elif isinstance(response, list):
            models_data = response
        elif isinstance(response, dict) and "models" in response:
            models_data = response["models"]
        else:
            models_data = []

        models_list = []
        for model in models_data:
            # Handle the actual Model object structure
            name = model.model
            size = model.size
            digest = model.digest
            modified_at = model.modified_at.isoformat() if model.modified_at else ""

            models_list.append(
                ModelInfo(
                    name=name,
                    size=size,
                    digest=digest,
                    modified_at=modified_at,
                )
            )

        return models_list

    except Exception as e:
        print(f"Error listing models: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@router.post("/chat", response_model=LLMResponse)
async def chat_completion(
    request: ChatRequest, current_user: dict = Depends(get_current_user)
):
    """Chat completion endpoint using Ollama"""
    try:
        model = request.model or settings.ollama_model

        # Convert messages to ollama format
        messages = [
            {"role": msg.role, "content": msg.content} for msg in request.messages
        ]

        if request.stream:

            def stream_chat():
                try:
                    for chunk in ollama.chat(
                        model=model,
                        messages=messages,
                        stream=True,
                        options=(
                            {
                                "temperature": request.temperature,
                                "num_predict": request.max_tokens,
                            }
                            if request.max_tokens
                            else {"temperature": request.temperature}
                        ),
                    ):
                        # Extract the serializable data from the ChatResponse object
                        chunk_data = {
                            "message": {
                                "role": chunk.get("message", {}).get(
                                    "role", "assistant"
                                ),
                                "content": chunk.get("message", {}).get("content", ""),
                            },
                            "model": chunk.get("model", model),
                            "done": chunk.get("done", False),
                        }

                        # Add timing info if available
                        if "total_duration" in chunk:
                            chunk_data["total_duration"] = chunk["total_duration"]
                        if "load_duration" in chunk:
                            chunk_data["load_duration"] = chunk["load_duration"]
                        if "prompt_eval_count" in chunk:
                            chunk_data["prompt_eval_count"] = chunk["prompt_eval_count"]
                        if "eval_count" in chunk:
                            chunk_data["eval_count"] = chunk["eval_count"]

                        yield f"data: {json.dumps(chunk_data)}\n\n"

                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
                finally:
                    yield "data: [DONE]\n\n"

            return StreamingResponse(
                stream_chat(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/plain; charset=utf-8",
                },
            )

        response = ollama.chat(
            model=model,
            messages=messages,
            stream=False,
            options=(
                {
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens,
                }
                if request.max_tokens
                else {"temperature": request.temperature}
            ),
        )

        return LLMResponse(
            content=response["message"]["content"],
            model=response["model"],
            total_duration=response.get("total_duration"),
            load_duration=response.get("load_duration"),
            prompt_eval_count=response.get("prompt_eval_count"),
            eval_count=response.get("eval_count"),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat completion failed: {str(e)}")


@router.post("/completion", response_model=LLMResponse)
async def text_completion(
    request: CompletionRequest, current_user: dict = Depends(get_current_user)
):
    """Text completion endpoint using Ollama"""
    try:
        model = request.model or settings.ollama_model

        response = ollama.generate(
            model=model,
            prompt=request.prompt,
            options=(
                {
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens,
                }
                if request.max_tokens
                else {"temperature": request.temperature}
            ),
        )

        return LLMResponse(
            content=response["response"],
            model=response["model"],
            total_duration=response.get("total_duration"),
            load_duration=response.get("load_duration"),
            prompt_eval_count=response.get("prompt_eval_count"),
            eval_count=response.get("eval_count"),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text completion failed: {str(e)}")


@router.post("/pull/{model_name}")
async def pull_model(model_name: str, current_user: dict = Depends(get_current_user)):
    """Pull a model from Ollama registry"""
    try:
        ollama.pull(model_name)
        return {"message": f"Model {model_name} pulled successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pull model: {str(e)}")


@router.delete("/models/{model_name}")
async def delete_model(model_name: str, current_user: dict = Depends(get_current_user)):
    """Delete a model from Ollama"""
    try:
        ollama.delete(model_name)
        return {"message": f"Model {model_name} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete model: {str(e)}")
