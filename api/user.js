/**
 * 用户相关 API
 */
import { get, post, put } from './request'
import { API_BASE_URL } from '@/config'

// 获取用户信息
export const getUserInfo = () => get('/api/user/info')

// 登录 (OAuth2 需要 form-urlencoded 格式)
export const login = (data) => {
	return new Promise((resolve, reject) => {
		uni.request({
			url: API_BASE_URL + '/api/user/login',
			method: 'POST',
			header: {
				'Content-Type': 'application/x-www-form-urlencoded'
			},
			data: `username=${encodeURIComponent(data.username)}&password=${encodeURIComponent(data.password)}`,
			success: (res) => {
				if (res.statusCode === 200 && res.data.code === 0) {
					resolve(res.data)
				} else {
					reject(res.data)
				}
			},
			fail: reject
		})
	})
}

// 注册
export const register = (data) => post('/api/user/register', data)

// 获取统计数据
export const getStats = () => get('/api/user/stats')

// 更新用户设置
export const updateSettings = (data) => post('/api/user/settings', data)

// 保存/获取 AI 配置
export const saveAIConfig = (data) => post('/api/user/ai-config', data)
export const getAIConfig = () => get('/api/user/ai-config')

// AI 使用监控
export const getAIUsage = (days = 1) => get(`/api/user/ai-usage?days=${days}`)

// 更新用户资料（昵称、头像）
export const updateProfile = (data) => post('/api/user/profile', data)

// 修改密码
export const changePassword = (data) => post('/api/user/password', data)
