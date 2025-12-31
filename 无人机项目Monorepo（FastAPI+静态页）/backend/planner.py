from typing import List
from schemas import PlanningRequest, PlanningResponse, PathPoint


def straight_line_planner(req: PlanningRequest, steps: int = 20) -> PlanningResponse:
    sx, sy, sz = req.start
    ex, ey, ez = req.end
    path: List[PathPoint] = []
    for i in range(steps + 1):
        u = i / steps
        x = sx + (ex - sx) * u
        y = sy + (ey - sy) * u
        z = sz + (ez - sz) * u
        t = u  # normalized time
        spd = 1.0
        path.append(PathPoint(x=x, y=y, z=z, t=t, spd=spd))
    return PlanningResponse(path=path, cost=float(steps))
