# 个人智识库

> 智能 + 知识 = 智识库

一个简易的私人知识库，随时随地记录你的想法和知识，AI 智能检索让你的知识触手可及。

## 特点

- 📝 **随时记录** - 随时随地记录想法、笔记、知识
- 🔍 **智能检索** - AI 语义搜索，快速找到你需要的内容
- 🤖 **AI 对话** - 与 AI 聊天，基于你的知识库回答问题
- 📄 **文件解析** - 支持 PDF、Word、Excel、PPT 文档导入
- 🖼️ **图片识别** - 拍照或上传图片，AI 自动识别内容
- 🌐 **联网搜索** - AI 联网获取最新信息
- ☁️ **云端同步** - 数据云端存储，多端同步

## 技术栈

**前端：** UniApp (Vue 3) - 支持 H5、微信小程序、App

**后端：** FastAPI + PostgreSQL + pgvector + Redis

## 一键部署

**国内服务器（推荐）：**
```bash
curl -fsSL https://gitee.com/2201_75827989/zhi_shi_ku/raw/main/deploy-cn.sh | bash
```

**国外服务器：**
```bash
curl -fsSL https://raw.githubusercontent.com/adminhuan/ai-knowledge-base/main/deploy.sh | bash
```

自动安装 Docker、Python，克隆项目并启动数据库。国内版已配置阿里云 Docker 镜像 + 清华 pip 镜像。

## 手动部署

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

使用 HBuilderX 打开项目，运行到浏览器或其他平台

## 环境变量

| 变量 | 说明 | 申请地址 |
|------|------|----------|
| `ZHIPU_API_KEY` | 智谱 AI（对话+视觉+向量） | https://open.bigmodel.cn/ |
| `QWEN_API_KEY` | 通义千问（联网搜索+文件解析） | https://dashscope.console.aliyun.com/ |
| `COS_SECRET_ID/KEY` | 腾讯云 COS（文件存储） | https://console.cloud.tencent.com/cos |

## 使用的 AI 模型

| 功能 | 模型 | 费用 |
|------|------|------|
| 对话 | GLM-4-Flash | 免费 |
| 视觉识别 | GLM-4V-Flash | 免费 |
| 向量检索 | Embedding-2 | 付费 |
| 联网搜索 | Qwen-Turbo | 有免费额度 |
| 文件解析 | Qwen-Doc-Turbo | 有免费额度 |

## License

MIT
