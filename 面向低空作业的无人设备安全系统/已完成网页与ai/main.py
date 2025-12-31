from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi_poe import get_bot_response, ProtocolMessage
import json
import os

app = FastAPI()

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str


def get_poe_api_key() -> str:
    api_key = os.getenv("POE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail=(
                "服务端未配置 POE_API_KEY 环境变量。"
                "请先设置后重启服务。"
            ),
        )
    return api_key

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    api_key = get_poe_api_key()
    messages = [ProtocolMessage(role="user", content=request.message)]
    full_response = []
    
    try:
        async for partial in get_bot_response(
            messages=messages,
            bot_name="GPT-3.5-Turbo",
            api_key=api_key
        ):
            if partial.raw_response:
                raw_text = json.loads(partial.raw_response.get("text", "{}"))
                if "text" in raw_text:
                    full_response.append(raw_text["text"])
        return {"reply": "".join(full_response)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))