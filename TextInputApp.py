import tkinter as tk
from tkinter import scrolledtext, filedialog
import threading
import time
import os
from datetime import datetime

class TextInputApp:
    """
    图形化输入输出应用程序
    
    属性：
        root (tk.Tk): 主窗口对象
        dialogue_file (str): 当前会话的对话记录文件路径
    """
    def __init__(self, root: tk.Tk):
        """
        初始化应用程序界面和组件
        """
        self.root = root
        self.root.title("图形化输入输出")

        # 输入的状态信息
        self.input_event = tk.BooleanVar(value=False)
        self.user_input = ""
        self.file_path = []

        # 初始化对话记录系统
        self._init_dialogue_system()

        # 配置网格布局
        self._setup_ui()
        
        # 绑定退出事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _init_dialogue_system(self):
        """初始化对话记录系统"""
        # 确保Dialogue目录存在
        os.makedirs("Dialogue", exist_ok=True)
        
        # 为当前会话创建唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.dialogue_file = f"Dialogue/session_{timestamp}.txt"
        
        # 写入会话头信息
        with open(self.dialogue_file, 'a', encoding='utf-8') as f:
            f.write(f"=== 对话会话开始于 {timestamp} ===\n\n")

    def _setup_ui(self):
        """初始化用户界面组件"""
        # 配置网格布局权重
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        
        # 输出区域
        self.output_text = scrolledtext.ScrolledText(
            self.root, 
            width=60,
            height=20,
            wrap=tk.WORD,
            spacing1=2,
            spacing3=2,
            state='disabled'
        )
        self.output_text.grid(
            row=0, 
            column=0, 
            columnspan=2,
            padx=10, 
            pady=10, 
            sticky="nsew"
        )
        
        # 输入区域
        self.input_text = tk.Text(
            self.root,
            width=50,
            height=5,
            wrap=tk.WORD,
            spacing1=2,
            spacing3=2
        )
        self.input_text.grid(
            row=1, 
            column=0,
            rowspan=2, 
            padx=(10, 5), 
            pady=5, 
            sticky="nsew"
        )
        self.input_text.focus()
        
        # 提交按钮
        self.submit_button = tk.Button(
            self.root, 
            text="提交", 
            width=10,
            height=2,
            command=self.submit_input
        )
        self.submit_button.grid(
            row=1, 
            column=1, 
            padx=(5, 10), 
            pady=5, 
            sticky="nsew"
        )

        # 文件选取按钮
        self.file_selection_button = tk.Button(
            self.root, 
            text="添加文件", 
            width=10,
            height=2,
            command=self.select_file
        )
        self.file_selection_button.grid(
            row=2, 
            column=1, 
            padx=(5, 10), 
            pady=5, 
            sticky="nsew"
        )
        
        # 绑定快捷键
        self._bind_shortcuts()

    def _bind_shortcuts(self):
        """绑定快捷键"""
        shortcuts = ["<Shift-Return>", "<Control-Return>", "<Command-Return>"]
        for shortcut in shortcuts:
            self.input_text.bind(shortcut, lambda e: self.submit_input())
        self.input_text.bind("<Command-Delete>", lambda e: self.delete_all())
    
    def delete_all(self):
        """清空输入框"""
        self.input_text.delete("1.0", tk.END)

    def put_output(self, text):
        """
        输出文本到界面并记录到对话文件
        :param text: 要输出的文本
        """
        self._append_output(f"{text}\n")
        
        # 记录到对话文件
        with open(self.dialogue_file, 'a', encoding='utf-8') as f:
            f.write(f"{text}\n")

    def _append_output(self, text):
        """安全更新输出区域"""
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')
    
    def submit_input(self):
        """提交用户输入"""
        self.input_event.set(value=True)  # 结束get_input的阻塞状态
        self.user_input = self.input_text.get("1.0", tk.END).strip()
        if not self.user_input:
            return

        # 清空输入框
        self.input_text.delete("1.0", tk.END)

        # 在输出区域显示用户输入
        self._append_output(f"[User]: {self.user_input}\n")
        
        # 记录用户输入到文件
        with open(self.dialogue_file, 'a', encoding='utf-8') as f:
            f.write(f"[User]: {self.user_input}\n")

    def get_input(self):
        """获取用户输入"""
        self.user_input = ""
        self.input_text.config(state="normal")
        self.root.wait_variable(self.input_event)
        self.input_text.config(state="disabled")
        self.input_event.set(value=False)
        files = self.file_path
        self.file_path = []
        return [self.user_input, files]

    def select_file(self):
        """选择文件并添加到当前会话"""
        filepath = filedialog.askopenfilename()
        if filepath:  # 用户可能取消选择
            self.file_path.append(filepath)
            msg = f"[User]: 文件 {os.path.basename(filepath)} 已添加。本轮对话已上传 {len(self.file_path)} 个文件。\n"
            self._append_output(msg)
            
            # 记录文件添加操作
            with open(self.dialogue_file, 'a', encoding='utf-8') as f:
                f.write(msg)
        return self.file_path

    def _on_close(self):
        """关闭窗口时的清理操作"""
        # 写入会话结束标记
        with open(self.dialogue_file, 'a', encoding='utf-8') as f:
            f.write("\n=== 对话会话结束 ===\n")
        
        # 关闭窗口
        self.root.destroy()
        os._exit(0)

root = tk.Tk()
app = TextInputApp(root)