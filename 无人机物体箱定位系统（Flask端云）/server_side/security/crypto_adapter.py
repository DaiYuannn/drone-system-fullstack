"""
通用加密适配层（服务器端）

说明：
- 与无人机端适配层一致，通过 .crypto_algo 切换算法
- 默认支持AES-GCM；如果未安装库则回退为明文
"""
from __future__ import annotations

import json
import os
import importlib
from typing import Any, Dict

def _load_crypto_algo():
    module_name = os.getenv("SERVER_CRYPTO_ALGO_MODULE")
    if module_name:
        try:
            mod = importlib.import_module(module_name)
            return getattr(mod, "CryptoAlgo")
        except Exception:
            if "." not in module_name and __package__:
                base_pkg = __package__  # e.g. 'server_side.security'
                try:
                    mod = importlib.import_module(f"{base_pkg}.{module_name}")
                    return getattr(mod, "CryptoAlgo")
                except Exception:
                    pass
    try:
        from .crypto_algo import CryptoAlgo  # type: ignore
        return CryptoAlgo
    except Exception:
        return None

CryptoAlgo = _load_crypto_algo()  # type: ignore

if CryptoAlgo is None:
    class CryptoAlgo:  # type: ignore
        name = "PLAINTEXT"
        kid = "none"

        @staticmethod
        def encrypt(data: bytes) -> Dict[str, Any]:
            return {
                "enc": CryptoAlgo.name,
                "kid": CryptoAlgo.kid,
                "nonce": "",
                "tag": "",
                "ts": 0,
                "ciphertext": data.decode("utf-8"),
                "plaintext": True,
            }

        @staticmethod
        def decrypt(envelope: Dict[str, Any]) -> bytes:
            if envelope.get("plaintext"):
                return str(envelope.get("ciphertext", "")).encode("utf-8")
            raise ValueError("No crypto_algo available and not plaintext")


def maybe_decrypt_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """如果是加密信封则解密；兼容 enc/ciphertext 与 alg/payload 两种外观。"""
    if not isinstance(data, dict):
        return data

    # 1) 兼容现有 enc/ciphertext 形态
    if {"enc", "ciphertext"}.issubset(data.keys()):
        raw = CryptoAlgo.decrypt(data)
        return json.loads(raw.decode("utf-8"))

    # 2) 兼容提案的 alg/payload 形态
    if {"alg", "payload"}.issubset(data.keys()):
        alg = str(data.get("alg", "")).upper()
        # AES-GCM：将 payload 等价映射为 ciphertext，复用现有解密逻辑
        if "AES" in alg or "GCM" in alg:
            env = dict(data)
            env.setdefault("enc", data.get("alg", "AES-GCM"))
            env.setdefault("ciphertext", data.get("payload", ""))
            raw = CryptoAlgo.decrypt(env)
            return json.loads(raw.decode("utf-8"))
        # Paillier 字段同态：负载为字段级密文对象，按业务上层处理（此处直通）
        if "PAILLIER" in alg:
            payload = data.get("payload")
            return payload if isinstance(payload, dict) else data

    # 否则原样返回
    return data
