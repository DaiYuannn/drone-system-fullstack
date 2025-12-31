from __future__ import annotations

import base64
import os
import time
from typing import Any, Dict

try:
    from Crypto.Cipher import AES
except Exception:
    AES = None  # type: ignore


class CryptoAlgo:
    name = "AES-GCM"
    kid = os.getenv("SERVER_KID", "default")

    @staticmethod
    def _get_key() -> bytes:
        key_b64 = os.getenv("SERVER_AES_KEY_B64")
        if key_b64:
            return base64.b64decode(key_b64)
        return (os.getenv("SERVER_AES_KEY", "0" * 32)).encode("utf-8").ljust(32, b"0")[:32]

    @staticmethod
    def encrypt(data: bytes) -> Dict[str, Any]:
        # 服务端通常不负责加密上行；保留以便需要时响应下行密文
        if AES is None:
            return {
                "enc": "PLAINTEXT",
                "kid": CryptoAlgo.kid,
                "nonce": "",
                "tag": "",
                "ts": int(time.time()),
                "ciphertext": data.decode("utf-8"),
                "plaintext": True,
            }
        raise NotImplementedError("Server-side encrypt not used by default")

    @staticmethod
    def decrypt(envelope: Dict[str, Any]) -> bytes:
        if envelope.get("plaintext") or envelope.get("enc") == "PLAINTEXT":
            return str(envelope.get("ciphertext", "")).encode("utf-8")
        if AES is None:
            raise RuntimeError("AES backend not available")
        nonce = base64.b64decode(envelope["nonce"])  # type: ignore
        tag = base64.b64decode(envelope["tag"])      # type: ignore
        ciphertext = base64.b64decode(envelope["ciphertext"])  # type: ignore
        key = CryptoAlgo._get_key()
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        data = cipher.decrypt_and_verify(ciphertext, tag)
        return data
