/**
 * 分类相关 API
 */
import { get, post, put, del } from './request'

// 获取分类列表
export const getCategories = () => get('/api/categories')

// 创建分类
export const createCategory = (data) => post('/api/categories', data)

// 更新分类
export const updateCategory = (id, data) => put(`/api/categories/${id}`, data)

// 删除分类
export const deleteCategory = (id) => del(`/api/categories/${id}`)

export default {
	getCategories,
	createCategory,
	updateCategory,
	deleteCategory
}
