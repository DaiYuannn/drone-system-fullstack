#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分模块测试可视化控制台（Tkinter）

功能：
- 提供 5 个测试模块的按钮：视觉识别、随机数据、加密上传、本地回环、心跳-only
- 可输入服务器地址、上传次数、间隔、图片路径
- 右侧“模拟内嵌浏览器”区域：
  - 显示 / 的返回（HTML 前 2000 字符）
  - 显示 /api/health, /api/positions, /api/drones 的 JSON 内容
  - 支持刷新与“打开主页”调用默认浏览器

依赖：标准库 + requests（用于抓取服务器页面与API）
说明：测试模块逻辑复用 tests/windows/modular_tests_cli.py 中的实现。
"""
from __future__ import annotations
import os
import sys
import json
import threading
import time
import webbrowser
import importlib.util
import urllib.request
from functools import partial
from contextlib import redirect_stdout, redirect_stderr
import traceback
import io
from typing import TextIO, cast
from tkinter import Tk, StringVar, IntVar, DoubleVar, BooleanVar, Text, BOTH, END, N, S, E, W, NE, filedialog, messagebox
from tkinter import ttk


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

HAS_REQUESTS = importlib.util.find_spec('requests') is not None
_requests = importlib.import_module('requests') if HAS_REQUESTS else None

def http_get_text(url: str, timeout: float = 6.0) -> str:
    if HAS_REQUESTS and _requests is not None:
        r = _requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r.text
    req = urllib.request.Request(url, method='GET')
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode('utf-8', errors='ignore')

def http_get_json(url: str, timeout: float = 6.0):
    if HAS_REQUESTS and _requests is not None:
        r = _requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r.json()
    text = http_get_text(url, timeout)
    try:
        return json.loads(text)
    except Exception:
        return text

def http_post_json(url: str, payload: dict, headers: dict | None = None, timeout: float = 8.0):
    headers = headers or {}
    if HAS_REQUESTS and _requests is not None:
        r = _requests.post(url, json=payload, headers=headers, timeout=timeout)
        r.raise_for_status()
        return r.json()
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST', headers={'Content-Type': 'application/json', **headers})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode('utf-8', errors='ignore')
        try:
            return json.loads(body)
        except Exception:
            return {'text': body}

def _load_mod_cli():
    """动态加载 modular_tests_cli.py 作为模块，避免包路径问题"""
    path = os.path.join(PROJECT_ROOT, 'tests', 'windows', 'modular_tests_cli.py')
    spec = importlib.util.spec_from_file_location('mod_cli', path)
    if spec is None or spec.loader is None:
        raise RuntimeError('无法加载 modular_tests_cli.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class StreamToText(io.TextIOBase):
    """A text IO stream that forwards writes to App._append_log."""
    def __init__(self, app: 'App'):
        super().__init__()
        self.app = app
        self._buf = ''
    def writable(self) -> bool:
        return True
    def write(self, s: str) -> int:
        if not s:
            return 0
        self._buf += s
        while '\n' in self._buf:
            line, self._buf = self._buf.split('\n', 1)
            self.app._append_log(line)
        return len(s)
    def flush(self) -> None:
        if self._buf:
            self.app._append_log(self._buf)
            self._buf = ''


class App:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title('分模块测试控制台')
        self.root.geometry('1200x700')

        self.server = StringVar(value=os.environ.get('TEST_SERVER', 'http://127.0.0.1:5000'))
        self.count = IntVar(value=3)
        self.interval = DoubleVar(value=1.0)
        self.image_path = StringVar(value=os.path.join(PROJECT_ROOT, 'tests', 'IMG_0002.JPG'))
        self.video_path = StringVar(value='')
        self.admin_token = StringVar(value=os.environ.get('ADMIN_TOKEN',''))
        self.auto_refresh = BooleanVar(value=True)
        self.admin_available = BooleanVar(value=True)

        self._build_ui()

    def _build_ui(self):
        main = ttk.Panedwindow(self.root, orient='horizontal')
        main.pack(fill=BOTH, expand=True)

        # 左侧控制区
        left = ttk.Frame(main, padding=10)
        main.add(left, weight=1)

        # 右侧“模拟浏览器”
        right = ttk.Frame(main, padding=10)
        main.add(right, weight=2)

        # 左侧：参数区
        params = ttk.LabelFrame(left, text='参数')
        params.grid(row=0, column=0, sticky='we', padx=5, pady=5)
        ttk.Label(params, text='服务器:').grid(row=0, column=0, sticky=E)
        ttk.Entry(params, textvariable=self.server, width=40).grid(row=0, column=1, sticky='we', padx=5)
        ttk.Label(params, text='次数:').grid(row=1, column=0, sticky=E)
        ttk.Entry(params, textvariable=self.count, width=8).grid(row=1, column=1, sticky=W)
        ttk.Label(params, text='间隔(s):').grid(row=2, column=0, sticky=E)
        ttk.Entry(params, textvariable=self.interval, width=8).grid(row=2, column=1, sticky=W)
        ttk.Label(params, text='图片:').grid(row=3, column=0, sticky=E)
        entry_img = ttk.Entry(params, textvariable=self.image_path, width=40)
        entry_img.grid(row=3, column=1, sticky='we', padx=5)
        ttk.Button(params, text='浏览...', command=self._choose_image).grid(row=3, column=2, sticky=W)

        for i in range(3):
            params.grid_columnconfigure(i, weight=1)

        # 左侧：模块按钮
        mods = ttk.LabelFrame(left, text='测试模块')
        mods.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        ttk.Button(mods, text='模块1 视觉识别', command=self.run_module1).grid(row=0, column=0, sticky='we', pady=3)
        ttk.Button(mods, text='模块2 随机数据', command=self.run_module2).grid(row=1, column=0, sticky='we', pady=3)
        ttk.Button(mods, text='模块3 加密上传', command=self.run_module3).grid(row=2, column=0, sticky='we', pady=3)
        ttk.Button(mods, text='模块4 本地回环', command=self.run_module4).grid(row=3, column=0, sticky='we', pady=3)
        ttk.Button(mods, text='模块5 心跳-only', command=self.run_module5).grid(row=4, column=0, sticky='we', pady=3)

        # 左侧：日志
        logs = ttk.LabelFrame(left, text='日志')
        logs.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        self.log_text = Text(logs, wrap='word', height=22)
        self.log_text.pack(fill=BOTH, expand=True)

        left.grid_rowconfigure(2, weight=1)
        left.grid_columnconfigure(0, weight=1)

        # 右侧：模拟浏览器
        viewer_top = ttk.Frame(right)
        viewer_top.pack(fill='x')
        ttk.Button(viewer_top, text='刷新', command=self.refresh_viewer).pack(side='left', padx=5)
        ttk.Button(viewer_top, text='打开主页', command=lambda: webbrowser.open(self.server.get())).pack(side='left')

        self.nb = ttk.Notebook(right)
        self.nb.pack(fill=BOTH, expand=True)

        self.tab_root = Text(self.nb, wrap='none')
        self.nb.add(self.tab_root, text='主页(/)')

        self.tab_health = Text(self.nb, wrap='word')
        self.nb.add(self.tab_health, text='/api/health')

        self.tab_positions = Text(self.nb, wrap='word')
        self.nb.add(self.tab_positions, text='/api/positions')

        self.tab_drones = Text(self.nb, wrap='word')
        self.nb.add(self.tab_drones, text='/api/drones')

        # 新增：上传/手动 与 数据库 标签
        self.tab_upload = ttk.Frame(self.nb)
        self.nb.add(self.tab_upload, text='上传/手动')
        self._build_upload_tab(self.tab_upload)

        self.tab_db = ttk.Frame(self.nb)
        self.nb.add(self.tab_db, text='数据库')
        self._build_db_tab(self.tab_db)

        self.refresh_viewer()

    def _choose_image(self):
        path = filedialog.askopenfilename(title='选择测试图片')
        if path:
            self.image_path.set(path)

    def _choose_video(self):
        path = filedialog.askopenfilename(title='选择视频文件')
        if path:
            self.video_path.set(path)

    def _append_log(self, text: str):
        # 线程安全地向日志窗口输出
        def do_insert():
            self.log_text.insert(END, text + '\n')
            self.log_text.see(END)
        try:
            # 使用 after 确保在主线程更新 UI
            self.root.after(0, do_insert)
        except Exception:
            # 回退：直接插入（不推荐，但防止极端情况下丢日志）
            self.log_text.insert(END, text + '\n')
            self.log_text.see(END)

    def _run_in_thread(self, target, *args, **kwargs):
        def runner():
            try:
                stream = StreamToText(self)
                with redirect_stdout(cast(TextIO, stream)), redirect_stderr(cast(TextIO, stream)):
                    ret = target(*args, **kwargs)
                # 冲刷残留缓冲
                try:
                    stream.flush()
                except Exception:
                    pass
                self._append_log(f'[完成] 返回码={ret}')
            except Exception as e:
                self._append_log(f'[异常] {e}')
                try:
                    self._append_log(traceback.format_exc())
                except Exception:
                    pass
        th = threading.Thread(target=runner, daemon=True)
        th.start()

    # 模块按钮回调
    def run_module1(self):
        mod = _load_mod_cli()
        self._append_log('[启动] 模块1 视觉识别')
        self._run_in_thread(mod.module_1_visual_detect, self.image_path.get())

    def run_module2(self):
        mod = _load_mod_cli()
        self._append_log('[启动] 模块2 随机数据')
        self._run_in_thread(mod.module_2_random_data)

    def run_module3(self):
        mod = _load_mod_cli()
        self._append_log('[启动] 模块3 加密上传')
        self._run_in_thread(mod.module_3_encrypt_upload, self.server.get(), self.count.get(), self.interval.get())

    def run_module4(self):
        mod = _load_mod_cli()
        self._append_log('[启动] 模块4 本地回环')
        self._run_in_thread(mod.module_4_crypto_roundtrip)

    def run_module5(self):
        mod = _load_mod_cli()
        self._append_log('[启动] 模块5 心跳-only')
        self._run_in_thread(mod.module_5_heartbeat_only, self.server.get())

    # 右侧“模拟浏览器”刷新
    def refresh_viewer(self):
        base = self.server.get().rstrip('/')
        def safe_get(url, as_json=False):
            try:
                return http_get_json(url) if as_json else http_get_text(url)
            except Exception as e:
                return f'请求失败: {e}'

        # 主页
        html = safe_get(base + '/')
        if isinstance(html, str):
            self.tab_root.delete('1.0', END)
            self.tab_root.insert('1.0', html[:2000])
        else:
            self.tab_root.delete('1.0', END)
            self.tab_root.insert('1.0', str(html))

        # /api/health
        data = safe_get(base + '/api/health', as_json=True)
        self.tab_health.delete('1.0', END)
        self.tab_health.insert('1.0', json.dumps(data, ensure_ascii=False, indent=2) if not isinstance(data, str) else data)

        # /api/positions
        data = safe_get(base + '/api/positions?limit=10', as_json=True)
        self.tab_positions.delete('1.0', END)
        self.tab_positions.insert('1.0', json.dumps(data, ensure_ascii=False, indent=2) if not isinstance(data, str) else data)

        # /api/drones
        data = safe_get(base + '/api/drones', as_json=True)
        self.tab_drones.delete('1.0', END)
        self.tab_drones.insert('1.0', json.dumps(data, ensure_ascii=False, indent=2) if not isinstance(data, str) else data)

        # 自动刷新
        if self.auto_refresh.get():
            self.root.after(5000, self.refresh_viewer)

    # -------- 上传/手动 Tab --------
    def _build_upload_tab(self, parent: ttk.Frame):
        frm = ttk.Frame(parent)
        frm.pack(fill='both', expand=True, padx=8, pady=8)

        # 行1：图片/视频选择
        row1 = ttk.LabelFrame(frm, text='识别并上传')
        row1.pack(fill='x', pady=6)
        ttk.Label(row1, text='图片:').grid(row=0, column=0, sticky=E)
        ttk.Entry(row1, textvariable=self.image_path, width=50).grid(row=0, column=1, sticky='we', padx=5)
        ttk.Button(row1, text='浏览...', command=self._choose_image).grid(row=0, column=2)
        ttk.Button(row1, text='识别并上传图片', command=self._action_detect_image_upload).grid(row=0, column=3, padx=5)

        ttk.Label(row1, text='视频:').grid(row=1, column=0, sticky=E)
        ttk.Entry(row1, textvariable=self.video_path, width=50).grid(row=1, column=1, sticky='we', padx=5)
        ttk.Button(row1, text='浏览...', command=self._choose_video).grid(row=1, column=2)
        ttk.Button(row1, text='识别并上传视频(首个QR)', command=self._action_detect_video_upload).grid(row=1, column=3, padx=5)
        for i in range(4):
            row1.grid_columnconfigure(i, weight=1)

        # 行2：手动 JSON 上传
        row2 = ttk.LabelFrame(frm, text='手动上传(JSON)')
        row2.pack(fill='both', expand=True, pady=6)
        self.manual_endpoint = StringVar(value='/api/upload')
        ttk.Label(row2, text='端点:').grid(row=0, column=0, sticky=E)
        ttk.Combobox(row2, values=['/api/upload','/api/heartbeat'], textvariable=self.manual_endpoint, width=20).grid(row=0, column=1, sticky=W)
        ttk.Label(row2, text='内容:').grid(row=1, column=0, sticky=NE)
        self.manual_text = Text(row2, height=10)
        self.manual_text.grid(row=1, column=1, columnspan=3, sticky='nsew', padx=5, pady=5)
        ttk.Button(row2, text='发送', command=self._action_manual_send).grid(row=2, column=3, sticky=E)
        for i in range(4):
            row2.grid_columnconfigure(i, weight=1)
        row2.grid_rowconfigure(1, weight=1)

    def _client_encrypt(self, payload: dict) -> dict:
        try:
            mod = importlib.import_module('drone_side.security.crypto_adapter')
            return mod.encrypt_payload(payload)
        except Exception:
            return payload

    def _build_detection_payload(self, text: str) -> dict:
        from datetime import datetime, timezone
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'drone_id': 'DRONE_GUI',
            'barcode_data': text,
            'confidence': 0.99,
            'gps': {'latitude': 39.9, 'longitude': 116.3, 'altitude': 50}
        }

    def _detect_qr_texts(self, image_path: str) -> list[str]:
        texts = []
        try:
            cv2 = importlib.import_module('cv2')
            img = cv2.imread(image_path)
            if img is not None:
                detector = cv2.QRCodeDetector()
                try:
                    txts, points, _ = detector.detectAndDecodeMulti(img)
                    for t in (txts or []):
                        if t:
                            texts.append(t)
                except Exception:
                    t, pts, _ = detector.detectAndDecode(img)
                    if t:
                        texts.append(t)
        except Exception:
            pass
        if not texts:
            try:
                pyzbar = importlib.import_module('pyzbar.pyzbar')
                Image = importlib.import_module('PIL.Image')
                img = Image.open(image_path)
                decoded = pyzbar.decode(img)
                for obj in decoded:
                    try:
                        texts.append(obj.data.decode('utf-8', errors='ignore'))
                    except Exception:
                        continue
            except Exception:
                pass
        return texts

    def _action_detect_image_upload(self):
        path = self.image_path.get()
        if not path or not os.path.exists(path):
            messagebox.showwarning('提示', '请选择有效的图片文件')
            return
        texts = self._detect_qr_texts(path)
        if not texts:
            messagebox.showinfo('结果', '未识别到二维码/条码')
            return
        base = self.server.get().strip().rstrip('/')
        for t in texts:
            payload = self._build_detection_payload(t)
            enc = self._client_encrypt(payload)
            try:
                resp = http_post_json(base + '/api/upload', enc)
                self._append_log(f'[上传图片] {t} -> {resp}')
            except Exception as e:
                self._append_log(f'[上传图片失败] {e}')

    def _action_detect_video_upload(self):
        path = self.video_path.get()
        if not path or not os.path.exists(path):
            messagebox.showwarning('提示', '请选择有效的视频文件')
            return
        def worker():
            try:
                cv2 = importlib.import_module('cv2')
            except Exception:
                self._append_log('[视频识别] 需要安装 opencv-python')
                return
            cap = cv2.VideoCapture(path)
            found = None
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                detector = cv2.QRCodeDetector()
                t, pts, _ = detector.detectAndDecode(frame)
                if t:
                    found = t
                    break
            cap.release()
            if found:
                base = self.server.get().strip().rstrip('/')
                payload = self._build_detection_payload(found)
                enc = self._client_encrypt(payload)
                try:
                    resp = http_post_json(base + '/api/upload', enc)
                    self._append_log(f'[上传视频帧] {found} -> {resp}')
                except Exception as e:
                    self._append_log(f'[上传视频失败] {e}')
            else:
                self._append_log('[视频识别] 未识别到二维码')
        self._run_in_thread(worker)

    def _action_manual_send(self):
        base = self.server.get().strip().rstrip('/')
        endpoint = self.manual_endpoint.get()
        try:
            obj = json.loads(self.manual_text.get('1.0', END))
        except Exception as e:
            messagebox.showerror('错误', f'JSON 解析失败: {e}')
            return
        enc = self._client_encrypt(obj)
        try:
            resp = http_post_json(base + endpoint, enc)
            self._append_log(f'[手动上传] -> {resp}')
        except Exception as e:
            self._append_log(f'[手动上传失败] {e}')

    # -------- 数据库 Tab --------
    def _build_db_tab(self, parent: ttk.Frame):
        top = ttk.LabelFrame(parent, text='控制')
        top.pack(fill='x', padx=8, pady=6)
        ttk.Label(top, text='Admin Token:').grid(row=0, column=0, sticky=E)
        ttk.Entry(top, textvariable=self.admin_token, width=40).grid(row=0, column=1, sticky='we', padx=5)
        ttk.Checkbutton(top, text='自动刷新', variable=self.auto_refresh).grid(row=0, column=2, sticky=W)
        ttk.Button(top, text='检测管理端点', command=self._check_admin_available).grid(row=0, column=3, padx=4)
        self.admin_status_label = ttk.Label(top, text='管理端点：未知')
        self.admin_status_label.grid(row=0, column=4, sticky=W, padx=6)

        # 操作区
        ops = ttk.LabelFrame(parent, text='操作')
        ops.pack(fill='x', padx=8, pady=6)
        self.btn_clear_positions = ttk.Button(ops, text='清空 positions', command=self._action_clear_positions)
        self.btn_clear_positions.grid(row=0, column=0, padx=4)
        self.btn_clear_drones = ttk.Button(ops, text='清空 drones', command=self._action_clear_drones)
        self.btn_clear_drones.grid(row=0, column=1, padx=4)
        ttk.Label(ops, text='删除IDs(逗号):').grid(row=1, column=0, sticky=E)
        self.del_ids = StringVar(value='')
        ttk.Entry(ops, textvariable=self.del_ids, width=30).grid(row=1, column=1, sticky='we', padx=4)
        self.btn_delete = ttk.Button(ops, text='删除', command=self._action_delete_positions)
        self.btn_delete.grid(row=1, column=2)
        ttk.Label(ops, text='更新(id, fields JSON):').grid(row=2, column=0, sticky=E)
        self.upd_id = StringVar(value='')
        self.upd_fields = StringVar(value='{"confidence":0.95}')
        ttk.Entry(ops, textvariable=self.upd_id, width=6).grid(row=2, column=1, sticky='w')
        ttk.Entry(ops, textvariable=self.upd_fields, width=50).grid(row=2, column=1, sticky='e', padx=80)
        self.btn_update = ttk.Button(ops, text='更新', command=self._action_update_position)
        self.btn_update.grid(row=2, column=2)

        # 视图区
        view = ttk.LabelFrame(parent, text='实时视图(/api/positions, /api/drones)')
        view.pack(fill='both', expand=True, padx=8, pady=6)
        self.db_positions = Text(view, height=12)
        self.db_positions.pack(fill='both', expand=True, padx=4, pady=4)
        self.db_drones = Text(view, height=8)
        self.db_drones.pack(fill='both', expand=True, padx=4, pady=4)
        ttk.Button(view, text='刷新', command=self._refresh_db_view).pack(anchor='e', padx=6, pady=4)
        self._refresh_db_view()
        # 初次探测管理端点
        self._check_admin_available()

    def _update_admin_buttons_state(self):
        state = 'normal' if self.admin_available.get() else 'disabled'
        for btn in [getattr(self, 'btn_clear_positions', None), getattr(self, 'btn_clear_drones', None), getattr(self, 'btn_delete', None), getattr(self, 'btn_update', None)]:
            if btn is not None:
                btn.configure(state=state)

    def _check_admin_available(self):
        base = self.server.get().strip().rstrip('/')
        # 以 confirm=False 探测路由是否存在，不会执行危险动作
        try:
            http_post_json(base + '/api/admin/positions/clear', {'confirm': False}, headers=self._admin_headers(), timeout=4.0)
            # 能返回JSON则认为存在（即使未授权）
            self.admin_available.set(True)
            self.admin_status_label.configure(text='管理端点：可用（可能需要令牌）', foreground='green')
        except Exception as e:
            em = str(e).lower()
            if '404' in em or 'not found' in em:
                self.admin_available.set(False)
                self.admin_status_label.configure(text='管理端点：不可用（服务器未包含此功能）', foreground='orange')
            else:
                # 其他错误（如 403 未授权、网络问题等）视作端点存在但当前不可用
                self.admin_available.set(True)
                self.admin_status_label.configure(text='管理端点：可用（检查令牌或网络）', foreground='blue')
        self._update_admin_buttons_state()

    def _admin_headers(self) -> dict:
        token = self.admin_token.get().strip()
        return {'X-Admin-Token': token} if token else {}

    def _confirm_twice(self, title: str, msg: str) -> bool:
        if not messagebox.askyesno(title, msg):
            return False
        return messagebox.askyesno(title, '再次确认执行该操作？')

    def _action_clear_positions(self):
        if not self._confirm_twice('确认', '清空所有 positions 记录？'): return
        base = self.server.get().strip().rstrip('/')
        try:
            resp = http_post_json(base + '/api/admin/positions/clear', {'confirm': True}, headers=self._admin_headers())
            self._append_log(f'[清空 positions] -> {resp}')
        except Exception as e:
            self._append_log(f'[清空 positions 失败] {e}')

    def _action_clear_drones(self):
        if not self._confirm_twice('确认', '清空所有 drones 状态？'): return
        base = self.server.get().strip().rstrip('/')
        try:
            resp = http_post_json(base + '/api/admin/drones/clear', {'confirm': True}, headers=self._admin_headers())
            self._append_log(f'[清空 drones] -> {resp}')
        except Exception as e:
            self._append_log(f'[清空 drones 失败] {e}')

    def _action_delete_positions(self):
        ids_str = self.del_ids.get().strip()
        if not ids_str:
            messagebox.showwarning('提示','请输入要删除的ID列表')
            return
        try:
            ids = [int(x) for x in ids_str.split(',') if x.strip()]
        except Exception:
            messagebox.showerror('错误','ID 列表需为逗号分隔的整数')
            return
        if not self._confirm_twice('确认', f'删除 {len(ids)} 条记录？'): return
        base = self.server.get().strip().rstrip('/')
        try:
            resp = http_post_json(base + '/api/admin/positions/delete', {'ids': ids, 'confirm': True}, headers=self._admin_headers())
            self._append_log(f'[删除 positions] -> {resp}')
        except Exception as e:
            self._append_log(f'[删除 positions 失败] {e}')

    def _action_update_position(self):
        pid = self.upd_id.get().strip()
        fields_str = self.upd_fields.get().strip()
        if not pid or not fields_str:
            messagebox.showwarning('提示','请输入 id 与 fields')
            return
        try:
            pid_i = int(pid)
            fields = json.loads(fields_str)
            if not isinstance(fields, dict): raise ValueError('fields 必须是 JSON 对象')
        except Exception as e:
            messagebox.showerror('错误', f'参数错误: {e}')
            return
        base = self.server.get().strip().rstrip('/')
        try:
            resp = http_post_json(base + '/api/admin/positions/update', {'id': pid_i, 'fields': fields}, headers=self._admin_headers())
            self._append_log(f'[更新 position] -> {resp}')
        except Exception as e:
            self._append_log(f'[更新 position 失败] {e}')

    def _refresh_db_view(self):
        base = self.server.get().strip().rstrip('/')
        try:
            pos = http_get_json(base + '/api/positions?limit=20')
            self.db_positions.delete('1.0', END)
            self.db_positions.insert('1.0', json.dumps(pos, ensure_ascii=False, indent=2) if not isinstance(pos, str) else pos)
        except Exception as e:
            self.db_positions.delete('1.0', END)
            self.db_positions.insert('1.0', f'错误: {e}')
        try:
            dr = http_get_json(base + '/api/drones')
            self.db_drones.delete('1.0', END)
            self.db_drones.insert('1.0', json.dumps(dr, ensure_ascii=False, indent=2) if not isinstance(dr, str) else dr)
        except Exception as e:
            self.db_drones.delete('1.0', END)
            self.db_drones.insert('1.0', f'错误: {e}')


def main():
    root = Tk()
    App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
