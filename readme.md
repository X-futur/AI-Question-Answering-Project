# AI 智能问答系统

基于 FastAPI 构建的多功能 AI 问答平台，集成大语言模型（Qwen）、图像生成（通义万相）、图像识别（Qwen-VL）、联网搜索及邮件发送等功能，提供流式响应的 Web 交互界面。

## 功能特性

- **智能问答** — 基于 Qwen-Plus 模型提供文本对话，支持流式输出（打字机效果）
- **图像生成** — 调用通义万相（Wanx2.1/Wan2.7）文生图模型，生成并展示图像
- **图像识别** — 上传图片后通过 Qwen-VL 多模态模型识别并描述图像内容
- **联网搜索** — 通过阿里云 OpenSearch 搜索引擎获取实时信息，辅助大模型回答
- **邮件发送** — 大模型通过 Function Calling 自动识别用户意图，调用 SMTP 发送邮件
- **语音朗读** — 前端集成 Web Speech API，支持将 AI 回复转为语音朗读

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 后端框架 | Python FastAPI |
| 大模型 API | 阿里云 Dashscope（通义千问 Qwen-Plus、Qwen3.7-Plus、通义万相 Wanx/Wan2.7） |
| 搜索引擎 | 阿里云 OpenSearch 联网搜索 |
| 邮件服务 | QQ 邮箱 SMTP |
| 前端 | 原生 HTML + CSS + JavaScript |
| 语音合成 | 浏览器 Web Speech API |

## 项目结构

```
AI-Question-Answering-Project/
├── templates/
│   └── chat.html          # 前端聊天界面
├── static/
│   ├── script.js          # 前端交互逻辑（流式渲染、图像上传、朗读控制等）
│   ├── style.css          # 界面样式
│   └── images/            # 生成的图像文件（运行时动态创建）
├── qa.py                  # 智能问答路由（流式对话 + 联网搜索 + Function Calling）
├── generate.py            # 图像生成路由（调用通义万相 API）
├── recognize.py           # 图像识别路由（调用 Qwen-VL 多模态模型）
├── func_calling.py        # 邮件发送功能 + 函数调用描述（供大模型使用）
├── model.py               # 阿里云 OpenSearch 联网搜索封装
├── test.py                # 图像生成测试（通义万相 v2 备选实现）
├── readme.md              # 项目说明文档
├── .env                   # API 密钥配置（不纳入版本控制）
├── .gitignore             # Git 忽略规则
└── LICENSE                # MIT 开源许可证
```

## 快速开始

### 1. 环境要求

- Python 3.10+
- pip / uv / conda
- （可选）虚拟环境

### 2. 安装依赖

```bash
pip install fastapi uvicorn python-multipart openai dashscope python-dotenv requests
```
安装 Jinja2：`pip install jinja2`

核心依赖说明：

| 包名 | 用途 |
| --- | --- |
| `fastapi` + `uvicorn` | Web 服务器框架 |
| `openai` | OpenAI 兼容 SDK（访问 Dashscope 大模型） |
| `dashscope` | 阿里云 Dashscope SDK（图像生成） |
| `python-dotenv` | 环境变量加载 |
| `python-multipart` | FastAPI 表单数据解析 |
| `requests` | HTTP 请求（下载图像、调用搜索 API） |

### 3. 配置环境变量

复制或编辑 `.env` 文件：

```env
Dashscope_API_Key = "your-dashscope-api-key"
Aliyun_Search_Key = "your-opensearch-api-key"
QQ_Mail_Password = "your-qq-smtp-authorization-code"
```

- **Dashscope_API_Key** — 阿里云大模型服务 API Key，[获取地址](https://dashscope.aliyun.com/)
- **Aliyun_Search_Key** — 阿里云 OpenSearch 联网搜索 API Key
- **QQ_Mail_Password** — QQ 邮箱 SMTP 授权码（用于 `func_calling.py` 发送邮件）

### 4. 启动服务

启动命令：

```bash
python main.py
```

然后访问 `http://127.0.0.1:8000/` 即可。
访问 `http://127.0.0.1:8000/docs` 即可查看 `SwaggerUI` 接口文档

## 核心设计说明

### 流式输出（Server-Sent Events）

前端通过 Fetch API 的 `ReadableStream` 读取后端生成器（Generator）发出的增量文本，实现打字机效果。每个 chunk 以 `\n` 分隔的 JSON 字符串形式传输。

### Function Calling 邮件发送

- 用户输入提问后，后端先调用 Qwen-Plus 模型（非流式模式）检测是否存在 function call
- 若模型识别出用户需要发送邮件，则返回 `send_email` 函数调用声明
- 后端解析出收件人、正文、标题等参数并执行 `func_calling.send_email()`
- 将执行结果回传给模型，模型据此组织自然语言回复，流式输出给用户

### 联网搜索

当用户勾选"联网"选项时，请求携带 `search: true`，后端先调用阿里云 OpenSearch 获取搜索结果摘要（设为 `way: "full"` 模式以大模型过滤），再将结果作为 context 拼入提示词供大模型参考回答。

### 多模态识别

图像识别使用阿里云专属部署的 Qwen3.7-Plus 模型（通过专有 endpoint 访问），前端将图像转为 Base64 后通过 API 上传，模型同时接收图像和文本提示词，返回流式描述。

## License

MIT License — 详见 [LICENSE](./LICENSE)
