<template>
	<view class="category">
		<!-- 顶部操作栏 -->
		<view class="header">
			<text class="title">知识分类</text>
			<view class="add-btn" @click="showAddModal">
				<Icon name="plus" size="18" class="add-icon" />
				<text class="add-text">新建</text>
			</view>
		</view>
		
		<!-- 分类列表 -->
		<view class="category-list">
			<view 
				class="category-item" 
				v-for="item in categories" 
				:key="item.id"
				@click="goCategory(item)"
				@longpress="showActions(item)"
			>
				<view class="item-icon" :style="{ backgroundColor: item.color }">
					<Icon :name="item.icon" size="22" class="icon-text" />
				</view>
				<view class="item-info">
					<text class="item-name">{{ item.name }}</text>
					<text class="item-count">{{ item.count }} 条知识</text>
				</view>
				<text class="item-arrow">›</text>
			</view>
		</view>
		
		<!-- 默认分类 -->
		<view class="default-section">
			<text class="section-title">系统分类</text>
			<view class="category-list">
				<view class="category-item" @click="goCategory({ id: 'all', name: '全部' })">
					<view class="item-icon" style="background-color: #07C160">
						<Icon name="book" size="22" class="icon-text" />
					</view>
					<view class="item-info">
						<text class="item-name">全部知识</text>
						<text class="item-count">{{ totalCount }} 条</text>
					</view>
					<text class="item-arrow">›</text>
				</view>
				<view class="category-item" @click="goCategory({ id: 'uncategorized', name: '未分类' })">
					<view class="item-icon" style="background-color: #999">
						<Icon name="folder" size="22" class="icon-text" />
					</view>
					<view class="item-info">
						<text class="item-name">未分类</text>
						<text class="item-count">{{ uncategorizedCount }} 条</text>
					</view>
					<text class="item-arrow">›</text>
				</view>
				<view class="category-item" @click="goCategory({ id: 'favorites', name: '收藏' })">
					<view class="item-icon" style="background-color: #faad14">
						<Icon name="sparkle" size="22" class="icon-text" />
					</view>
					<view class="item-info">
						<text class="item-name">我的收藏</text>
						<text class="item-count">{{ favoritesCount }} 条</text>
					</view>
					<text class="item-arrow">›</text>
				</view>
			</view>
		</view>
		
		<!-- 新建/编辑弹窗 -->
		<view class="modal" v-if="showModal" @click="closeModal">
			<view class="modal-content" @click.stop>
				<view class="modal-header">
					<text class="modal-title">{{ editingCategory ? '编辑分类' : '新建分类' }}</text>
					<view class="modal-close" @click="closeModal">
						<Icon name="close" size="18" />
					</view>
				</view>
				
				<view class="form-item">
					<text class="form-label">分类名称</text>
					<input 
						class="form-input" 
						v-model="formData.name" 
						placeholder="输入分类名称"
					/>
				</view>
				
				<view class="form-item">
					<text class="form-label">选择图标</text>
					<view class="icon-picker">
						<view 
							class="icon-option" 
							:class="{ 'selected': formData.icon === icon }"
							v-for="icon in iconOptions" 
							:key="icon"
							@click="formData.icon = icon"
						>
							<Icon :name="icon" size="22" />
						</view>
					</view>
				</view>
				
				<view class="form-item">
					<text class="form-label">选择颜色</text>
					<view class="color-picker">
						<view 
							class="color-option" 
							:class="{ 'selected': formData.color === color }"
							:style="{ backgroundColor: color }"
							v-for="color in colorOptions" 
							:key="color"
							@click="formData.color = color"
						>
						</view>
					</view>
				</view>
				
				<view class="modal-footer">
					<view class="cancel-btn" @click="closeModal">取消</view>
					<view class="confirm-btn" @click="saveCategory">保存</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import Icon from '@/components/Icon.vue'
import { getCategories, createCategory, updateCategory, deleteCategory } from '@/api/category'

const showModal = ref(false)
const editingCategory = ref(null)
const formData = ref({
	name: '',
	icon: 'folder',
	color: '#07C160'
})

const categories = ref([])
const totalCount = ref(0)
const uncategorizedCount = ref(0)
const favoritesCount = ref(0)

const iconOptions = ['folder', 'note', 'lightning', 'wrench', 'chart', 'target', 'laptop', 'globe', 'phone', 'lock', 'doc', 'palette']
const colorOptions = ['#07C160', '#1890ff', '#06AD56', '#10b981', '#fa8c16', '#52c41a', '#13c2c2', '#07C160']

onMounted(() => {
	loadCategories()
})

const loadCategories = () => {
	getCategories().then(res => {
		categories.value = res.data || []
		// 计数信息可用后端的 count 字段，缺失则用 0
		totalCount.value = categories.value.reduce((s, c) => s + (c.count || 0), 0)
		uncategorizedCount.value = 0
		favoritesCount.value = 0
	}).catch(() => {
		categories.value = []
		uni.showToast({ title: '加载分类失败', icon: 'none' })
	})
}

