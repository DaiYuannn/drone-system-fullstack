#!/usr/bin/env python3
"""
Linux 部署状态自检脚本
- 检查 HTTP 健康接口 /api/health
- 检查端口监听
- 检查 systemd 服务（可选）
- 输出关键信息，作为部署后的快速体检

用法（Linux 服务器上执行）:
  SERVER_URL=http://127.0.0.1:5000 python3 tests/linux_deploy_check.py
可选环境变量:
  SERVER_URL   服务器地址，默认 http://127.0.0.1:5000
  SERVICE_NAME systemd 服务名，默认 drone-positioning
  CHECK_TIMEOUT 超时秒数，默认 4.0
"""
import os
import sys
import json
import socket
import subprocess
from urllib.request import urlopen, Request

SERVER = os.environ.get('SERVER_URL', 'http://127.0.0.1:5000')
SERVICE = os.environ.get('SERVICE_NAME', 'drone-positioning')
TIMEOUT = float(os.environ.get('CHECK_TIMEOUT', '4.0'))


def http_get(url: str, timeout: float = TIMEOUT):
    req = Request(url, method='GET')
    with urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode('utf-8', errors='ignore')
        try:
            return json.loads(body)
        except Exception:
            return body


def check_health():
    try:
        data = http_get(SERVER.rstrip('/') + '/api/health')
        print('[OK] /api/health ->', data if isinstance(data, dict) else '非JSON响应')
        return True
    except Exception as e:
        print('[FAIL] /api/health 请求失败:', e)
        return False


def check_port(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=TIMEOUT):
            return True
    except Exception:
        return False


def check_systemd(service: str) -> bool:
    if sys.platform != 'linux':
        print('[SKIP] 非 Linux 平台，跳过 systemd 检查')
        return True
    try:
        out = subprocess.check_output(['systemctl', 'is-active', service], stderr=subprocess.STDOUT, timeout=TIMEOUT)
        state = out.decode().strip()
        print(f'[OK] systemd 状态: {service} -> {state}')
        return state == 'active'
    except Exception as e:
        print(f'[WARN] systemd 状态查询失败: {e}')
        return False


def main():
    print('=== Linux 部署状态自检 ===')
    print('SERVER_URL =', SERVER)
    print('SERVICE    =', SERVICE)

    ok_health = check_health()

    # 解析 host:port
    hostport = SERVER.split('://', 1)[-1].split('/', 1)[0]
    parts = hostport.split(':', 1)
    host = parts[0]
    port = int(parts[1]) if len(parts) == 2 and parts[1].isdigit() else 5000

    ok_port = check_port(host, port)
    print(f"[{'OK' if ok_port else 'FAIL'}] 端口检查: {host}:{port}")

    ok_systemd = check_systemd(SERVICE)

    overall = ok_health and ok_port
    print('\n=== 结果 ===')
    print('健康接口  :', '通过' if ok_health else '失败')
    print('端口监听  :', '通过' if ok_port else '失败')
    print('systemd  :', '通过/忽略' if ok_systemd else '失败或不可用')

    sys.exit(0 if overall else 1)


if __name__ == '__main__':
    main()
