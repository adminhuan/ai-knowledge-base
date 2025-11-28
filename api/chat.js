/**
 * 聊天相关 API
 */
import { get, post, del } from './request'

// 获取会话列表
export const getConversations = () => get('/api/chat/conversations')

// 创建会话
export const createConversation = (data) => post('/api/chat/conversations', data)

// 删除会话
export const deleteConversation = (id) => del(`/api/chat/conversations/${id}`)

// 获取会话消息
export const getMessages = (conversationId, params = {}) => get(`/api/chat/conversations/${conversationId}/messages`, params)

// 发送消息（AI对话）- 增加超时时间，因为可能需要抓取网页
import request from './request'
export const sendChatMessage = (data) => request({ 
    url: '/api/chat', 
    method: 'POST', 
    data, 
    timeout: 60000  // 60秒超时
})

// 删除单条消息
export const deleteMessage = (messageId) => del(`/api/chat/messages/${messageId}`)

// 更新消息的文件URL（上传云端后调用）
export const updateMessageFile = (messageId, fileUrl, fileType = 'image') => 
    request({ url: `/api/chat/messages/${messageId}/file`, method: 'PUT', data: { fileUrl, fileType } })

// 保存消息到知识库
export const saveToKnowledge = (data) => post('/api/knowledge/from-chat', data)
