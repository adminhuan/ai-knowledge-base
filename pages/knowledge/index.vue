<template>
	<view class="knowledge-page">
		<!-- 顶部 -->
		<view class="page-header">
			<view class="header-top">
				<text class="page-title">知识库</text>
				<view class="header-actions">
					<view class="search-btn" @click="goSearch">
						<Icon name="search" size="20" />
					</view>
					<view class="add-btn" @click="addKnowledge">
						<Icon name="plus" size="20" />
					</view>
				</view>
			</view>
			<text class="page-subtitle">共 {{ knowledgeList.length }} 条知识</text>
		</view>

		<!-- 分类标签 -->
		<scroll-view class="category-bar" scroll-x :show-scrollbar="false">
			<view class="category-list">
				<view 
					class="category-item" 
					:class="{ active: currentCategory === item.id }"
					v-for="item in categories" 
					:key="item.id"
					@click="switchCategory(item.id)"
				>
					<text>{{ item.name }}</text>
				</view>
			</view>
		</scroll-view>

		<!-- 知识列表 -->
		<scroll-view class="knowledge-list" scroll-y @scrolltolower="loadMore">
			<view 
				class="knowledge-card" 
				v-for="item in knowledgeList" 
				:key="item.id"
				@click="goDetail(item)"
			>
				<view class="card-header">
					<view class="card-icon" :class="item.source || 'manual'">
						<text>{{ getSourceIcon(item.source) }}</text>
					</view>
					<view class="card-info">
						<text class="card-title">{{ item.title }}</text>
						<text class="card-time">{{ formatTime(item.createdAt) }}</text>
					</view>
					<view class="card-actions">
						<view class="card-favorite" v-if="item.isFavorite">
							<text>♥</text>
						</view>
						<view class="delete-btn" @click.stop="confirmDelete(item)">
							<text>×</text>
						</view>
					</view>
				</view>
				<view class="card-content" v-if="item.content">
					<text>{{ item.content.substring(0, 80) }}{{ item.content.length > 80 ? '...' : '' }}</text>
				</view>
				<view class="card-tags" v-if="item.tags && item.tags.length">
					<text class="tag" v-for="(tag, i) in item.tags.slice(0, 3)" :key="i">#{{ tag }}</text>
				</view>
			</view>

			<!-- 空状态 -->
			<view class="empty-state" v-if="knowledgeList.length === 0 && !loading">
				<text class="empty-icon">📚</text>
				<text class="empty-title">暂无知识</text>
				<text class="empty-tip">点击右上角 + 添加新知识</text>
			</view>

			<!-- 加载中 -->
			<view class="loading" v-if="loading">
				<text>加载中...</text>
			</view>

			<view class="bottom-space"></view>
		</scroll-view>

		<CustomTabBar :currentTab="1" />
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { onShow, onPullDownRefresh } from '@dcloudio/uni-app'
import { getKnowledgeList, deleteKnowledge } from '@/api/knowledge'
import { getCategories } from '@/api/category'
import Icon from '@/components/Icon.vue'
import CustomTabBar from '@/components/CustomTabBar.vue'

const categories = ref([
	{ id: 'all', name: '全部' },
	{ id: 'favorites', name: '收藏' },
	{ id: 'chat', name: 'AI对话' },
	{ id: 'manual', name: '手动' },
	{ id: 'import', name: '导入' }
])
const currentCategory = ref('all')
const knowledgeList = ref([])
const loading = ref(false)

onMounted(() => {
	loadCategories()
	loadKnowledge()
})

onShow(() => {
	loadKnowledge()
})

onPullDownRefresh(async () => {
	await loadKnowledge()
	uni.stopPullDownRefresh()
})

const loadCategories = async () => {
	try {
		const res = await getCategories()
		const apiList = (res.data || []).map(item => ({
			id: String(item.id),
			name: item.name
		}))
		if (apiList.length) {
			categories.value = [...categories.value, ...apiList]
		}
	} catch (e) {}
}

const loadKnowledge = async () => {
	loading.value = true
	try {
		const res = await getKnowledgeList({
			category: currentCategory.value === 'all' ? '' : currentCategory.value
		})
		knowledgeList.value = res.data || []
	} catch (e) {
		knowledgeList.value = []
	} finally {
		loading.value = false
	}
}

const loadMore = () => {
	// 可扩展分页加载
}

const switchCategory = (id) => {
	currentCategory.value = id
	loadKnowledge()
}

const goSearch = () => {
	uni.navigateTo({ url: '/pages/knowledge/search' })
}

const goDetail = (item) => {
	uni.navigateTo({ url: `/pages/knowledge/detail?id=${item.id}` })
}

const addKnowledge = () => {
	uni.showActionSheet({
		itemList: ['新建知识', '从文件导入'],
		success: (res) => {
			if (res.tapIndex === 0) {
				uni.navigateTo({ url: '/pages/knowledge/detail?mode=create' })
			}
		}
	})
}

