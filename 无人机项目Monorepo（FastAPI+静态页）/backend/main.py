from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import List
from schemas import PlanningRequest, PlanningResponse, WsPathUpdate, WsTelemetry
from planner import straight_line_planner

app = FastAPI(title="UAV Backend", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/planning", response_model=PlanningResponse)
def api_planning(req: PlanningRequest):
    try:
        return straight_line_planner(req)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_json()
            # Echo back basic telemetry or path.update ack
            if isinstance(data, dict) and data.get("type") == "path.update":
                msg = {"type": "ack", "event": "path.update", "count": len(data.get("points", []))}
                await ws.send_json(msg)
            else:
                await ws.send_json({"type": "echo", "data": data})
    except WebSocketDisconnect:
        pass
