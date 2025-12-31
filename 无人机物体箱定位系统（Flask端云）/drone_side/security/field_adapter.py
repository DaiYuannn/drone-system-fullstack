"""
字段级隐私/兼容性适配

职责：
- 将本地字段转换为服务端数据库所需格式（例如将 bbox 元组拆分为 bbox_x1..bbox_y2）
- 预留轻量隐私处理（如字段脱敏/哈希等），默认直通
"""
from __future__ import annotations

from typing import Any, Dict, Tuple


def _split_bbox(payload: Dict[str, Any]) -> Dict[str, Any]:
    """将 bbox:(x1,y1,x2,y2) 拆分为独立字段，便于服务器入库。"""
    bbox = payload.get("bbox")
    if isinstance(bbox, (list, tuple)) and len(bbox) == 4:
        try:
            x1, y1, x2, y2 = bbox  # type: ignore
            payload["bbox_x1"] = int(x1)
            payload["bbox_y1"] = int(y1)
            payload["bbox_x2"] = int(x2)
            payload["bbox_y2"] = int(y2)
            # 传输层不再包含大图 ROI 等大字段，减少带宽与隐私暴露
            payload.pop("bbox", None)
            payload.pop("roi", None)
        except Exception:
            # 非关键失败，保持原样
            pass
    return payload


def transform_outgoing(payload: Dict[str, Any]) -> Dict[str, Any]:
    """发往服务器前的字段适配（可插拔）。

    当前实现：
    - 拆分 bbox
    - 预留其他隐私处理入口（默认无变更）
    """
    if not isinstance(payload, dict):
        return payload
    payload = dict(payload)  # 浅拷贝，避免外部引用被修改
    payload = _split_bbox(payload)
    return payload
