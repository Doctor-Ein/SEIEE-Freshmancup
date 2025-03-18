import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog
import threading
import time
import os

class TextInputApp:
    """
    图形化输入输出应用程序
    
    属性：
        root (tk.Tk): 主窗口对象
    """
    def __init__(self, root:tk.Tk):
        """
        初始化应用程序界面和组件
        """
        self.root = root
        self.root.title("图形化输入输出")

        # 输入的状态信息
        self.input_event = tk.BooleanVar(value=False)
        self.user_input=""
        self.file_path=[]

        # 配置网格布局
        self._setup_ui()
        
        # 绑定退出事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

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
        self.input_text.bind("<Command-Delete>",lambda e:self.delete_all())
    
    def delete_all(self):
        # 清空输入框
        self.input_text.delete("1.0", tk.END)

    def put_output(self,text):
        self._append_output(f"{text}\n")
        print(f"{text}\n") #在禁用音频模式的情况下，代替输出调试信息

    def _append_output(self, text):
        """安全更新输出区域"""
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')
    
    def submit_input(self):
        """提交用户输入"""
        self.input_event.set(value=True) # 立即结束get_input阻塞状态，但是会等到submit_input结束
        self.user_input = self.input_text.get("1.0", tk.END).strip()
        if not self.user_input:
            return

        # 清空输入框
        self.input_text.delete("1.0", tk.END)

        # 在输出区域显示用户输入
        self._append_output(f"[User]: {self.user_input}\n")

    def get_input(self):
        self.user_input = ""
        self.input_text.config(state="normal")
        self.root.wait_variable(self.input_event)
        self.input_text.config(state="disabled")
        self.input_event.set(value=False)
        files = self.file_path
        self.file_path=[]
        return [self.user_input,files]

    def select_file(self):
        self.file_path.append(filedialog.askopenfilename())
        self._append_output(f"[User]：文件{self.file_path[-1]}已添加。本轮对话已上传{len(self.file_path)}个文件。\n")
        return self.file_path

    def _on_close(self):
        """关闭窗口时的清理操作"""
        self.root.destroy()
        os._exit(0)

root = tk.Tk()
app = TextInputApp(root)

# 使用示例
if __name__ == "__main__":
    # 启动模拟处理线程
    def model_thread(app):
        """模拟模型处理线程"""
        while True:
            # 获取输入
            user_input = app.get_input()
            if user_input[0] or user_input[1]:
                # 模拟处理耗时
                time.sleep(0.5)
                # 返回处理结果
                app.put_output(f"文字输入：{user_input[0].upper()}")
                app.put_output(f"文件输入：{user_input[1]}")
            time.sleep(0.1)

    threading.Thread(target=model_thread, args=(app,), daemon=True).start()
    
    root.mainloop()