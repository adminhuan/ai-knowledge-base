/**
 * 请求封装
 */
import { API_BASE_URL } from '@/config'

const request = (options) => {
	return new Promise((resolve, reject) => {
		const token = uni.getStorageSync('token')
		
		uni.request({
			url: API_BASE_URL + options.url,
			method: options.method || 'GET',
			data: options.data,
			header: {
				'Content-Type': 'application/json',
				'Authorization': token ? `Bearer ${token}` : '',
				...options.header
			},
			timeout: options.timeout || 30000,
			success: (res) => {
				if (res.statusCode === 200) {
					if (res.data.code === 0 || res.data.code === 200) {
						resolve(res.data)
					} else {
						uni.showToast({
							title: res.data.message || '请求失败',
							icon: 'none'
						})
						reject(res.data)
					}
				} else if (res.statusCode === 401) {
					uni.removeStorageSync('token')
					uni.removeStorageSync('userInfo')
					uni.showToast({
						title: '登录已过期',
						icon: 'none'
					})
					setTimeout(() => {
						uni.reLaunch({ url: '/pages/login/index' })
					}, 1500)
					reject(res)
				} else {
					reject(res)
				}
			},
			fail: (err) => {
				console.error('请求失败:', err)
				reject(err)
			}
		})
	})
}

export const get = (url, data) => request({ url, method: 'GET', data })
export const post = (url, data) => request({ url, method: 'POST', data })
export const put = (url, data) => request({ url, method: 'PUT', data })
export const del = (url, data) => request({ url, method: 'DELETE', data })

export default request
