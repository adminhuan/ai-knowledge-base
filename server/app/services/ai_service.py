from typing import List, Optional, Dict, Any
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.core.config import settings
from app.core.redis import redis_client
from app.models.knowledge import Knowledge
from app.models.user import User
from app.services.web_scraper import web_scraper
import json
import httpx
import base64
import re


class AIService:
    def __init__(self):
        # 默认客户端 - 智谱AI（普通聊天 + Embedding + 视觉）
        self.client = AsyncOpenAI(
            api_key=settings.ZHIPU_API_KEY,
            base_url=settings.ZHIPU_BASE_URL
        )
        # 默认客户端 - 通义千问（联网搜索 + 文件解析）
        self.qwen_client = AsyncOpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_BASE_URL
        )
        # 视觉模型列表（轮换使用）
        self.vision_models = settings.VISION_MODELS.split(',')
        self.vision_model_index = 0
    
    def get_next_vision_model(self) -> str:
        """获取下一个视觉模型（轮换）"""
        model = self.vision_models[self.vision_model_index]
        self.vision_model_index = (self.vision_model_index + 1) % len(self.vision_models)
        return model
    
    async def get_user_ai_config(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """获取用户AI配置"""
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user and user.settings:
                settings_data = json.loads(user.settings) if isinstance(user.settings, str) else user.settings
                return settings_data.get('ai_config', {})
        except Exception as e:
            print(f"获取用户配置失败: {e}")
        return {}
    
    def get_client(self, base_url: str, api_key: str) -> AsyncOpenAI:
        """根据配置创建客户端"""
        return AsyncOpenAI(api_key=api_key, base_url=base_url)
    
    def calculate_cost(self, provider: str, model: str, input_tokens: int, output_tokens: int, cached_tokens: int = 0) -> int:
        """计算成本（返回单位：万分之一元）
        
        价格表（每百万token）：
        - 智谱 glm-4.5-flash: 免费
        - 智谱 glm-4-flash: 免费
        - 智谱 embedding-2: 0.5元/M
        - 通义 qwen-turbo: 输入0.3元/M 输出0.6元/M 缓存0.06元/M
        - 通义 qwen-flash: 输入0.15元/M 输出1.5元/M
        - DeepSeek chat: 输入1元/M 输出2元/M 缓存0.1元/M
        """
        # 价格配置（单位：元/百万token）
        PRICES = {
            'zhipu': {
                'glm-4.5-flash': {'input': 0, 'output': 0, 'cached': 0},
                'glm-4-flash': {'input': 0, 'output': 0, 'cached': 0},
                'glm-4-flash-250414': {'input': 0, 'output': 0, 'cached': 0},
                'glm-4v-flash': {'input': 0, 'output': 0, 'cached': 0},
                'glm-4.1v-thinking-flash': {'input': 0, 'output': 0, 'cached': 0},
                'embedding-2': {'input': 0.5, 'output': 0, 'cached': 0},
                'default': {'input': 0, 'output': 0, 'cached': 0}
            },
            'qwen': {
                'qwen-turbo': {'input': 0.3, 'output': 0.6, 'cached': 0.06},
                'qwen-flash': {'input': 0.15, 'output': 1.5, 'cached': 0.03},
                'qwen-plus': {'input': 0.8, 'output': 2, 'cached': 0.16},
                'qwen-max': {'input': 2, 'output': 6, 'cached': 0.4},
                'qwen-doc-turbo': {'input': 0.6, 'output': 1, 'cached': 0},
                'qwen-long': {'input': 0.5, 'output': 2, 'cached': 0},
                'qwen-vl-plus': {'input': 1.5, 'output': 1.5, 'cached': 0},
                'qwen-vl-max': {'input': 3, 'output': 3, 'cached': 0},
                'text-embedding-v3': {'input': 0.7, 'output': 0, 'cached': 0},
                'default': {'input': 0.3, 'output': 0.6, 'cached': 0.06}
            },
            'deepseek': {
                'deepseek-chat': {'input': 1, 'output': 2, 'cached': 0.1},
                'deepseek-reasoner': {'input': 4, 'output': 16, 'cached': 0.4},
                'default': {'input': 1, 'output': 2, 'cached': 0.1}
            },
            'openai': {
                'gpt-4o-mini': {'input': 1.1, 'output': 4.4, 'cached': 0.55},
                'gpt-4o': {'input': 18, 'output': 72, 'cached': 9},
                'text-embedding-3-small': {'input': 0.15, 'output': 0, 'cached': 0},
                'default': {'input': 1.1, 'output': 4.4, 'cached': 0.55}
            },
            'kimi': {
                'moonshot-v1-auto': {'input': 0, 'output': 0, 'cached': 0},  # 限时免费
                'default': {'input': 12, 'output': 12, 'cached': 0}
            }
        }
        
        # 获取价格
        provider_prices = PRICES.get(provider, PRICES.get('zhipu'))
        model_price = provider_prices.get(model, provider_prices.get('default'))
        
        # 计算非缓存的输入token
        non_cached_input = max(0, input_tokens - cached_tokens)
        
        # 计算成本（元）
        cost_yuan = (
            non_cached_input * model_price['input'] / 1000000 +
            output_tokens * model_price['output'] / 1000000 +
            cached_tokens * model_price['cached'] / 1000000
        )
        
        # 转换为万分之一元（保留精度）
        return int(cost_yuan * 10000)
    
    async def get_embedding(self, text: str, user_config: Dict[str, Any] = None) -> Optional[List[float]]:
        """获取文本的向量表示"""
        try:
            # 使用用户配置或默认配置
            if user_config and user_config.get('embedding_api_key'):
                client = self.get_client(
                    user_config.get('embedding_base_url', settings.ZHIPU_BASE_URL),
                    user_config.get('embedding_api_key')
                )
                model = user_config.get('embedding_model', settings.EMBEDDING_MODEL)
            else:
                client = self.client
                model = settings.EMBEDDING_MODEL
            
            response = await client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding API 错误: {e}")
            return None
    
    async def search_knowledge(
        self, 
        db: AsyncSession, 
        user_id: int, 
        query: str, 
        limit: int = 5
    ) -> List[dict]:
        """搜索知识库（向量搜索 + 关键词搜索）"""
        results = []
        
        # 尝试向量搜索
        query_embedding = await self.get_embedding(query)
        if query_embedding is not None:
            try:
                embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
                sql = text("""
                    SELECT id, title, content, summary, tags, 
                           1 - (embedding <=> cast(:embedding as vector)) as similarity
                    FROM knowledge
                    WHERE user_id = :user_id AND status = 1 AND embedding IS NOT NULL
                    ORDER BY embedding <=> cast(:embedding as vector)
                    LIMIT :limit
                """)
                result = await db.execute(sql, {
                    "embedding": embedding_str,
                    "user_id": user_id,
                    "limit": limit
                })
                rows = result.fetchall()
                for row in rows:
                    if row.similarity > 0.7:
                        results.append({
                            "id": row.id,
                            "title": row.title,
                            "content": row.content,
                            "similarity": round(row.similarity, 3)
                        })
            except Exception as e:
                print(f"向量搜索失败: {e}")
                await db.rollback()
        
        # 关键词搜索作为补充
        if len(results) < limit:
            try:
                # 提取关键词
                keywords = [w for w in query.replace('？', '').replace('?', '').split() if len(w) >= 2]
                if not keywords:
                    keywords = [query[:10]]
                
                keyword_sql = text("""
                    SELECT id, title, content, summary, tags
                    FROM knowledge
                    WHERE user_id = :user_id AND status = 1
                    AND (title ILIKE :kw OR content ILIKE :kw)
                    LIMIT :limit
                """)
                
                for kw in keywords[:3]:
                    result = await db.execute(keyword_sql, {
                        "user_id": user_id,
                        "kw": f"%{kw}%",
                        "limit": limit
                    })
                    rows = result.fetchall()
                    for row in rows:
                        if not any(r["id"] == row.id for r in results):
                            results.append({
                                "id": row.id,
                                "title": row.title,
                                "content": row.content,
                                "similarity": 0.8
                            })
            except Exception as e:
                print(f"关键词搜索失败: {e}")
                await db.rollback()
        
        return results[:limit]
    
    async def chat(
        self,
        db: AsyncSession,
        user_id: int,
        conversation_id: int,
        message: str,
        use_knowledge: bool = False,
        web_search: bool = False
    ) -> dict:
        """AI对话（带知识库RAG + 可选联网搜索 + 网页抓取）"""
        
        # 获取用户AI配置
        user_config = await self.get_user_ai_config(db, user_id)
        
        # 0. 检测是否包含URL，如果有则抓取网页内容
        url = web_scraper.extract_url(message)
        web_content = ""
        if url:
            print(f"[DEBUG] 检测到URL: {url}")
            result = await web_scraper.fetch_url(url)
            print(f"[DEBUG] 抓取结果: success={result['success']}, title={result.get('title', '')}, content_len={len(result.get('content', ''))}")
            if result['success']:
                web_content = f"\n\n【网页内容】\n标题: {result['title']}\n网址: {result['url']}\n\n{result['content']}"
                print(f"[DEBUG] web_content 长度: {len(web_content)}")
                # 检查是否包含免费模型关键词
                if 'GLM-4.5-Flash' in result.get('content', ''):
                    print("[DEBUG] ✅ 内容包含 GLM-4.5-Flash")
                else:
                    print("[DEBUG] ❌ 内容不包含 GLM-4.5-Flash")
            else:
                web_content = f"\n\n【网页抓取失败】{result['error']}"
                print(f"[DEBUG] 抓取失败: {result['error']}")
        
        # 1. 获取聊天上下文
        context_messages = await redis_client.get_chat_context(user_id, conversation_id)
        
        # 2. 检索知识库
        references = []
        knowledge_context = ""
        should_search = False
        
        # 检测是否包含查找关键词
        search_keywords = ['查找', '查一下', '帮我查', '搜索', '搜一下', '找一下', '找找', '查询', '检索', '有没有保存', '保存过']
        has_search_keyword = any(kw in message for kw in search_keywords)
        
        if not web_search and not url:
            if use_knowledge:
                # 用户点了知识库按钮 → 强制检索
                should_search = True
            elif user_config.get('enable_rag', False) and has_search_keyword:
                # 开启了自动检索 + 包含查找关键词 → 检索
                should_search = True
        
        if should_search:
            try:
                references = await self.search_knowledge(db, user_id, message)
                if references:
                    knowledge_context = "\n\n相关知识参考：\n" + "\n".join([
                        f"- {ref['title']}: {ref['content']}"
                        for ref in references[:3]
                    ])
            except Exception as e:
                print(f"知识库检索失败: {e}")
        
        # 3. 构建消息
        if url and web_content:
            # 预处理：提取免费模型信息
            free_models_hint = ""
            if '免费' in message or 'free' in message.lower():
                # 查找所有包含"免费模型"的行
                lines = web_content.split('\n')
                free_models = []
                for line in lines:
                    if '免费模型' in line and '|' in line:
                        # 提取模型名称
                        match = re.search(r'\[([^\]]+)\]', line)
                        if match:
                            free_models.append(match.group(1))
                if free_models:
                    free_models_hint = f"\n\n=== 免费模型列表（已从网页提取）===\n" + "\n".join([f"• {m}" for m in free_models]) + "\n=== 以上是免费模型 ==="
                    print(f"[DEBUG] 提取到免费模型: {free_models}")
            
            # 如果提取到了免费模型，直接告诉 AI 答案
            if free_models_hint:
                system_prompt = f"""你是一个智能助手。用户问的是免费模型，我已经从网页中提取出来了：
{free_models_hint}

请直接把上面的免费模型列表告诉用户，并简单介绍每个模型的用途。"""
            else:
                system_prompt = f"""你是一个智能助手。我已经抓取了用户发送的网页内容：

{web_content}

请根据上述内容回答用户的问题。直接给出答案，不要说"没有找到"或"建议访问网页"。"""
        elif web_search:
            system_prompt = "你是一个智能助手，可以联网搜索最新信息来回答用户问题。请根据搜索结果给出准确、有用的回答。"
        elif message.startswith("[转发的聊天记录]"):
            # 处理转发的聊天记录
            system_prompt = """你是用户的私人AI助手。用户转发了一段聊天记录给你。

请仔细阅读这段聊天记录，然后询问用户需要什么帮助：
- 总结这段对话的主要内容
- 分析对话中提到的关键信息
- 保存到知识库
- 回答关于这段对话的问题
- 继续聊这个话题

请先简要说明你看到了什么内容，然后询问用户需要你做什么。"""
        else:
            if should_search and knowledge_context:
                # 开启了知识库模式，且找到了内容
                system_prompt = f"""你是用户的私人AI助手。我从知识库中搜索到以下内容：

{knowledge_context}

请直接把找到的内容告诉用户。"""
            elif should_search and not knowledge_context:
                # 开启了知识库模式，但没有找到
                system_prompt = """你是用户的私人AI助手。当前开启了知识库检索模式，但没有找到相关记录。
请告诉用户"知识库中暂无此记录"，建议用户可以先保存相关内容，或者关闭知识库模式进行普通对话。"""
            else:
                # 普通聊天模式
                system_prompt = """你是用户的私人AI助手。你可以：
1. 回答问题、聊天
2. 帮用户保存信息到知识库（用户说"帮我保存：xxx"）
3. 分析用户上传的文件

如果用户想查找知识库内容，需要先点击"知识库"按钮开启检索模式。
请根据对话历史给出有帮助的回答。"""
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # 添加历史上下文
        for ctx in context_messages[-6:]:
            messages.append({"role": ctx["role"], "content": ctx["content"]})
        
        # 添加当前消息
        messages.append({"role": "user", "content": message})
        
        # 4. 调用AI（优先使用用户配置）
        if web_search:
            # 联网搜索
            if user_config.get('search_api_key'):
                search_client = self.get_client(
                    user_config.get('search_base_url', settings.QWEN_BASE_URL),
                    user_config.get('search_api_key')
                )
                search_model = user_config.get('search_model', settings.QWEN_CHAT_MODEL)
            else:
                search_client = self.qwen_client
                search_model = settings.QWEN_CHAT_MODEL
            
            response = await search_client.chat.completions.create(
                model=search_model,
                messages=messages,
                extra_body={"enable_search": True},
                temperature=0.7,
                max_tokens=2000
            )
        else:
            # 普通聊天
            if user_config.get('chat_api_key'):
                chat_client = self.get_client(
                    user_config.get('chat_base_url', settings.ZHIPU_BASE_URL),
                    user_config.get('chat_api_key')
                )
                chat_model = user_config.get('chat_model', settings.CHAT_MODEL)
            else:
                chat_client = self.client
                chat_model = settings.CHAT_MODEL
            
            response = await chat_client.chat.completions.create(
                model=chat_model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
        
        reply = response.choices[0].message.content
        
        # 解析token使用详情
        usage = response.usage
        tokens_used = usage.total_tokens if usage else 0
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0
        
        # 解析缓存命中（不同服务商格式不同）
        cached_tokens = 0
        if usage:
            # 通义千问格式
            if hasattr(usage, 'prompt_tokens_details') and usage.prompt_tokens_details:
                cached_tokens = getattr(usage.prompt_tokens_details, 'cached_tokens', 0) or 0
            # 智谱AI格式 - prompt_cache
            elif hasattr(usage, 'prompt_cache'):
                cached_tokens = getattr(usage, 'prompt_cache', 0) or 0
        
        # 确定使用的模型和服务商
        if web_search:
            used_model = search_model
            used_provider = 'qwen'
        else:
            used_model = chat_model
            used_provider = 'zhipu'
        
        # 计算成本（单位：万分之一元）
        cost = self.calculate_cost(used_provider, used_model, input_tokens, output_tokens, cached_tokens)
        
        # 5. 缓存到Redis
        await redis_client.add_chat_message(user_id, conversation_id, {
            "role": "user",
            "content": message
        })
        await redis_client.add_chat_message(user_id, conversation_id, {
            "role": "assistant",
            "content": reply
        })
        
        return {
            "reply": reply,
            "references": references,
            "tokens_used": tokens_used,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cached_tokens": cached_tokens,
            "model_name": used_model,
            "provider": used_provider,
            "cost": cost
        }
    
    async def summarize(self, content: str) -> dict:
        """AI总结内容"""
        response = await self.client.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个内容总结专家。请为以下内容生成一个简洁的标题（不超过20字）和摘要（不超过100字）。以JSON格式返回：{\"title\": \"标题\", \"summary\": \"摘要\"}"
                },
                {"role": "user", "content": content}
            ],
            temperature=0.3
        )
        
        import json
        try:
            result = json.loads(response.choices[0].message.content)
            return result
        except:
            return {"title": content[:20], "summary": content[:100]}
    
    async def generate_tags(self, content: str) -> List[str]:
        """AI生成标签"""
        response = await self.chat_client.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个内容分析专家。请为以下内容生成3-5个相关标签，以JSON数组格式返回，如：[\"标签1\", \"标签2\"]"
                },
                {"role": "user", "content": content}
            ],
            temperature=0.3
        )
        
        import json
        try:
            tags = json.loads(response.choices[0].message.content)
            return tags[:5]
        except:
            return []
    
    async def parse_file(self, file_url: str, prompt: str = "描述这个文件的内容") -> dict:
        """使用 Qwen-Doc-Turbo 解析文件（图片/PDF/Word/Excel）
        
        需要使用 DashScope 原生协议
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                    headers={
                        "Authorization": f"Bearer {settings.QWEN_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.QWEN_DOC_MODEL,
                        "input": {
                            "messages": [
                                {"role": "system", "content": "You are a helpful assistant."},
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt},
                                        {"type": "doc_url", "doc_url": [file_url]}
                                    ]
                                }
                            ]
                        }
                    }
                )
                
                result = response.json()
                
                if "output" in result and "choices" in result["output"]:
                    content = result["output"]["choices"][0]["message"]["content"]
                    usage = result.get("usage", {})
                    return {
                        "success": True,
                        "content": content,
                        "input_tokens": usage.get("input_tokens", 0),
                        "output_tokens": usage.get("output_tokens", 0),
                        "model": settings.QWEN_DOC_MODEL,
                        "provider": "qwen"
                    }
                else:
                    error_msg = result.get("message", "未知错误")
                    return {"success": False, "error": error_msg}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def parse_file_base64(self, file_data: bytes, file_type: str, prompt: str = "描述这个文件的内容") -> dict:
        """使用 base64 编码解析本地文件"""
        try:
            # 转换为 base64
            b64_data = base64.b64encode(file_data).decode('utf-8')
            
            # 根据文件类型构建 data URL
            mime_types = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'pdf': 'application/pdf',
                'doc': 'application/msword',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'xls': 'application/vnd.ms-excel',
                'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }
            
            mime_type = mime_types.get(file_type.lower(), 'application/octet-stream')
            data_url = f"data:{mime_type};base64,{b64_data}"
            
            # 对于图片，可以用 image_url 方式
            if file_type.lower() in ['jpg', 'jpeg', 'png', 'gif']:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {settings.QWEN_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "qwen-vl-plus",
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt},
                                        {"type": "image_url", "image_url": {"url": data_url}}
                                    ]
                                }
                            ]
                        }
                    )
                    
                    result = response.json()
                    if "choices" in result:
                        return {
                            "success": True,
                            "content": result["choices"][0]["message"]["content"],
                            "model": "qwen-vl-plus",
                            "provider": "qwen"
                        }
                    else:
                        return {"success": False, "error": result.get("error", {}).get("message", "未知错误")}
            else:
                # 非图片文件暂不支持 base64 方式，需要先上传
                return {"success": False, "error": "非图片文件请先上传到服务器获取URL"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def parse_document(self, file_data: bytes, filename: str, prompt: str = "请描述这个文件的内容") -> dict:
        """使用 qwen-doc-turbo 解析文档（支持 PDF/Word/Excel/PPT/图片）
        
        步骤：1. 通过 OpenAI 兼容接口上传文件获取 file_id  2. 调用 qwen-doc-turbo 解析
        """
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # 步骤1：通过 OpenAI 兼容接口上传文件
                upload_response = await client.post(
                    "https://dashscope.aliyuncs.com/compatible-mode/v1/files",
                    headers={
                        "Authorization": f"Bearer {settings.QWEN_API_KEY}"
                    },
                    files={
                        "file": (filename, file_data),
                    },
                    data={
                        "purpose": "file-extract"
                    }
                )
                
                upload_result = upload_response.json()
                
                # OpenAI 兼容接口返回格式：{"id": "file-xxx", "object": "file", ...}
                file_id = upload_result.get("id")
                if not file_id:
                    error_msg = upload_result.get("error", {}).get("message", "文件上传失败")
                    return {"success": False, "error": error_msg}
                
                # 步骤2：等待文件解析完成后调用 qwen-doc-turbo (OpenAI 兼容接口)
                import asyncio
                max_retries = 5
                
                for retry in range(max_retries):
                    response = await client.post(
                        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {settings.QWEN_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "qwen-doc-turbo",
                            "messages": [
                                {"role": "system", "content": "You are a helpful assistant."},
                                {"role": "system", "content": f"fileid://{file_id}"},
                                {"role": "user", "content": prompt}
                            ]
                        }
                    )
                    
                    result = response.json()
                    
                    # 检查是否文件还在解析中
                    error_msg = result.get("error", {}).get("message", "")
                    if "File parsing in progress" in error_msg:
                        await asyncio.sleep(2)
                        continue
                    
                    if "choices" in result:
                        usage = result.get("usage", {})
                        return {
                            "success": True,
                            "content": result["choices"][0]["message"]["content"],
                            "model": "qwen-doc-turbo",
                            "provider": "qwen",
                            "input_tokens": usage.get("prompt_tokens", 0),
                            "output_tokens": usage.get("completion_tokens", 0)
                        }
                    else:
                        return {"success": False, "error": error_msg or "文档解析失败"}
                
                return {"success": False, "error": "文件解析超时，请稍后重试"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def parse_image(self, image_data_url: str, prompt: str = "请描述这张图片的内容") -> dict:
        """使用智谱 GLM 视觉模型解析图片（GLM-4V-Flash / GLM-4.1V-Thinking-Flash 轮换）"""
        try:
            # 获取下一个视觉模型
            vision_model = self.get_next_vision_model()
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{settings.ZHIPU_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.ZHIPU_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": vision_model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "image_url", "image_url": {"url": image_data_url}},
                                    {"type": "text", "text": prompt}
                                ]
                            }
                        ],
                        "max_tokens": 2000
                    }
                )
                
                result = response.json()
                print(f"[DEBUG] 图片解析API响应 model={vision_model}: {result}")
                
                if "choices" in result:
                    usage = result.get("usage", {})
                    return {
                        "success": True,
                        "content": result["choices"][0]["message"]["content"],
                        "model": vision_model,
                        "provider": "zhipu",
                        "input_tokens": usage.get("prompt_tokens", 0),
                        "output_tokens": usage.get("completion_tokens", 0)
                    }
                else:
                    error_msg = result.get("error", {}).get("message", "图片解析失败")
                    print(f"[ERROR] 图片解析失败: {result}")
                    return {"success": False, "error": f"图片解析失败: {error_msg}"}
                    
        except Exception as e:
            print(f"[ERROR] 图片解析异常: {e}")
            return {"success": False, "error": str(e)}
    
    async def parse_image_with_model(self, image_data_url: str, prompt: str, model: str = None) -> dict:
        """使用指定的视觉模型解析图片"""
        try:
            vision_model = model or self.get_next_vision_model()
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{settings.ZHIPU_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.ZHIPU_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": vision_model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "image_url", "image_url": {"url": image_data_url}},
                                    {"type": "text", "text": prompt}
                                ]
                            }
                        ],
                        "max_tokens": 2000
                    }
                )
                
                result = response.json()
                
                if "choices" in result:
                    usage = result.get("usage", {})
                    return {
                        "success": True,
                        "content": result["choices"][0]["message"]["content"],
                        "model": vision_model,
                        "provider": "zhipu",
                        "input_tokens": usage.get("prompt_tokens", 0),
                        "output_tokens": usage.get("completion_tokens", 0)
                    }
                else:
                    error_msg = result.get("error", {}).get("message", "图片解析失败")
                    return {"success": False, "error": error_msg}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}


ai_service = AIService()
