import os
import json
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from openai import OpenAI
HISTORY_FILE = "chat_history.json"
KNOWLEDGE_FOLDER = "knowledge_base"
from config import API_KEY, BASE_URL, MODEL# 加载配置
# ==================== 加载知识库 ====================
def load_knowledge_base(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return None

    all_content = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.txt'):
            file_path = os.path.join(folder_path, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    all_content.append(f"\n【文件：{file_name}】\n{content}\n")
                print(f"✅ 已加载知识库：{file_name}")
            except Exception as e:
                print(f"⚠️ 加载失败 {file_name}：{e}")

    return "\n".join(all_content) if all_content else None


knowledge_content = load_knowledge_base(KNOWLEDGE_FOLDER)

if knowledge_content:
    SYSTEM_PROMPT = f"""你是我的专属AI助手。

## 我的个人知识库（请优先使用这些信息）：
{knowledge_content}

## 规则：
1. 当问到关于我个人、经历、心得、笔记等内容时，从上面的知识库中找答案
2. 如果知识库里有，直接回答
3. 如果知识库里没有，才用你自己的知识
4. 回答要简洁、准确
"""
else:
    SYSTEM_PROMPT = "你是我的AI助手，回答简洁准确。"


# ==================== 对话类 ====================
class DeepSeekChat:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        self.model = MODEL
        self.messages = []
        self.history_file = HISTORY_FILE
        self.load_history()

        if not self.messages:
            self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            self.save_history()
            print("✨ 新会话已创建")
        else:
            # 更新系统提示词
            self.messages[0] = {"role": "system", "content": SYSTEM_PROMPT}
            self.save_history()
            print(f"📂 已加载 {len(self.messages)} 条历史消息")

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.messages = json.load(f)
                print("✅ 已加载历史记录")
            except:
                pass

    def save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
        except:
            pass

    def clear_history(self):
        system_msg = self.messages[0] if self.messages else {"role": "system", "content": SYSTEM_PROMPT}
        self.messages = [system_msg]
        self.save_history()
        print("🗑️ 历史已清空")

    def chat_stream(self, user_input, callback):
        """流式对话"""
        self.messages.append({"role": "user", "content": user_input})
        self.save_history()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                stream=True,
                temperature=0.7
            )

            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    callback(content, False)  # 未完成

            if full_response:
                self.messages.append({"role": "assistant", "content": full_response})
                self.save_history()

            callback("", True)  # 完成

        except Exception as e:
            callback(f"\n[错误：{str(e)}]", True)


# ==================== UI 界面 ====================
class DeepSeekUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DeepSeek 智能助手")
        self.root.withdraw()  # 隐藏
        self.root.geometry("1000x600")

        # 新增：窗口居中
        self.root.update_idletasks()  # 确保窗口大小完全生效
        win_width = self.root.winfo_width()
        win_height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - win_width) // 2
        y = (screen_height - win_height) // 2
        self.root.geometry(f"{win_width}x{win_height}+{x}+{y}")

        # 初始化聊天
        self.chat = DeepSeekChat()
        self.is_responding = False
        self.auto_scroll = True  # 是否自动滚动到底部

        # 设置UI
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 显示欢迎
        self.display_welcome()
        # 关键：显示窗口（此时已在居中位置）
        self.root.deiconify()

    def setup_ui(self):
        # 显示区域
        self.display = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, font=("微软雅黑", 11),
            bg="#1e1e2e", fg="#cdd6f4", padx=10, pady=10,
            insertbackground="#00e5ff",  # 光标改为亮青色
            selectbackground="#45475a"  # 选中文字的背景色
        )
        self.display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.display.tag_config("user", foreground="#89b4fa")
        self.display.tag_config("ai", foreground="#a6e3a1")
        self.display.tag_config("system", foreground="#f9e2af")

        # 绑定鼠标滚轮事件，用户滚动时自动暂停自动滚动
        self.display.bind("<MouseWheel>", self.on_mouse_wheel)

        # 输入框
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.input_entry = tk.Text(
            input_frame, height=4, font=("微软雅黑", 11),
            bg="#313244", fg="#ffffff", wrap=tk.WORD,
            insertbackground="#00e5ff",  # 光标改为亮青色
            selectbackground="#45475a"  # 选中文字的背景色
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # 按钮容器
        btn_frame = tk.Frame(input_frame)
        btn_frame.pack(side=tk.RIGHT)

        # 暂停/恢复滚动按钮
        self.scroll_btn = tk.Button(
            btn_frame, text="⏸ 暂停滚动", font=("微软雅黑", 10),
            command=self.toggle_auto_scroll, width=10
        )
        self.scroll_btn.pack(side=tk.TOP, pady=(0, 5))

        self.send_btn = tk.Button(
            btn_frame, text="发送", font=("微软雅黑", 11),
            command=self.send_message, width=9, height=1
        )
        self.send_btn.pack(side=tk.BOTTOM)

        # 绑定回车
        self.input_entry.bind("<Return>", self.on_enter)
        self.input_entry.bind("<Control-Return>", lambda e: None)

        # 底部按钮
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        clear_btn = tk.Button(bottom_frame, text="清空历史", command=self.clear_history)
        clear_btn.pack(side=tk.LEFT)

        status = "✅ 知识库已加载" if knowledge_content else "⚠️ 知识库为空"
        self.status_label = tk.Label(bottom_frame, text=status, fg="gray")
        self.status_label.pack(side=tk.RIGHT)

        self.input_entry.focus()

    def on_mouse_wheel(self, event):
        """用户滚动鼠标滚轮时，暂停自动滚动"""
        self.auto_scroll = False
        self.scroll_btn.config(text="▶ 恢复滚动")

    def toggle_auto_scroll(self):
        """切换自动滚动状态"""
        self.auto_scroll = not self.auto_scroll
        if self.auto_scroll:
            self.scroll_btn.config(text="⏸ 暂停滚动")
            # 立刻滚到底部
            self.display.see(tk.END)
        else:
            self.scroll_btn.config(text="▶ 恢复滚动")

    def display_welcome(self):
        self.display.insert(tk.END, "✨ DeepSeek 智能助手\n", "system")
        self.display.insert(tk.END, "=" * 30 + "\n\n", "system")
        if knowledge_content:
            self.display.insert(tk.END, "📚 知识库已加载\n", "system")
            self.display.insert(tk.END, "💡 请问有什么需要帮助\n\n", "system")

    def on_enter(self, event):
        if not event.state & 0x4:
            self.send_message()
            return "break"
        return None

    def send_message(self):
        if self.is_responding:
            messagebox.showwarning("提示", "AI正在回复中...")
            return

        user_input = self.input_entry.get("1.0", tk.END).strip()
        if not user_input:
            return

        # 清空输入框
        self.input_entry.delete("1.0", tk.END)

        # 显示用户消息
        self.display.insert(tk.END, f"\n你: {user_input}\n", "user")
        self.display.see(tk.END)

        # 显示AI标签
        self.display.insert(tk.END, "AI: ", "ai")
        self.ai_start = self.display.index(tk.END)

        # 禁用按钮
        self.is_responding = True
        self.send_btn.config(state=tk.DISABLED, text="思考中...")

        # 开线程
        thread = threading.Thread(target=self.get_response, args=(user_input,))
        thread.daemon = True
        thread.start()

    def get_response(self, user_input):
        def update_ui(content, is_done):
            self.root.after(0, lambda: self.append_text(content, is_done))

        self.chat.chat_stream(user_input, update_ui)

    def append_text(self, content, is_done):
        if content:
            self.display.insert(tk.END, content, "ai")
            # 只有开启自动滚动时才滚到底部
            if self.auto_scroll:
                self.display.see(tk.END)

        if is_done:
            self.display.insert(tk.END, "\n\n")
            if self.auto_scroll:
                self.display.see(tk.END)
            self.is_responding = False
            self.send_btn.config(state=tk.NORMAL, text="发送")

    def clear_history(self):
        if messagebox.askyesno("确认", "清空对话历史？"):
            self.chat.clear_history()
            self.display.delete(1.0, tk.END)
            self.display_welcome()

    def on_closing(self):
        self.chat.save_history()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = DeepSeekUI()
    app.run()