const getSourceIcon = (source) => {
	const icons = { chat: '💬', manual: '✏️', import: '📄' }
	return icons[source] || '📝'
}

const formatTime = (time) => {
	if (!time) return ''
	const date = new Date(time)
	const now = new Date()
	const diff = now - date
	
	if (diff < 60000) return '刚刚'
	if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
	if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
	if (diff < 604800000) return Math.floor(diff / 86400000) + '天前'
	
	return `${date.getMonth() + 1}/${date.getDate()}`
}

const confirmDelete = (item) => {
	uni.showModal({
		title: '删除确认',
		content: `确定删除「${item.title}」吗？`,
		confirmColor: '#ff4d4f',
		success: async (res) => {
			if (res.confirm) {
				try {
					await deleteKnowledge(item.id)
					knowledgeList.value = knowledgeList.value.filter(k => k.id !== item.id)
					uni.showToast({ title: '已删除', icon: 'success' })
				} catch (e) {
					uni.showToast({ title: '删除失败', icon: 'none' })
				}
			}
		}
	})
}
</script>

<style scoped>
.knowledge-page {
	min-height: 100vh;
	background: #f5f5f5;
	padding-bottom: 120rpx;
}

/* 顶部 */
.page-header {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	padding: 48rpx 32rpx 32rpx;
}

.header-top {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.page-title {
	font-size: 44rpx;
	font-weight: 700;
	color: #fff;
}

.header-actions {
	display: flex;
	gap: 20rpx;
}

.search-btn, .add-btn {
	width: 72rpx;
	height: 72rpx;
	background: rgba(255,255,255,0.2);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	color: #fff;
}

.page-subtitle {
	font-size: 26rpx;
	color: rgba(255,255,255,0.8);
	margin-top: 8rpx;
	display: block;
}

/* 分类标签 */
.category-bar {
	background: #fff;
	border-bottom: 1rpx solid #eee;
}

.category-list {
	display: flex;
	padding: 20rpx 24rpx;
	gap: 16rpx;
}

.category-item {
	padding: 14rpx 28rpx;
	background: #f5f5f5;
	border-radius: 32rpx;
	font-size: 26rpx;
	color: #666;
	flex-shrink: 0;
}

.category-item.active {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	color: #fff;
	font-weight: 500;
}

/* 知识列表 */
.knowledge-list {
	height: calc(100vh - 380rpx);
	padding: 24rpx;
}

.knowledge-card {
	background: #fff;
	border-radius: 20rpx;
	padding: 28rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.05);
}

.card-header {
	display: flex;
	align-items: center;
}

.card-icon {
	width: 72rpx;
	height: 72rpx;
	border-radius: 16rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 32rpx;
	margin-right: 20rpx;
	flex-shrink: 0;
}

.card-icon.chat { background: #e8f5e9; }
.card-icon.manual { background: #e3f2fd; }
.card-icon.import { background: #fff3e0; }

.card-info {
	flex: 1;
	min-width: 0;
}

.card-title {
	font-size: 30rpx;
	font-weight: 600;
	color: #333;
	display: block;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.card-time {
	font-size: 24rpx;
	color: #999;
	margin-top: 6rpx;
	display: block;
}

.card-actions {
	display: flex;
	align-items: center;
	gap: 16rpx;
}

.card-favorite {
	color: #ff6b6b;
	font-size: 32rpx;
}

.delete-btn {
	width: 48rpx;
	height: 48rpx;
	border-radius: 50%;
	background: #f5f5f5;
	display: flex;
	align-items: center;
	justify-content: center;
}

.delete-btn text {
	font-size: 36rpx;
	color: #999;
	line-height: 1;
}

.delete-btn:active {
	background: #ffebee;
}

.delete-btn:active text {
	color: #ff4d4f;
}

.card-content {
	margin-top: 20rpx;
	padding-top: 20rpx;
	border-top: 1rpx solid #f0f0f0;
}

.card-content text {
	font-size: 26rpx;
	color: #666;
	line-height: 1.6;
}

.card-tags {
	display: flex;
	flex-wrap: wrap;
	gap: 12rpx;
	margin-top: 16rpx;
}

.tag {
	font-size: 22rpx;
	color: #07C160;
	background: rgba(7, 193, 96, 0.1);
	padding: 6rpx 14rpx;
	border-radius: 8rpx;
}

/* 空状态 */
.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 120rpx 40rpx;
}

.empty-icon {
	font-size: 80rpx;
	margin-bottom: 24rpx;
}

.empty-title {
	font-size: 32rpx;
	color: #333;
	margin-bottom: 12rpx;
}

.empty-tip {
	font-size: 26rpx;
	color: #999;
}

.loading {
	text-align: center;
	padding: 32rpx;
	color: #999;
	font-size: 26rpx;
}

.bottom-space {
	height: 40rpx;
}
</style>
