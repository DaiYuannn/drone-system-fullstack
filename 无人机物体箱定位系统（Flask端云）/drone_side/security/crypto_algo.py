"""
默认算法实现：AES-GCM（对称加密）

说明：
- 该文件可被同名实现直接替换以切换算法（如Paillier/HLP混合封装、DPQKET等）
- 密钥管理：演示版从环境变量读取对称密钥或本地文件；生产应使用KMS/安全芯片
"""
from __future__ import annotations

import base64
import os
import time
from typing import Any, Dict

try:
    from Crypto.Cipher import AES  # PyCryptodome
    from Crypto.Random import get_random_bytes
except Exception as e:  # pragma: no cover
    AES = None  # type: ignore
    get_random_bytes = None  # type: ignore


class CryptoAlgo:
    name = "AES-GCM"
    kid = os.getenv("DRONE_KID", "default")

    @staticmethod
    def _get_key() -> bytes:
        key_b64 = os.getenv("DRONE_AES_KEY_B64")
        if key_b64:
            return base64.b64decode(key_b64)
        # 演示用固定key（32字节）；务必替换为安全来源
        return (os.getenv("DRONE_AES_KEY", "0" * 32)).encode("utf-8").ljust(32, b"0")[:32]

    @staticmethod
    def encrypt(data: bytes) -> Dict[str, Any]:
        if AES is None:
            # 无PyCryptodome时，退化为明文
            return {
                "enc": "PLAINTEXT",
                "kid": CryptoAlgo.kid,
                "nonce": "",
                "tag": "",
                "ts": int(time.time()),
                "ciphertext": data.decode("utf-8"),
                "plaintext": True,
            }

        key = CryptoAlgo._get_key()
        nonce = get_random_bytes(12)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        return {
            "enc": CryptoAlgo.name,
            "kid": CryptoAlgo.kid,
            "nonce": base64.b64encode(nonce).decode("ascii"),
            "tag": base64.b64encode(tag).decode("ascii"),
            "ts": int(time.time()),
            "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
        }

    @staticmethod
    def decrypt(envelope: Dict[str, Any]) -> bytes:
        if envelope.get("plaintext") or envelope.get("enc") == "PLAINTEXT":
            return str(envelope.get("ciphertext", "")).encode("utf-8")

        if AES is None:
            raise RuntimeError("AES backend not available for decryption")

        key = CryptoAlgo._get_key()
        nonce = base64.b64decode(envelope["nonce"])  # type: ignore
        tag = base64.b64decode(envelope["tag"])      # type: ignore
        ciphertext = base64.b64decode(envelope["ciphertext"])  # type: ignore
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        data = cipher.decrypt_and_verify(ciphertext, tag)
        return data
