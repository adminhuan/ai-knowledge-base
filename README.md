# AI 知识库助手

一个基于 UniApp + FastAPI 的智能知识库管理系统，支持 AI 对话、知识检索、文件解析等功能。

## 功能特性

- 🤖 **AI 对话** - 支持多种大模型（智谱GLM、通义千问等）
- 📚 **知识库管理** - 支持知识的增删改查、分类、标签
- 🔍 **语义搜索** - 基于向量的智能知识检索
- 📄 **文件解析** - 支持 PDF、Word、Excel、PPT 等文档解析
- 🖼️ **图片识别** - 支持图片内容识别和分析
- 🌐 **联网搜索** - 支持实时联网获取最新信息
- ☁️ **云端存储** - 支持腾讯云 COS 文件存储
- 🔐 **用户系统** - 支持注册、登录、个人设置

## 技术栈

**前端：**
- UniApp (Vue 3)
- 支持 H5、微信小程序、App

**后端：**
- FastAPI (Python 3.10+)
- PostgreSQL + pgvector (向量数据库)
- Redis (缓存)

## 快速开始

### 1. 启动数据库

```bash
docker-compose up -d
```

### 2. 配置环境变量

```bash
cd server
cp .env.example .env
# 编辑 .env 填入你的 API 密钥
```

### 3. 启动后端

```bash
cd server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### 4. 启动前端

```bash
# 使用 HBuilderX 打开项目
# 运行到浏览器或其他平台
```

## 环境变量说明

| 变量 | 说明 | 申请地址 |
|------|------|----------|
| `ZHIPU_API_KEY` | 智谱 AI 密钥（对话+向量+视觉） | https://open.bigmodel.cn/ |
| `QWEN_API_KEY` | 通义千问密钥（联网搜索+文件解析） | https://dashscope.console.aliyun.com/ |
| `COS_SECRET_ID/KEY` | 腾讯云 COS 密钥 | https://console.cloud.tencent.com/cos |

## 项目结构

```
├── api/                 # 前端 API 封装
├── components/          # 前端组件
├── pages/               # 前端页面
├── server/              # 后端代码
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据模型
│   │   └── services/    # 业务服务
│   ├── main.py          # 入口文件
│   └── requirements.txt
├── static/              # 静态资源
└── docker-compose.yml   # Docker 配置
```

## 免费模型推荐

本项目默认使用以下免费模型：

- **智谱 GLM-4-Flash** - 对话模型（免费）
- **智谱 GLM-4V-Flash** - 视觉模型（免费）
- **智谱 Embedding-2** - 向量模型（免费）
- **通义 Qwen-Turbo** - 联网搜索（有免费额度）
- **通义 Qwen-Doc-Turbo** - 文件解析（有免费额度）

## License

MIT
