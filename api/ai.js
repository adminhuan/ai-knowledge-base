/**
 * AI 相关 API
 */
import { post } from './request'

// AI对话（带知识库RAG检索）
export const aiChat = (data) => post('/api/ai/chat', data)

// AI总结内容
export const aiSummarize = (content) => post('/api/ai/summarize', { content })

// AI生成标签
export const aiGenerateTags = (content) => post('/api/ai/generate-tags', { content })

// AI检索知识库
export const aiSearch = (query) => post('/api/ai/search', { query })

// AI整理内容
export const aiOrganize = (content) => post('/api/ai/organize', { content })
