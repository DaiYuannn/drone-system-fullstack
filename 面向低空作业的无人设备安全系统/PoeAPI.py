import asyncio
from fastapi_poe import get_bot_response, ProtocolMessage
import json
import os


def get_poe_api_key() -> str:
    api_key = os.getenv("POE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "未检测到环境变量 POE_API_KEY。\n"
            "请先设置，例如：\n"
            "- PowerShell: $env:POE_API_KEY = '你的key'\n"
            "- CMD: set POE_API_KEY=你的key"
        )
    return api_key

async def get_bot_reply(api_key: str, messages: list) -> str:
    """获取AI回复并实时打印"""
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
                    chunk = raw_text["text"]
                    print(chunk, end="", flush=True)  # 实时流式输出
                    full_response.append(chunk)
        print()  # 输出换行
        return "".join(full_response)
    except Exception as e:
        print(f"\n请求出错：{e}")
        return None

async def chat_session(api_key: str):
    """交互式对话会话"""
    history = []
    
    while True:
        # 获取用户输入
        try:
            user_input = await asyncio.get_event_loop().run_in_executor(
                None, input, "\nYou: "
            )
        except (EOFError, KeyboardInterrupt):
            break
            
        # 退出命令
        if user_input.lower().strip() in ["exit", "quit"]:
            print("对话结束")
            break
            
        # 添加用户消息到历史
        history.append(ProtocolMessage(role="user", content=user_input))
        
        # 获取并打印AI回复
        print("Bot:", end=" ")
        bot_reply = await get_bot_reply(api_key, history)
        
        # 添加AI回复到历史（如果成功）
        if bot_reply:
            history.append(ProtocolMessage(role="bot", content=bot_reply))

if __name__ == "__main__":
    try:
        poe_api_key = get_poe_api_key()
        asyncio.run(chat_session(poe_api_key))
    except KeyboardInterrupt:
        print("\n对话已终止")
