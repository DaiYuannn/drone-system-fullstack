import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import csv

# 可选依赖：PDF 与 DOCX 解析
try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

try:
    import docx  # python-docx
except Exception:
    docx = None

class FileSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件内容搜索工具")
        self.root.geometry("800x600")
        
        # 搜索线程控制
        self.search_thread = None
        self.stop_search = False
        
        self.create_widgets()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # 文件夹选择
        ttk.Label(main_frame, text="搜索文件夹:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.folder_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.folder_path, width=50).grid(row=0, column=1, sticky="we", pady=5)
        ttk.Button(main_frame, text="浏览", command=self.browse_folder).grid(row=0, column=2, padx=5, pady=5)

        # 搜索关键词
        ttk.Label(main_frame, text="搜索内容:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.search_text = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.search_text, width=50).grid(row=1, column=1, sticky="we", pady=5)

        # 搜索选项
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=2, column=0, columnspan=3, sticky="we", pady=5)

        self.case_sensitive = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="区分大小写", variable=self.case_sensitive).grid(row=0, column=0, padx=5)

        self.search_filename = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="搜索文件名", variable=self.search_filename).grid(row=0, column=1, padx=5)

        self.search_content = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="搜索文件内容", variable=self.search_content).grid(row=0, column=2, padx=5)

        # 搜索按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=5)

        ttk.Button(button_frame, text="开始搜索", command=self.start_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="停止搜索", command=self.stop_search_func).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清除结果", command=self.clear_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="导出结果", command=self.export_results).pack(side=tk.LEFT, padx=5)

        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky="we", pady=5)

        # 结果统计
        self.result_count = tk.StringVar(value="找到 0 个结果")
        ttk.Label(main_frame, textvariable=self.result_count).grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=5)

        # 结果树形视图
        columns = ("类型", "位置", "详细信息")
        self.results_tree = ttk.Treeview(main_frame, columns=columns, show="tree headings", height=15)
        self.results_tree.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=5)

        # 设置列标题
        self.results_tree.heading("#0", text="文件/文件夹")
        self.results_tree.column("#0", width=200)

        for col in columns:
            self.results_tree.heading(col, text=col)
            if col == "类型":
                self.results_tree.column(col, width=80)
            elif col == "位置":
                self.results_tree.column(col, width=300)
            else:
                self.results_tree.column(col, width=200)

        # 滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        scrollbar.grid(row=6, column=3, sticky="ns")
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        # 双击结果打开文件位置
        self.results_tree.bind("<Double-1>", self.on_item_double_click)

        # 结果异步队列 & 统计
        self.result_queue = queue.Queue()
        self._ui_updater_running = False
        self._matched_count = 0
        self._total_files = 0
        self._executor = None
        
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
    
    def start_search(self):
        if not self.folder_path.get():
            messagebox.showerror("错误", "请选择要搜索的文件夹")
            return
            
        if not self.search_text.get():
            messagebox.showerror("错误", "请输入要搜索的内容")
            return
            
        if not self.search_filename.get() and not self.search_content.get():
            messagebox.showerror("错误", "请至少选择一种搜索类型")
            return
        
        # 依赖提示（仅提示一次）
        if self.search_content.get():
            missing = []
            if fitz is None:
                missing.append("PDF (PyMuPDF)")
            if docx is None:
                missing.append("Word (python-docx)")
            if missing:
                messagebox.showinfo(
                    "提示",
                    "未安装以下解析依赖，将跳过对应格式的内容搜索：\n- " + "\n- ".join(missing) +
                    "\n\n可用 pip 安装：pip install pymupdf python-docx"
                )
        
        # 清除之前的结果
        self.clear_results()
        
        # 开始进度条
        self.progress.start()
        
        # 禁用搜索按钮，启用停止按钮
        self.toggle_buttons(False)
        
        # 重置停止标志
        self.stop_search = False
        
        # 在新线程中执行搜索
        self.search_thread = threading.Thread(target=self.perform_search)
        self.search_thread.daemon = True
        self.search_thread.start()
        
        # 定期检查线程状态
        self.check_thread()
    
    def stop_search_func(self):
        self.stop_search = True
        if self.search_thread and self.search_thread.is_alive():
            self.search_thread.join(timeout=1.0)
        self.progress.stop()
        self.toggle_buttons(True)
        # 停止 UI 队列更新
        self._ui_updater_running = False
    
    def clear_results(self):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.result_count.set("找到 0 个结果")
        self._matched_count = 0
    
    def toggle_buttons(self, enabled):
        # 在实际应用中，您可能需要添加更多按钮控制
        pass
    
    def check_thread(self):
        if self.search_thread and self.search_thread.is_alive():
            self.root.after(100, self.check_thread)
        else:
            self.progress.stop()
            self.toggle_buttons(True)
    
    def perform_search(self):
        search_folder = self.folder_path.get()
        search_term = self.search_text.get()
        case_sensitive = self.case_sensitive.get()
        search_filename = self.search_filename.get()
        search_content = self.search_content.get()
        
        # 设置匹配标志
        flags = 0 if case_sensitive else re.IGNORECASE
        
        # 编译正则表达式
        pattern = re.compile(re.escape(search_term), flags)
        
        # 先遍历收集目录与文件（目录匹配仍在主线程）
        files_to_process = []
        for root_dir, dirs, files in os.walk(search_folder):
            if self.stop_search:
                break

            # 目录名匹配
            if search_filename:
                for dir_name in dirs:
                    if self.stop_search:
                        break
                    if pattern.search(dir_name):
                        self.enqueue_result("文件夹", dir_name, root_dir, "文件夹名称匹配")

            # 收集文件路径，后续并发处理
            for file_name in files:
                if self.stop_search:
                    break
                file_path = os.path.join(root_dir, file_name)
                files_to_process.append(file_path)

        if self.stop_search:
            return

        self._total_files = len(files_to_process)

        # 启动 UI 批量更新器
        self.start_ui_updater()

        # 并发处理文件（包含文件名匹配 + 内容匹配）
        max_workers = max(4, (os.cpu_count() or 4) * 2)
        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                self._executor = executor
                futures = []
                for fp in files_to_process:
                    futures.append(executor.submit(
                        self.process_single_file,
                        fp,
                        pattern,
                        search_filename,
                        search_content
                    ))

                for fut in as_completed(futures):
                    if self.stop_search:
                        break
                    try:
                        results = fut.result()
                        if not results:
                            continue
                        for item in results:
                            self.enqueue_result(*item)
                    except Exception:
                        # 单文件异常忽略
                        pass
        finally:
            # 结束 UI 批量更新
            self._ui_updater_running = False
            self._executor = None

        # 最终更新结果计数（由 UI updater 实时更新，这里确保收尾）
        self.root.after(0, lambda: self.result_count.set(f"找到 {self._matched_count} 个结果"))

    def enqueue_result(self, item_type, name, location, details):
        self.result_queue.put((item_type, name, location, details))

    def start_ui_updater(self):
        if self._ui_updater_running:
            return
        self._ui_updater_running = True
        self.root.after(0, self._drain_queue_periodic)

    def _drain_queue_periodic(self):
        # 每次批量处理一定数量，避免 UI 卡顿
        processed = 0
        while not self.result_queue.empty() and processed < 200:
            try:
                item_type, name, location, details = self.result_queue.get_nowait()
                self._add_result_to_tree(item_type, name, location, details)
                self._matched_count += 1
            except queue.Empty:
                break
            finally:
                processed += 1

        # 更新计数
        self.result_count.set(f"找到 {self._matched_count} 个结果")

        if self._ui_updater_running:
            self.root.after(100, self._drain_queue_periodic)

    def process_single_file(self, file_path, pattern, search_filename, search_content):
        if self.stop_search:
            return []

        results = []
        root_dir, file_name = os.path.split(file_path)

        # 文件名匹配
        if search_filename and pattern.search(file_name):
            file_size = self.get_file_size(file_path)
            results.append(("文件", file_name, root_dir, f"文件名匹配 (大小: {file_size})"))

        # 内容匹配
        if search_content:
            # 大文件/二进制跳过（但 PDF/DOCX 仍尝试用解析器）
            ext = os.path.splitext(file_name)[1].lower()
            is_docx = ext == ".docx"
            is_pdf = ext == ".pdf"

            try:
                if is_pdf and fitz is not None:
                    pdf_hit = self.search_pdf_first_match(file_path, pattern)
                    if pdf_hit is not None:
                        page_num, snippet = pdf_hit
                        results.append(("文件", file_name, root_dir, f"第 {page_num} 页: {snippet}"))
                elif is_docx and docx is not None:
                    para_idx, snippet = self.search_docx_first_match(file_path, pattern)
                    if para_idx is not None:
                        results.append(("文件", file_name, root_dir, f"第 {para_idx} 段: {snippet}"))
                else:
                    # 纯文本兜底
                    if not self.is_large_file(file_path) and not self.is_binary_file(file_path):
                        line_num, snippet = self.search_text_first_match(file_path, pattern)
                        if line_num is not None:
                            results.append(("文件", file_name, root_dir, f"第 {line_num} 行: {snippet}"))
            except Exception:
                # 单文件解析异常忽略
                pass

        return results

    def search_text_first_match(self, file_path, pattern):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f, start=1):
                    if self.stop_search:
                        return (None, None)
                    m = pattern.search(line)
                    if m:
                        return (i, self._make_snippet(line, m.start(), m.end()))
        except Exception:
            return (None, None)
        return (None, None)

    def search_docx_first_match(self, file_path, pattern):
        if docx is None:
            return (None, None)
        try:
            d = docx.Document(file_path)
            for idx, p in enumerate(d.paragraphs, start=1):
                if self.stop_search:
                    return (None, None)
                text = p.text or ""
                m = pattern.search(text)
                if m:
                    return (idx, self._make_snippet(text, m.start(), m.end()))
        except Exception:
            return (None, None)
        return (None, None)

    def search_pdf_first_match(self, file_path, pattern):
        if fitz is None:
            return None
        try:
            with fitz.open(file_path) as doc:
                if doc.is_encrypted:
                    return None
                for page_index in range(len(doc)):
                    if self.stop_search:
                        return None
                    page = doc.load_page(page_index)
                    text = page.get_text("text") or ""
                    m = pattern.search(text)
                    if m:
                        return (page_index + 1, self._make_snippet(text, m.start(), m.end()))
        except Exception:
            return None
        return None

    def _make_snippet(self, text, start, end, ctx=50):
        # 从匹配位置裁剪片段，便于展示
        start_ctx = max(0, start - ctx)
        end_ctx = min(len(text), end + ctx)
        snippet = text[start_ctx:end_ctx].strip()
        snippet = snippet.replace('\n', ' ').replace('\r', ' ')
        return (snippet[:100] + '...') if len(snippet) > 100 else snippet
    
    def add_result_to_tree(self, item_type, name, location, details):
        # 在主线程中更新UI
        self.root.after(0, self._add_result_to_tree, item_type, name, location, details)
    
    def _add_result_to_tree(self, item_type, name, location, details):
        self.results_tree.insert(
            "", 
            tk.END, 
            text=name, 
            values=(item_type, location, details)
        )

    def export_results(self):
        # 导出当前结果为 CSV
        if not self.results_tree.get_children():
            messagebox.showinfo("提示", "没有可导出的结果")
            return
        file_path = filedialog.asksaveasfilename(
            title="导出为 CSV",
            defaultextension=".csv",
            filetypes=(("CSV 文件", "*.csv"), ("所有文件", "*.*"))
        )
        if not file_path:
            return
        try:
            with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["文件/文件夹", "类型", "位置", "详细信息", "导出时间"])
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                for item in self.results_tree.get_children():
                    text = self.results_tree.item(item, "text")
                    vals = self.results_tree.item(item, "values")
                    writer.writerow([text, vals[0], vals[1], vals[2], now])
            messagebox.showinfo("成功", f"已导出到: {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")
    
    def get_file_size(self, file_path):
        try:
            size = os.path.getsize(file_path)
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size/1024:.1f} KB"
            else:
                return f"{size/(1024*1024):.1f} MB"
        except:
            return "未知"
    
    def is_binary_file(self, file_path):
        # 简单的二进制文件检测
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\0' in chunk:
                    return True
        except:
            pass
        return False
    
    def is_large_file(self, file_path, max_size_mb=10):
        try:
            size = os.path.getsize(file_path)
            return size > max_size_mb * 1024 * 1024
        except:
            return True
    
    def on_item_double_click(self, event):
        item = self.results_tree.selection()[0]
        item_type = self.results_tree.item(item, "values")[0]
        location = self.results_tree.item(item, "values")[1]
        name = self.results_tree.item(item, "text")
        
        if item_type == "文件":
            file_path = os.path.join(location, name)
            # 在Windows上打开文件所在文件夹并选中文件
            if os.name == 'nt':
                try:
                    # 使用 explorer 精确选中文件
                    os.system(f'explorer /select,"{file_path}"')
                except:
                    messagebox.showinfo("信息", f"文件路径: {file_path}")
            else:
                messagebox.showinfo("信息", f"文件路径: {file_path}")
        else:
            # 打开文件夹
            folder_path = os.path.join(location, name)
            if os.name == 'nt':
                try:
                    os.system(f'explorer "{folder_path}"')
                except:
                    messagebox.showinfo("信息", f"文件夹路径: {folder_path}")
            else:
                messagebox.showinfo("信息", f"文件夹路径: {folder_path}")

def main():
    root = tk.Tk()
    app = FileSearchApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()