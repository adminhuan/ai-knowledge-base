/**
 * 监控相关 API
 */
import { get, post, put } from './request'

export const getMonitorMessages = () => get('/api/monitor/messages')
export const addMonitorMessage = (data) => post('/api/monitor/messages', data)
export const updateMonitorMessage = (id, data) => put(`/api/monitor/messages/${id}`, data)
export const clearMonitorMessages = () => post('/api/monitor/messages/clear')

export default {
  getMonitorMessages,
  addMonitorMessage,
  updateMonitorMessage,
  clearMonitorMessages
}
