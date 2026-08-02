# deepseek-chat-python
# DeepSeek 智能助手

一个基于 DeepSeek API 的桌面聊天客户端，支持知识库加载、流式回复、多轮对话，使用 Python + Tkinter 构建，轻量易用。

## 功能特性

- **流式回复**：打字机效果，实时显示 AI 输出
- **知识库加载**：自动读取 `knowledge_base/` 文件夹中的 TXT 文件作为专属知识库
- **多轮对话**：自动保留上下文，支持连续对话
- **自动滚动控制**：AI 回复时可暂停/恢复自动滚动，方便阅读
- **深色护眼 UI**：低亮度界面设计 + 高亮光标，长时间使用不疲劳

## 项目结构

├── main.py                # 主程序入口
├── config.py              # 配置文件（读取环境变量）
├── requirements.txt       # 依赖清单
├── .env          # 环境变量模板（填入你自己的 API Key）
└── README.md              # 项目说明

## 安装与运行

1. 克隆项目

   git clone https://github.com/UinChen/deepseek-chat-python.git
   cd deepseek-chat-python

2. 安装依赖

   pip install -r requirements.txt

3. 配置 API Key

   打开项目根目录下的 `.env` 文件，把 `your key` 替换成你自己的 DeepSeek API Key：

   DEEPSEEK_API_KEY=your key   ← 在这里填入你的真实密钥
   BASE_URL=https://api.deepseek.com
   MODEL=deepseek-v4-flash

4. 启动

   python main.py

## 使用说明

- 启动后，在底部输入框输入问题，点击「发送」或按回车键
- AI 回复过程中，点击「暂停滚动」可停止自动滑动，方便查看上文
- 点击「清空历史」可清除当前对话记录，开始新会话

## 常见问题

**Q：提示 `请配置 DEEPSEEK_API_KEY`？**

A：请检查项目根目录下是否存在 `.env` 文件，并确认其中 `DEEPSEEK_API_KEY` 已填入真实密钥。

**Q：提示 `ModuleNotFoundError: No module named 'openai'`？**

A：请先运行 `pip install -r requirements.txt` 安装所有依赖。

**Q：知识库没有生效？**

A：在项目根目录下创建 `knowledge_base/` 文件夹，放入 `.txt` 文件，重启程序后会自动加载。

## 技术栈

- Python 3
- Tkinter（GUI）
- OpenAI SDK（DeepSeek 兼容接口）
- python-dotenv（环境变量管理）

## 许可证

MIT License
