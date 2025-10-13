import tkinter as tk
from tkinter import messagebox, filedialog
import os
import subprocess

# 创建主窗口
root = tk.Tk()
root.title("简单UI界面")  # 窗口标题
root.geometry("400x300")  # 窗口大小（宽x高）

# 添加标签
label = tk.Label(root, text="欢迎使用我的第一个UI界面", font=("abc", 12))
label.pack(pady=20)  # 放置标签，设置上下边距


# 定义按钮点击事件
def on_click():
    messagebox.showinfo("提示", "按钮被点击了！")  # 弹出提示框


# 添加按钮
button = tk.Button(root, text="点击我", command=on_click, width=15, height=2)
button.pack(pady=10)

# 添加输入框
entry = tk.Entry(root, width=30)
entry.pack(pady=10)
entry.insert(0, "请输入文本...")  # 默认提示文本


# 定义打开文本文档的函数
def open_text_file():
    # 弹出文件选择对话框
    file_path = filedialog.askopenfilename(
        title="选择文本文档",
        filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
    )

    if file_path:  # 如果选择了文件
        try:
            # 根据操作系统打开文件
            if os.name == 'nt':  # Windows系统
                os.startfile(file_path)
            else:  # macOS或Linux系统
                subprocess.run(['open' if os.name == 'posix' else 'xdg-open', file_path])
            messagebox.showinfo("成功", f"已打开文件：{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"打开文件失败：{str(e)}")


# 添加打开文件按钮
file_button = tk.Button(root, text="打开文本文档", command=open_text_file, width=15, height=2)
file_button.pack(pady=10)

# 启动主循环（显示窗口）
root.mainloop()
