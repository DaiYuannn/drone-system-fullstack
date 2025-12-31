"""
示例算法实现：Paillier 字段级封装（服务器端演示）

说明：此实现仅为演示“可插拔”接口形态。
真实使用时，服务端应在业务层识别 alg=PAILLIER 的 payload，
执行字段级同态聚合或转存密文，而非在此处进行对称解密。
"""
from __future__ import annotations

from typing import Any, Dict


class CryptoAlgo:
    name = "PAILLIER"
    kid = "paillier-demo"

    @staticmethod
    def encrypt(data: bytes) -> Dict[str, Any]:
        return {
            "enc": CryptoAlgo.name,
            "kid": CryptoAlgo.kid,
            "nonce": "",
            "tag": "",
            "ts": 0,
            "ciphertext": data.decode("utf-8"),
            "alg": "PAILLIER",
        }

    @staticmethod
    def decrypt(envelope: Dict[str, Any]) -> bytes:
        # 直接返回原文；字段级同态在上层进行
        return str(envelope.get("ciphertext", "")).encode("utf-8")
