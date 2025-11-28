-- ============================================
-- 知识库数据库设计 (PostgreSQL + pgvector)
-- ============================================

-- 启用 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- 用户表
-- ============================================
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(64),
    avatar VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(100),
    status SMALLINT DEFAULT 1,  -- 1:正常 0:禁用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_phone ON users(phone);

-- ============================================
-- 会话表
-- ============================================
CREATE TABLE conversations (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    title VARCHAR(255) DEFAULT '新对话',
    last_message TEXT,
    message_count INT DEFAULT 0,
    status SMALLINT DEFAULT 1,  -- 1:正常 0:已删除
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_user ON conversations(user_id, status);
CREATE INDEX idx_conversations_updated ON conversations(updated_at DESC);

-- ============================================
-- 消息表
-- ============================================
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL REFERENCES conversations(id),
    user_id BIGINT NOT NULL REFERENCES users(id),
    role VARCHAR(20) NOT NULL,  -- user/assistant/system
    content TEXT NOT NULL,
    tokens_used INT DEFAULT 0,
    metadata JSONB,  -- 扩展字段：引用的知识ID、AI模型信息等
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_created ON messages(created_at);

-- ============================================
-- 知识库表 (核心表，带向量)
-- ============================================
CREATE TABLE knowledge (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,  -- AI生成的摘要
    source VARCHAR(50) DEFAULT 'manual',  -- chat:聊天提取 manual:手动添加 import:导入
    source_id VARCHAR(100),  -- 来源ID（如消息ID）
    tags JSONB DEFAULT '[]',  -- 标签数组
    embedding vector(1536),  -- OpenAI embedding 维度，其他模型可能不同
    token_count INT DEFAULT 0,
    view_count INT DEFAULT 0,
    status SMALLINT DEFAULT 1,  -- 1:正常 0:已删除
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 向量索引（用于相似度搜索）
CREATE INDEX idx_knowledge_embedding ON knowledge 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX idx_knowledge_user ON knowledge(user_id, status);
CREATE INDEX idx_knowledge_source ON knowledge(source);
CREATE INDEX idx_knowledge_created ON knowledge(created_at DESC);

-- 全文搜索索引（用于关键词搜索）
CREATE INDEX idx_knowledge_content_fts ON knowledge 
USING gin(to_tsvector('simple', title || ' ' || content));

-- ============================================
-- 知识标签表（可选，用于标签管理）
-- ============================================
CREATE TABLE tags (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    name VARCHAR(50) NOT NULL,
    color VARCHAR(20),
    count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, name)
);

-- ============================================
-- 聊天监控配置表
-- ============================================
CREATE TABLE monitor_config (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    enabled BOOLEAN DEFAULT true,
    keywords JSONB DEFAULT '[]',  -- 监控关键词
    auto_save BOOLEAN DEFAULT false,  -- 自动保存到知识库
    min_length INT DEFAULT 50,  -- 最小内容长度才触发
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- AI 调用记录表（可选，用于统计和计费）
-- ============================================
CREATE TABLE ai_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    action VARCHAR(50) NOT NULL,  -- chat/summarize/search/generate_tags
    model VARCHAR(50),
    prompt_tokens INT DEFAULT 0,
    completion_tokens INT DEFAULT 0,
    total_tokens INT DEFAULT 0,
    cost DECIMAL(10, 6) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_logs_user ON ai_logs(user_id);
CREATE INDEX idx_ai_logs_created ON ai_logs(created_at);

-- ============================================
-- 常用查询示例
-- ============================================

-- 1. 语义搜索（向量相似度）
-- SELECT id, title, content, 
--        1 - (embedding <=> '[0.1, 0.2, ...]'::vector) as similarity
-- FROM knowledge
-- WHERE user_id = ? AND status = 1
-- ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
-- LIMIT 5;

-- 2. 关键词搜索（全文搜索）
-- SELECT id, title, content
-- FROM knowledge
-- WHERE user_id = ? AND status = 1
--   AND to_tsvector('simple', title || ' ' || content) @@ to_tsquery('simple', '关键词')
-- ORDER BY created_at DESC
-- LIMIT 20;

-- 3. 混合搜索（结合向量和关键词）
-- SELECT id, title, content,
--        (0.7 * (1 - (embedding <=> ?::vector)) + 
--         0.3 * ts_rank(to_tsvector('simple', title || ' ' || content), to_tsquery('simple', ?))) as score
-- FROM knowledge
-- WHERE user_id = ? AND status = 1
-- ORDER BY score DESC
-- LIMIT 10;

-- ============================================
-- Redis 缓存设计（伪代码说明）
-- ============================================
-- 
-- 1. 会话上下文缓存
-- Key: chat:context:{user_id}:{conversation_id}
-- Value: 最近 N 条消息的 JSON 数组
-- TTL: 1 小时
--
-- 2. 用户信息缓存
-- Key: user:info:{user_id}
-- Value: 用户信息 JSON
-- TTL: 10 分钟
--
-- 3. 热点知识缓存
-- Key: knowledge:hot:{user_id}
-- Value: 最常访问的知识 ID 列表
-- TTL: 30 分钟
