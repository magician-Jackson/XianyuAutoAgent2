# Xianyu AutoAgent

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![LLM Powered](https://img.shields.io/badge/LLM-powered-FF6F61)](https://platform.openai.com/)

一个用于闲鱼消息自动回复的 Python 项目，支持：

- 自动连接闲鱼消息 WebSocket
- 基于商品信息和历史上下文生成回复
- 本地反代和云端 API 两种 LLM 接入方式
- 启动时选择本次运行使用的 LLM 模式
- 自动打开闲鱼消息页登录、等待滑块验证、校验 Cookie 可用性

本项目基于 [shaxiu/XianyuAutoAgent](https://github.com/shaxiu/XianyuAutoAgent) 二次开发。

## 功能概览

- 多 Agent 回复策略：分类、议价、技术、默认回复
- SQLite 持久化会话上下文和商品信息
- 支持人工接管 / 自动回复切换
- 支持本地 OpenAI 兼容反代
- 每次运行 `python main.py` 都会强制重新登录闲鱼消息页

## 环境要求

- Python 3.8+
- 已安装 Edge 或 Chrome

如果本机没有可用浏览器内核，安装依赖后再执行：

```bash
playwright install chromium
```

## 安装

```bash
git clone https://github.com/magician-Jackson/XianyuAutoAgent2.git
cd XianyuAutoAgent2
pip install -r requirements.txt
```

复制环境变量模板：

```bash
cp .env.example .env
```

Windows 也可以直接手动复制一份 `.env.example` 为 `.env`。

## `.env` 配置

### 1. LLM 接入模式

项目支持四种值：

- `proxy`：本地反代
- `api`：云端 / 官方 OpenAI 兼容接口
- `qclaw`：仓库里的 QClaw 模式
- `auto`：兼容旧配置，自动判断

推荐在 `.env` 里保留默认值：

```env
LLM_PROVIDER=auto
```

然后在运行 `python main.py` 时再选择本次使用：

- `1` 本地反代
- `2` 云端 API
- `3` 使用 `.env` 默认值

### 2. 云端 API 配置

例如百炼 / 其他 OpenAI 兼容平台：

```env
API_KEY=your_api_key_here
API_MODEL_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
API_MODEL_NAME=qwen-max
```

### 3. 本地反代配置

例如 CLIProxy / 本地 OpenAI 兼容网关：

```env
LOCAL_PROXY_API_KEY=openclaw-local-key
LOCAL_PROXY_BASE_URL=http://127.0.0.1:8317/v1
LOCAL_PROXY_MODEL_NAME=gpt-5.3-codex
```

### 4. 兼容旧配置

以下变量仍然保留，用于兼容旧版配置：

```env
MODEL_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL_NAME=qwen-max
```

### 5. 闲鱼登录配置

```env
COOKIES_STR=your_cookies_here
```

现在通常不需要手工填写真实 Cookie。程序启动时会自动清空旧 Cookie，然后打开闲鱼消息页让你重新登录。

### 6. 其他可选项

```env
TOGGLE_KEYWORDS=。
SIMULATE_HUMAN_TYPING=False
```

## 运行流程

直接运行：

```bash
python main.py
```

当前版本的启动流程是：

1. 读取 `.env`
2. 让你选择本次运行使用 `proxy`、`api` 或 `.env` 默认值
3. 初始化 LLM 客户端
4. 清空旧 `COOKIES_STR`
5. 清空浏览器登录缓存 `data/browser_profile/`
6. 自动打开闲鱼消息页：

```text
https://www.goofish.com/im?spm=a21ybx.home.sidebar.2.4c053da6K6mu08
```

7. 你在浏览器里扫码登录
8. 如果出现滑块，在消息页完成验证
9. 程序会反复校验 Cookie 是否真的能换到 `accessToken`
10. 校验成功后自动写回 `.env`，然后开始连接 WebSocket

## 闲鱼登录说明

这版代码不是“拿到任意 Cookie 就算成功”，而是会做两层校验：

- 必须已经进入闲鱼消息页
- 必须通过滑块 / 风控，Cookie 真正能够调用 `mtop.taobao.idlemessage.pc.login.token`

只有通过校验的 Cookie 才会被保存。

如果运行过程中再次触发风控，程序也会尝试重新打开消息页让你重新登录或过滑块。

## 目录说明

- `main.py`：主入口，负责启动、WebSocket、消息处理
- `browser_cookie_login.py`：浏览器登录、消息页风控校验、Cookie 刷新
- `XianyuApis.py`：闲鱼接口调用与 token 获取
- `XianyuAgent.py`：LLM 路由和回复生成
- `context_manager.py`：SQLite 上下文存储
- `prompts/`：各类提示词
- `utils/`：工具函数

## 常见场景

### 使用本地反代

`.env` 示例：

```env
LLM_PROVIDER=auto
LOCAL_PROXY_API_KEY=openclaw-local-key
LOCAL_PROXY_BASE_URL=http://127.0.0.1:8317/v1
LOCAL_PROXY_MODEL_NAME=gpt-5.3-codex
```

启动时输入：

```text
1
```

### 使用云端 API

`.env` 示例：

```env
LLM_PROVIDER=auto
API_KEY=你的真实API_KEY
API_MODEL_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
API_MODEL_NAME=qwen-max
```

启动时输入：

```text
2
```

## 提示词自定义

你可以直接修改：

- `prompts/classify_prompt.txt`
- `prompts/price_prompt.txt`
- `prompts/tech_prompt.txt`
- `prompts/default_prompt.txt`

## 注意事项

- 本项目仅供学习和交流使用
- 闲鱼风控策略可能随时变化
- 启动时会强制重新登录，因此不会复用上一次运行的登录态
- `data/browser_profile/` 为临时浏览器登录缓存，已加入 `.gitignore`

## 致谢

- [shaxiu/XianyuAutoAgent](https://github.com/shaxiu/XianyuAutoAgent)
