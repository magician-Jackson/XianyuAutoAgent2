# 🚀 Xianyu AutoAgent - 智能闲鱼客服机器人系统

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/) [![LLM Powered](https://img.shields.io/badge/LLM-powered-FF6F61)](https://platform.openai.com/)

专为闲鱼平台打造的AI值守解决方案，实现闲鱼平台7×24小时自动化值守，支持多专家协同决策、智能议价和上下文感知对话。

> 本项目基于 [shaxiu/XianyuAutoAgent](https://github.com/shaxiu/XianyuAutoAgent) 二次开发，新增 CLIProxy 反代支持。

## 🌟 核心特性

### 智能对话引擎

| 功能模块 | 技术实现 | 关键特性 |
| --- | --- | --- |
| 上下文感知 | 会话历史存储 | 轻量级对话记忆管理，完整对话历史作为LLM上下文输入 |
| 专家路由 | LLM prompt+规则路由 | 基于提示工程的意图识别 → 专家Agent动态分发，支持议价/技术/客服多场景切换 |

### 业务功能矩阵

| 模块 | 已实现 | 规划中 |
| --- | --- | --- |
| 核心引擎 | ✅ LLM自动回复 / ✅ 上下文管理 | 🔄 情感分析增强 |
| 议价系统 | ✅ 阶梯降价策略 | 🔄 市场比价功能 |
| 技术支持 | ✅ 网络搜索整合 | 🔄 RAG知识库增强 |
| 运维监控 | ✅ 基础日志 | 🔄 钉钉集成 / 🔄 Web管理界面 |

## 🚴 快速开始

### 环境要求

- Python 3.8+

### 安装步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/magician-Jackson/XianyuAutoAgent2.git
cd XianyuAutoAgent2
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量

复制 `.env.example` 为 `.env`，然后根据你的情况修改配置：

```bash
cp .env.example .env
```

`.env` 文件说明：

| 变量名 | 必填 | 说明 |
| --- | --- | --- |
| `API_KEY` | ✅ | API Key，通过模型平台获取；若使用 CLIProxy 反代，填写反代提供的 Key |
| `COOKIES_STR` | ✅ | 闲鱼网页端 Cookie（获取方式见下方说明） |
| `MODEL_BASE_URL` | ✅ | 模型 API 地址（默认通义千问） |
| `MODEL_NAME` | ✅ | 模型名称（默认 `qwen-max`） |
| `TOGGLE_KEYWORDS` | ❌ | 人工接管切换关键词，默认为中文句号 `。`（卖家发送该关键词切换人工/AI接管模式） |
| `SIMULATE_HUMAN_TYPING` | ❌ | 是否模拟人工打字延迟，`True` / `False`（默认 `False`） |

**如何获取闲鱼 Cookie（COOKIES_STR）：**

1. 打开浏览器，登录 [闲鱼网页版](https://www.goofish.com/)
2. 按 `F12` 打开开发者工具
3. 切换到 **Network（网络）** 选项卡
4. 点击 **Fetch/XHR** 过滤器
5. 在闲鱼页面上随意操作（如点击消息），触发一个网络请求
6. 点击任意一个请求，在 **Headers（请求头）** 中找到 `Cookie` 字段
7. 复制完整的 Cookie 值，粘贴到 `.env` 文件的 `COOKIES_STR` 中

#### 4. 配置提示词文件（可选）

项目中的 `prompts/` 目录下已内置默认提示词模板，可直接使用。如需自定义，编辑对应文件即可：

| 文件 | 用途 |
| --- | --- |
| `prompts/classify_prompt.txt` | 意图分类提示词 |
| `prompts/price_prompt.txt` | 议价专家提示词 |
| `prompts/tech_prompt.txt` | 技术专家提示词 |
| `prompts/default_prompt.txt` | 默认回复提示词 |

### 使用方法

运行主程序：

```bash
python main.py
```

启动后程序会自动连接闲鱼 WebSocket，监听买家消息并通过 LLM 自动回复。

- 卖家发送 `。`（中文句号）可切换为 **人工接管模式**，再次发送切换回 **AI 接管模式**
- 支持自动识别买家意图，分发给对应专家（议价 / 技术 / 默认客服）

---

## 🔌 使用 CLIProxy 反代（免费调用大模型）

如果你没有模型平台的 API Key，可以通过 CLIProxy 等本地反代工具，将大模型服务转发为 OpenAI 兼容接口。

### 配置步骤

1. 启动你的 CLIProxy 服务，记下终端输出的 **API 地址** 和 **API Key**，例如：

   ```text
   API 地址: http://127.0.0.1:8317/v1
   API Key:  openclaw-local-key
   ```

2. 修改 `.env` 文件：

   ```env
   API_KEY=openclaw-local-key
   MODEL_BASE_URL=http://127.0.0.1:8317/v1
   MODEL_NAME=gpt-5.3-codex
   ```

3. 正常运行即可，程序会自动通过反代调用模型：

   ```bash
   python main.py
   ```

### 兼容性说明

本项目兼容所有 OpenAI 格式的 API 接口，包括但不限于：

- 阿里百炼（通义千问）：`https://dashscope.aliyuncs.com/compatible-mode/v1`
- CLIProxy 本地反代：`http://127.0.0.1:8317/v1`
- 其他 OpenAI 兼容服务（如 LM Studio、Ollama 等）

---

## 自定义提示词

可以通过编辑 `prompts` 目录下的文件来自定义各个专家的提示词：

- `classify_prompt.txt` - 意图分类提示词
- `price_prompt.txt` - 价格专家提示词
- `tech_prompt.txt` - 技术专家提示词
- `default_prompt.txt` - 默认回复提示词

## 🤝 参与贡献

欢迎通过 Issue 提交建议或 PR 贡献代码。

## 🛡 注意事项

- 本项目仅供学习与交流，请勿用于商业用途
- 本项目基于 [shaxiu/XianyuAutoAgent](https://github.com/shaxiu/XianyuAutoAgent) 二次开发
- 鉴于项目的特殊性，可能在任何时间停止更新或删除项目
