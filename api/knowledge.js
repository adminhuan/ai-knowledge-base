/**
 * 知识库相关 API
 */
import { get, post, put, del } from './request'

// 获取知识列表
export const getKnowledgeList = (params) => get('/api/knowledge', params)

// 获取知识详情
export const getKnowledgeDetail = (id) => get(`/api/knowledge/${id}`)

// 创建知识
export const saveKnowledge = (data) => post('/api/knowledge', data)

// 更新知识
export const updateKnowledge = (id, data) => put(`/api/knowledge/${id}`, data)

// 删除知识
export const deleteKnowledge = (id) => del(`/api/knowledge/${id}`)

// 搜索知识（支持语义搜索和关键词搜索）
export const searchKnowledge = (params) => post('/api/knowledge/search', params)
