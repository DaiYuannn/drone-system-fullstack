"""
通用加密适配层（无人机端）

设计目标：
- 可插拔：仅需替换同目录下的 crypto_algo.py 文件即可切换算法
- 向后兼容：未启用加密时走明文
- 传输封装：统一密文信封格式，便于服务器端识别与解密

信封格式（JSON）：
{
  "enc": "AES-GCM",           # 算法名/标识
  "kid": "default",           # 密钥ID（可选）
  "nonce": "base64...",       # 随机数/IV
  "tag": "base64...",         # 验证标签
  "ts": 1699999999,            # 发送时间戳（秒）
  "ciphertext": "base64..."   # 密文（对原始JSON字节）
}
"""
from __future__ import annotations

import json
import os
import time
import importlib
from typing import Any, Dict

# 动态加载：优先依据环境变量 DRONE_CRYPTO_ALGO_MODULE 指定模块；否则回退到同目录 crypto_algo.py
def _load_crypto_algo():
    module_name = os.getenv("DRONE_CRYPTO_ALGO_MODULE")
    if module_name:
        try:
            mod = importlib.import_module(module_name)
            return getattr(mod, "CryptoAlgo")
        except Exception:
            # 尝试相对当前包（...security）回退导入
            if "." not in module_name and __package__:
                base_pkg = __package__  # e.g. 'drone_side.security'
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

if CryptoAlgo is None:  # pragma: no cover
    # 兜底的明文直通实现
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
                "ts": int(time.time()),
                "ciphertext": data.decode("utf-8"),
                "plaintext": True,
            }

        @staticmethod
        def decrypt(envelope: Dict[str, Any]) -> bytes:
            if envelope.get("plaintext"):
                return str(envelope.get("ciphertext", "")).encode("utf-8")
            raise ValueError("No crypto_algo available and not plaintext")


def encrypt_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """将字典负载加密为信封。

    Args:
        payload: 原始字典
    Returns:
        信封（dict）
    """
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    env = CryptoAlgo.encrypt(raw)
    if "enc" not in env:
        env["enc"] = getattr(CryptoAlgo, "name", "UNKNOWN")
    if "kid" not in env:
        env["kid"] = getattr(CryptoAlgo, "kid", "default")
    if "ts" not in env:
        env["ts"] = int(time.time())
    # 提案兼容：镜像一个 alg 字段，便于服务端按 alg/payload 识别
    if "alg" not in env:
        env["alg"] = env.get("enc")
    return env


def decrypt_payload(envelope: Dict[str, Any]) -> Dict[str, Any]:
    """将信封解密为字典负载。

    Args:
        envelope: 信封
    Returns:
        原始字典
    """
    raw = CryptoAlgo.decrypt(envelope)
    return json.loads(raw.decode("utf-8"))
