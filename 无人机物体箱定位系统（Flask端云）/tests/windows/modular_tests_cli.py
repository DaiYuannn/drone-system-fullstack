#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分模块测试命令行工具（Windows 优先）

模块列表：
  1) 视觉识别测试（仅识别，不上传）
  2) 随机数据生成测试（打印示例payload）
  3) 加密上传测试（心跳+识别上传，并在 /api 查询验证）
  4) 本地加解密回环测试（不依赖服务器）
  5) 心跳-only 测试

使用：
  python tests/windows/modular_tests_cli.py --module 4
  python tests/windows/modular_tests_cli.py --server http://<IP>:5000 --module 3 --count 3 --interval 1

环境：优先读取 TEST_SERVER 环境变量；若未提供则默认 http://127.0.0.1:5000。
"""
from __future__ import annotations
import os
import sys
import json
import time
import base64
import random
import string
import argparse
import importlib
import importlib.util
import urllib.request
import urllib.parse
from datetime import datetime, timezone

# 确保可以导入项目内模块
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

HAS_REQUESTS = importlib.util.find_spec('requests') is not None
_requests = importlib.import_module('requests') if HAS_REQUESTS else None

class _Resp:
    def __init__(self, body: bytes):
        self._body = body
        self.text = body.decode('utf-8', errors='ignore')
    def json(self):
        return json.loads(self.text)

def http_get_json(url: str, timeout: float = 6.0):
    if HAS_REQUESTS and _requests is not None:
        r = _requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r.json()
    req = urllib.request.Request(url, method='GET')
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
        return _Resp(body).json()

def http_post_json(url: str, payload: dict, timeout: float = 8.0):
    if HAS_REQUESTS and _requests is not None:
        r = _requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST', headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
        return _Resp(body).json()

def _try_imports():
    missing = []
    if importlib.util.find_spec('requests') is None:
        missing.append('requests')
    if importlib.util.find_spec('pyzbar') is None:
        missing.append('pyzbar')
    if importlib.util.find_spec('PIL') is None:
        missing.append('Pillow')
    if importlib.util.find_spec('Crypto') is None:
        missing.append('pycryptodome')
    return missing


def _load_crypto_adapters():
    # 客户端（drone）侧加密适配器
    try:
        from drone_side.security.crypto_adapter import encrypt_payload as client_encrypt
    except Exception:
        client_encrypt = lambda x: x  # 退化为明文
    # 服务端侧解密适配器（仅用于本地回环）
    try:
        from server_side.security.crypto_adapter import maybe_decrypt_request as server_maybe_decrypt
    except Exception:
        server_maybe_decrypt = lambda x: x
    return client_encrypt, server_maybe_decrypt


def _default_server(args_server: str | None) -> str:
    server = (args_server or os.environ.get('TEST_SERVER') or 'http://127.0.0.1:5000')
    # 去除可能的前后空白，避免 URL 解析失败
    server = server.strip().rstrip('/')
    return server


def _rand_string(n=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


def _build_detection_payload(drone_id: str):
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        'timestamp': now,
        'drone_id': drone_id,
        'barcode_data': _rand_string(12),
        'confidence': round(random.uniform(0.75, 0.99), 3),
        'gps': {
            'latitude': round(39.9 + random.uniform(-0.01, 0.01), 6),
            'longitude': round(116.3 + random.uniform(-0.01, 0.01), 6),
            'altitude': round(50 + random.uniform(-5, 5), 2)
        }
    }
    return payload


def module_1_visual_detect(image_path: str | None = None):
    """视觉识别测试（仅检测二维码/条形码，不上传）
    优先使用 OpenCV 的 QRCodeDetector（无需 zbar），若不可用再尝试 pyzbar。
    """
    # 选择图片
    if not image_path:
        candidate = os.path.join(PROJECT_ROOT, 'tests', 'IMG_0002.JPG')
        image_path = candidate if os.path.exists(candidate) else None
    if not image_path:
        print('[模块1] 未找到默认测试图，请通过 --image 指定图片路径。')
        return 1

    # 尝试 OpenCV
    try:
        cv2 = importlib.import_module('cv2')
        import numpy as np  # noqa: F401
        img_cv = cv2.imread(image_path)
        if img_cv is not None:
            detector = cv2.QRCodeDetector()
            data, points, _ = detector.detectAndDecode(img_cv)
            if data:
                print('[模块1][OpenCV] 识别到 QR：', data)
                return 0
    except Exception:
        pass

    # 回退 pyzbar
    try:
        pyzbar = importlib.import_module('pyzbar.pyzbar')
        Image = importlib.import_module('PIL.Image')
        img = Image.open(image_path)
        decoded = pyzbar.decode(img)
        if not decoded:
            print('[模块1] 未检测到二维码/条码。')
            return 0
        print('[模块1] 检测到如下码：')
        for obj in decoded:
            print(f'  - type={obj.type}, data={obj.data.decode("utf-8", errors="ignore")}')
        return 0
    except Exception as e:
        print('[模块1] OpenCV/pyzbar 皆不可用或识别失败：', e)
        print('建议安装 opencv-python（推荐）或 pyzbar+zbar 后重试。')
        return 1


def module_2_random_data():
    """随机数据生成测试（打印payload示例）"""
    payload = _build_detection_payload(drone_id='DRONE_TEST')
    print('[模块2] 构造的随机payload:')
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def module_3_encrypt_upload(server: str, count: int, interval: float):
    """加密上传测试：发送心跳与识别结果到服务端，并在 /api 查询验证"""
    client_encrypt, _ = _load_crypto_adapters()

    # 健康检查
    try:
        data_health = http_get_json(f'{server}/api/health', timeout=5)
        print('[模块3] 健康检查：', data_health)
    except Exception as e:
        print('[模块3] 健康检查失败，请确认服务器地址：', server)
        print(e)
        return 1

    drone_id = 'DRONE_TEST'

    for i in range(count):
        # 心跳
        hb = {
            'drone_id': drone_id,
            'gps': {
                'latitude': 39.9,
                'longitude': 116.3,
                'altitude': 50
            },
            'battery_level': random.randint(60, 100),
            'signal_strength': random.randint(60, 100),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        enc_hb = client_encrypt(hb)
        try:
            hb_resp = http_post_json(f'{server}/api/heartbeat', enc_hb, timeout=8)
            print(f'[模块3] 心跳({i+1}/{count}) ->', hb_resp)
        except Exception as e:
            print('[模块3] 心跳发送失败：', e)
            return 1

        # 识别上传
        det = _build_detection_payload(drone_id)
        enc_det = client_encrypt(det)
        try:
            up_resp = http_post_json(f'{server}/api/upload', enc_det, timeout=10)
            print(f'[模块3] 上传({i+1}/{count}) ->', up_resp)
        except Exception as e:
            print('[模块3] 上传失败：', e)
            return 1

        if i < count - 1:
            time.sleep(interval)

    # 查询验证
    try:
        data = http_get_json(f'{server}/api/positions?limit=5', timeout=8)
        print('[模块3] 最近 positions: count=', data.get('count'))
    except Exception as e:
        print('[模块3] 查询 positions 失败：', e)
        return 1

    try:
        data = http_get_json(f'{server}/api/drones', timeout=8)
        print('[模块3] drones 状态: count=', data.get('count'))
    except Exception as e:
        print('[模块3] 查询 drones 失败：', e)
        return 1

    return 0


def module_4_crypto_roundtrip():
    """本地加解密回环测试，不依赖服务器"""
    client_encrypt, server_maybe_decrypt = _load_crypto_adapters()
    payload = _build_detection_payload('DRONE_TEST')
    enc = client_encrypt(payload)
    dec = server_maybe_decrypt(enc if isinstance(enc, dict) else payload)
    ok = (dec == payload)
    print('[模块4] 回环结果：', 'PASS' if ok else 'FAIL')
    if not ok:
        print('  原始: ', json.dumps(payload, ensure_ascii=False))
        print('  解密: ', json.dumps(dec, ensure_ascii=False))
    return 0 if ok else 1


def module_5_heartbeat_only(server: str):
    client_encrypt, _ = _load_crypto_adapters()
    hb = {
        'drone_id': 'DRONE_TEST',
        'gps': {'latitude': 39.9, 'longitude': 116.3, 'altitude': 50},
        'battery_level': random.randint(60, 100),
        'signal_strength': random.randint(60, 100),
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    enc_hb = client_encrypt(hb)
    try:
        data = http_post_json(f'{server}/api/heartbeat', enc_hb, timeout=8)
        print('[模块5] 心跳响应：', data)
        return 0
    except Exception as e:
        print('[模块5] 心跳失败：', e)
        return 1


def main():
    parser = argparse.ArgumentParser(description='分模块测试命令行工具')
    parser.add_argument('--server', type=str, help='服务器地址，例如 http://<IP>:5000')
    parser.add_argument('--module', type=int, choices=[1,2,3,4,5], default=4, help='要运行的模块编号')
    parser.add_argument('--count', type=int, default=3, help='模块3的上传次数')
    parser.add_argument('--interval', type=float, default=1.0, help='模块3的上传间隔秒')
    parser.add_argument('--image', type=str, help='模块1使用的测试图片路径')
    args = parser.parse_args()

    missing = _try_imports()
    if missing:
        # 仅提示，不阻塞运行。模块1若缺少视觉库，函数内会自行提示并返回。
        print('提示：检测到可能缺少依赖 ->', ', '.join(missing))

    server = _default_server(args.server)

    if args.module == 1:
        return module_1_visual_detect(args.image)
    elif args.module == 2:
        return module_2_random_data()
    elif args.module == 3:
        return module_3_encrypt_upload(server, args.count, args.interval)
    elif args.module == 4:
        return module_4_crypto_roundtrip()
    elif args.module == 5:
        return module_5_heartbeat_only(server)
    else:
        print('未知模块')
        return 1


if __name__ == '__main__':
    sys.exit(main())
