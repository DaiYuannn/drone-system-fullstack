"""
示例算法实现：Paillier 字段级封装（演示版）

用途：演示如何以“替换同名类 CryptoAlgo”的方式实现可插拔。
注意：Paillier 适合字段级同态场景，完整传输层对整包加解密并不直接适配，
此处作为演示，将 payload 原样放入 ciphertext，标记 enc=PAILLIER。
上层应识别 alg/enc=PAILLIER 后，按字段级意义处理 payload。
"""
from __future__ import annotations

import json
import time
from typing import Any, Dict


class CryptoAlgo:
    name = "PAILLIER"
    kid = "paillier-demo"

    @staticmethod
    def encrypt(data: bytes) -> Dict[str, Any]:
        # 不做对称加密，直接包裹原文，交由上层字段级 Paillier 处理
        return {
            "enc": CryptoAlgo.name,
            "kid": CryptoAlgo.kid,
            "nonce": "",
            "tag": "",
            "ts": int(time.time()),
            "ciphertext": data.decode("utf-8"),
            "alg": "PAILLIER",
        }

    @staticmethod
    def decrypt(envelope: Dict[str, Any]) -> bytes:
        # 作为演示：直接返回明文（真实字段级同态需上层处理）
        return str(envelope.get("ciphertext", "")).encode("utf-8")
