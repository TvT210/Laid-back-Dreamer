import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import requests
import json
import threading


class DeepSeekChatUI:
    def __init__(self, root):
        # 设置主窗口
        self.root = root
        self.root.title("DeepSeek 对话界面")
        self.root.geometry("800x600")  # 窗口大小
        self.root.resizable(True, True)  # 允许窗口大小调整

        # 存储对话历史，用于连续对话
        self.chat_history = []

        # 创建UI组件
        self.create_widgets()

        # 配置网格权重，使组件能随窗口大小调整
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def create_widgets(self):
        # 1. API密钥输入区域
        api_frame = ttk.Frame(self.root, padding="10")
        api_frame.grid(row=0, column=0, sticky="ew")

        ttk.Label(api_frame, text="DeepSeek API密钥:").pack(side=tk.LEFT, padx=5)

        self.api_key_entry = ttk.Entry(api_frame, width=50, show="*")
        self.api_key_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        # 可以在这里预设API密钥，避免每次输入（仅本地测试用）
        # self.api_key_entry.insert(0, "your_api_key_here")

        # 2. 对话显示区域 - 使用Frame包裹来实现间距效果
        chat_frame = ttk.Frame(self.root, padding="10")
        chat_frame.grid(row=1, column=0, sticky="nsew")

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD  # 移除了不支持的padding参数
        )
        self.chat_display.pack(fill="both", expand=True)

        # 3. 用户输入区域
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.grid(row=2, column=0, sticky="ew")

        # 用户输入框使用Frame包裹实现内边距效果
        input_text_frame = ttk.Frame(input_frame)
        input_text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.user_input = scrolledtext.ScrolledText(
            input_text_frame, wrap=tk.WORD, height=3
        )
        self.user_input.pack(fill=tk.X, expand=True, padx=2, pady=2)
        self.user_input.focus_set()  # 设置焦点到输入框

        # 4. 按钮区域
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(side=tk.RIGHT, padx=5)

        self.send_btn = ttk.Button(
            button_frame, text="发送", command=self.send_message
        )
        self.send_btn.pack(pady=5, fill=tk.X)

        self.clear_btn = ttk.Button(
            button_frame, text="清空对话", command=self.clear_chat
        )
        self.clear_btn.pack(pady=5, fill=tk.X)

        # 绑定Enter键发送消息，Shift+Enter换行
        self.user_input.bind("<Return>", self.handle_enter)

    def handle_enter(self, event):
        """处理Enter键事件，区分普通Enter和Shift+Enter"""
        if event.state & 0x1:  # 检测Shift键是否按下
            return  # 允许换行
        else:
            self.send_message()
            return "break"  # 阻止默认行为（换行）

    def add_message_to_display(self, sender, message):
        """将消息添加到对话显示区域"""
        self.chat_display.config(state=tk.NORMAL)  # 临时允许编辑

        # 添加发送者标签（用户/AI）
        if sender == "user":
            self.chat_display.insert(tk.END, "你: \n", "user")
        else:
            self.chat_display.insert(tk.END, "AI: \n", "ai")

        # 添加消息内容
        self.chat_display.insert(tk.END, message + "\n\n")

        # 设置标签样式
        self.chat_display.tag_config("user", foreground="blue", font=("SimHei", 10, "bold"))
        self.chat_display.tag_config("ai", foreground="green", font=("SimHei", 10, "bold"))

        self.chat_display.config(state=tk.DISABLED)  # 禁止编辑
        self.chat_display.see(tk.END)  # 滚动到最新消息

    def send_message(self):
        """发送用户消息并获取AI回复"""
        # 获取用户输入
        user_message = self.user_input.get("1.0", tk.END).strip()

        # 检查输入是否为空
        if not user_message:
            messagebox.showwarning("警告", "请输入消息内容！")
            return

        # 检查API密钥是否为空
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showwarning("警告", "请输入API密钥！")
            return

        # 清空输入框
        self.user_input.delete("1.0", tk.END)

        # 显示用户消息
        self.add_message_to_display("user", user_message)

        # 更新对话历史
        self.chat_history.append({"role": "user", "content": user_message})

        # 禁用发送按钮，防止重复发送
        self.send_btn.config(state=tk.DISABLED)
        self.add_message_to_display("ai", "正在思考...")

        # 在新线程中调用API，避免界面卡顿
        threading.Thread(
            target=self.call_deepseek_api,
            args=(api_key, user_message),
            daemon=True
        ).start()

    def call_deepseek_api(self, api_key, user_message):
        """调用DeepSeek API获取回复"""
        try:
            # DeepSeek API端点
            url = "https://api.deepseek.com/v1/chat/completions"

            # 请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            # 请求体，包含对话历史
            payload = {
                "model": "deepseek-chat",  # 使用的模型
                "messages": self.chat_history,  # 完整对话历史，支持连续对话
                "temperature": 0.7,  # 创造性参数，0-1之间
                "max_tokens": 1024  # 最大回复长度
            }

            # 发送请求
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30  # 超时设置
            )

            # 检查响应状态
            response.raise_for_status()

            # 解析响应
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]

            # 更新对话历史
            self.chat_history.append({"role": "assistant", "content": ai_response})

            # 在主线程中更新UI
            self.root.after(0, self.update_ai_response, ai_response)

        except Exception as e:
            # 显示错误信息
            error_msg = f"API调用失败: {str(e)}"
            self.root.after(0, self.update_ai_response, error_msg)

    def update_ai_response(self, response):
        """更新AI回复到界面"""
        # 删除"正在思考..."消息
        self.chat_display.config(state=tk.NORMAL)
        last_line_start = self.chat_display.index("end-2l linestart")
        self.chat_display.delete(last_line_start, tk.END)
        self.chat_display.config(state=tk.DISABLED)

        # 显示实际回复
        self.add_message_to_display("ai", response)

        # 重新启用发送按钮
        self.send_btn.config(state=tk.NORMAL)

    def clear_chat(self):
        """清空对话历史和显示"""
        # 清空显示区域
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)

        # 重置对话历史
        self.chat_history = []

        messagebox.showinfo("提示", "对话已清空")


if __name__ == "__main__":
    # 创建主窗口并运行应用
    root = tk.Tk()
    app = DeepSeekChatUI(root)
    root.mainloop()
