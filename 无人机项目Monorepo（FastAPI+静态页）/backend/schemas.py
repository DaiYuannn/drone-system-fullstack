from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class PlanningRequest(BaseModel):
    start: List[float] = Field(min_length=3, max_length=3)
    end: List[float] = Field(min_length=3, max_length=3)
    obstacles: Optional[List[List[float]]] = None


class PathPoint(BaseModel):
    x: float
    y: float
    z: float
    t: float
    spd: float


class PlanningResponse(BaseModel):
    path: List[PathPoint]
    cost: Optional[float] = None


class WsTelemetry(BaseModel):
    type: Literal["telemetry"] = "telemetry"
    pose: dict
    battery: float
    link: dict
    alerts: List[str] = []


class WsPathUpdate(BaseModel):
    type: Literal["path.update"]
    points: List[List[float]]