const showAddModal = () => {
	editingCategory.value = null
	formData.value = {
		name: '',
		icon: 'folder',
		color: '#07C160'
	}
	showModal.value = true
}

const closeModal = () => {
	showModal.value = false
	editingCategory.value = null
}

const saveCategory = () => {
	if (!formData.value.name.trim()) {
		uni.showToast({ title: '请输入分类名称', icon: 'none' })
		return
	}
	
	const payload = {
		name: formData.value.name,
		icon: formData.value.icon,
		color: formData.value.color
	}

	const request = editingCategory.value
		? updateCategory(editingCategory.value.id, payload)
		: createCategory(payload)

	request.then(() => {
		uni.showToast({ title: '保存成功' })
		loadCategories()
	}).catch(() => {
		uni.showToast({ title: '保存失败', icon: 'none' })
	})
	
	closeModal()
}

const goCategory = (item) => {
	uni.navigateTo({
		url: `/pages/knowledge/index?categoryId=${item.id}&categoryName=${encodeURIComponent(item.name)}`
	})
}

const showActions = (item) => {
	uni.showActionSheet({
		itemList: ['编辑', '删除'],
		success: (res) => {
			if (res.tapIndex === 0) {
				editingCategory.value = item
				formData.value = {
					name: item.name,
					icon: item.icon,
					color: item.color
				}
				showModal.value = true
			} else if (res.tapIndex === 1) {
				uni.showModal({
					title: '确认删除',
					content: `删除分类"${item.name}"后，该分类下的知识将变为未分类`,
					success: (modalRes) => {
						if (modalRes.confirm) {
							deleteCategory(item.id).then(() => {
								uni.showToast({ title: '已删除' })
								loadCategories()
							}).catch(() => {
								uni.showToast({ title: '删除失败', icon: 'none' })
							})
						}
					}
				})
			}
		}
	})
}
</script>

<style scoped>
.category {
	min-height: 100vh;
	background-color: #f5f5f5;
}

.header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 32rpx;
	background-color: #fff;
}

.title {
	font-size: 36rpx;
	color: #333;
	font-weight: 600;
}

.add-btn {
	display: flex;
	align-items: center;
	padding: 12rpx 24rpx;
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	border-radius: 32rpx;
}

.add-icon {
	font-size: 28rpx;
	color: #fff;
	margin-right: 8rpx;
}

.add-text {
	font-size: 26rpx;
	color: #fff;
}

.category-list {
	background-color: #fff;
	margin-top: 24rpx;
}

.category-item {
	display: flex;
	align-items: center;
	padding: 28rpx 32rpx;
	border-bottom: 1rpx solid #f5f5f5;
}

.category-item:last-child {
	border-bottom: none;
}

.item-icon {
	width: 80rpx;
	height: 80rpx;
	border-radius: 16rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 24rpx;
}

.icon-text {
	color: #fff;
}

.item-info {
	flex: 1;
}

.item-name {
	font-size: 32rpx;
	color: #333;
	display: block;
	margin-bottom: 4rpx;
}

.item-count {
	font-size: 26rpx;
	color: #999;
}

.item-arrow {
	font-size: 32rpx;
	color: #ccc;
}

.default-section {
	margin-top: 48rpx;
}

.section-title {
	font-size: 28rpx;
	color: #999;
	padding: 0 32rpx 16rpx;
}

/* 弹窗 */
.modal {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background-color: rgba(0,0,0,0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 999;
}

.modal-content {
	width: 600rpx;
	background-color: #fff;
	border-radius: 16rpx;
	padding: 32rpx;
}

.modal-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 32rpx;
}

.modal-title {
	font-size: 34rpx;
	color: #333;
	font-weight: 500;
}

.modal-close {
	font-size: 36rpx;
	color: #999;
}

.form-item {
	margin-bottom: 32rpx;
}

.form-label {
	font-size: 28rpx;
	color: #666;
	margin-bottom: 16rpx;
	display: block;
}

.form-input {
	width: 100%;
	padding: 20rpx;
	background-color: #f5f5f5;
	border-radius: 8rpx;
	font-size: 30rpx;
}

.icon-picker, .color-picker {
	display: flex;
	flex-wrap: wrap;
	gap: 16rpx;
}

.icon-option {
	width: 72rpx;
	height: 72rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	background-color: #f5f5f5;
	border-radius: 12rpx;
	border: 2rpx solid transparent;
}

.icon-option.selected {
	border-color: #07C160;
	background-color: #e8f5e9;
}

.icon-emoji {
	font-size: 36rpx;
}

.color-option {
	width: 56rpx;
	height: 56rpx;
	border-radius: 50%;
	border: 3rpx solid transparent;
}

.color-option.selected {
	border-color: #333;
	transform: scale(1.1);
}

.modal-footer {
	display: flex;
	gap: 24rpx;
	margin-top: 32rpx;
}

.cancel-btn, .confirm-btn {
	flex: 1;
	text-align: center;
	padding: 24rpx;
	border-radius: 12rpx;
	font-size: 30rpx;
}

.cancel-btn {
	background-color: #f5f5f5;
	color: #666;
}

.confirm-btn {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	color: #fff;
}
</style>
