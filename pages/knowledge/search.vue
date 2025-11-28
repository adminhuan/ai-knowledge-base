<template>
	<view class="search-page" :style="pageStyle">
		<view class="page-hero">
			<view class="hero-texts">
				<text class="hero-title">搜索知识库</text>
				<text class="hero-desc">支持语义与关键词双模式，快速找到需要的资料。</text>
			</view>
			<view class="hero-pill">
				<text class="pill-dot"></text>
				<text class="pill-text">{{ results.length ? '找到 ' + results.length + ' 条' : '等待搜索' }}</text>
			</view>
		</view>

		<!-- 搜索栏 -->
		<view class="search-bar">
			<view class="search-input-wrapper">
				<Icon name="search" size="20" class="search-icon" />
				<input 
					class="search-input"
					v-model="keyword"
					placeholder="搜索知识库内容"
					focus
					@confirm="search"
					@input="onInput"
				/>
				<view class="clear-btn" v-if="keyword" @click="clearKeyword">
					<Icon name="close" size="16" />
				</view>
			</view>
			<text class="cancel-btn" @click="goBack">取消</text>
		</view>
		
		<!-- 搜索类型切换 -->
		<view class="search-type">
			<view 
				class="type-item" 
				:class="{ 'active': searchType === 'semantic' }"
				@click="searchType = 'semantic'"
			>
				<Icon name="brain" size="18" class="type-icon" />
				<text class="type-text">语义搜索</text>
			</view>
			<view 
				class="type-item" 
				:class="{ 'active': searchType === 'keyword' }"
				@click="searchType = 'keyword'"
			>
				<Icon name="note" size="18" class="type-icon" />
				<text class="type-text">关键词搜索</text>
			</view>
		</view>
		
		<!-- 热门搜索 -->
		<view class="hot-search" v-if="!keyword && !results.length">
			<text class="section-title">热门搜索</text>
			<view class="hot-tags">
				<text 
					class="hot-tag" 
					v-for="item in hotKeywords" 
					:key="item"
					@click="quickSearch(item)"
				>{{ item }}</text>
			</view>
		</view>
		
		<!-- 搜索历史 -->
		<view class="history" v-if="!keyword && !results.length && history.length">
			<view class="history-header">
				<text class="section-title">搜索历史</text>
				<text class="clear-history" @click="clearHistory">清空</text>
			</view>
			<view class="history-list">
				<text 
					class="history-item" 
					v-for="item in history" 
					:key="item"
					@click="quickSearch(item)"
				>{{ item }}</text>
			</view>
		</view>
		
		<!-- 搜索结果 -->
		<view class="results" v-if="results.length">
			<view class="result-header">
				<text class="result-count">找到 {{ results.length }} 条相关知识</text>
			</view>
			<view 
				class="result-item" 
				v-for="item in results" 
				:key="item.id"
				@click="goDetail(item)"
			>
				<text class="result-title">{{ item.title }}</text>
				<text class="result-content">{{ item.highlight || item.summary }}</text>
				<view class="result-meta">
					<text class="result-score" v-if="item.score">相关度: {{ (item.score * 100).toFixed(0) }}%</text>
					<text class="result-source">{{ sourceText(item.source) }}</text>
				</view>
			</view>
		</view>
		
		<!-- 空结果 -->
		<view class="empty-result" v-if="keyword && !results.length && searched">
			<Icon name="search" size="48" class="empty-icon" />
			<text class="empty-text">未找到相关内容</text>
			<text class="empty-tip">试试其他关键词，或使用语义搜索</text>
		</view>
		
		<!-- AI搜索建议 -->
		<view class="ai-suggest" v-if="keyword && !results.length && searched" @click="askAI">
			<Icon name="robot" size="20" class="suggest-icon" />
			<text class="suggest-text">让AI帮你查找相关内容</text>
		</view>
	</view>
</template>

<script setup>
import { ref, watch } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { searchKnowledge } from '@/api/knowledge'
import { getBackgroundStyle, applyGlobalBackground } from '@/utils/theme'
import Icon from '@/components/Icon.vue'

const keyword = ref('')
const searchType = ref('semantic')
const results = ref([])
const searched = ref(false)
const history = ref([])
const hotKeywords = ref(['开发规范', '数据库设计', '项目文档', 'API接口', '常见问题'])
const pageStyle = ref(getBackgroundStyle())

// 从本地存储加载历史
const loadHistory = () => {
	try {
		const stored = uni.getStorageSync('search_history')
		if (stored) {
			history.value = JSON.parse(stored)
		}
	} catch (e) {}
}
loadHistory()

const search = async () => {
	if (!keyword.value.trim()) return
	
	// 保存搜索历史
	saveHistory(keyword.value.trim())
	
	searched.value = true
	
	try {
		const res = await searchKnowledge({
			query: keyword.value,
			type: searchType.value
		})
		results.value = (res.data || []).map(item => ({
			...item,
			score: item.score ?? item.similarity ?? 0
		}))
	} catch (e) {
		results.value = []
		uni.showToast({ title: '搜索失败', icon: 'none' })
	}
}

const onInput = (e) => {
	if (!e.detail.value) {
		results.value = []
		searched.value = false
	}
}

const quickSearch = (text) => {
	keyword.value = text
	search()
}

const saveHistory = (text) => {
	const index = history.value.indexOf(text)
	if (index > -1) {
		history.value.splice(index, 1)
	}
	history.value.unshift(text)
	if (history.value.length > 10) {
		history.value = history.value.slice(0, 10)
	}
	uni.setStorageSync('search_history', JSON.stringify(history.value))
}

const clearHistory = () => {
	history.value = []
	uni.removeStorageSync('search_history')
}

const clearKeyword = () => {
	keyword.value = ''
	results.value = []
	searched.value = false
}

const goBack = () => {
	uni.navigateBack()
}

const goDetail = (item) => {
	uni.navigateTo({
		url: `/pages/knowledge/detail?id=${item.id}`
	})
}

const askAI = () => {
	uni.navigateTo({
		url: `/pages/chat/conversation?id=new&prompt=${encodeURIComponent('帮我查找关于 "' + keyword.value + '" 的相关内容')}`
	})
}

const sourceText = (source) => {
	const map = {
		chat: '聊天提取',
		manual: '手动添加',
		import: '导入'
	}
	return map[source] || source
}

watch(searchType, () => {
	if (keyword.value) {
		search()
	}
})

onShow(() => {
	pageStyle.value = getBackgroundStyle()
	applyGlobalBackground()
})
</script>

<style scoped>
.search-page {
	min-height: 100vh;
	padding-bottom: 60rpx;
	background: transparent;
	overflow-y: auto;
	-webkit-overflow-scrolling: touch;
}

.page-hero {
	padding: 28rpx 24rpx 6rpx;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.hero-texts {
	display: flex;
	flex-direction: column;
	gap: 6rpx;
}

.hero-title {
	font-size: 34rpx;
	font-weight: 700;
	color: var(--brand-ink);
}

.hero-desc {
	font-size: 24rpx;
	color: var(--brand-muted);
}

.hero-pill {
	display: flex;
	align-items: center;
	gap: 10rpx;
	padding: 12rpx 16rpx;
	background: rgba(16, 240, 194, 0.12);
	border-radius: 999rpx;
	border: 1rpx solid rgba(16, 240, 194, 0.25);
	margin-right: 12rpx;
	box-shadow: 0 10rpx 22rpx rgba(0, 0, 0, 0.35);
}

.pill-dot {
	width: 14rpx;
	height: 14rpx;
	background: #06AD56;
	border-radius: 50%;
}

.pill-text {
	font-size: 24rpx;
	color: var(--brand-ink);
}

.search-bar {
	display: flex;
	align-items: center;
	padding: 16rpx 24rpx;
}

.search-input-wrapper {
	flex: 1;
	display: flex;
	align-items: center;
	padding: 18rpx 24rpx;
	background-color: var(--card);
	border-radius: 24rpx;
	box-shadow: var(--shadow-plain);
	border: 1rpx solid var(--border);
}

.search-icon {
	margin-right: 12rpx;
	color: var(--brand-muted);
}

.search-input {
	flex: 1;
	font-size: 28rpx;
	color: var(--brand-ink);
}

.clear-btn {
	padding: 6rpx;
}

.cancel-btn {
	font-size: 28rpx;
	color: #06AD56;
	padding: 16rpx 18rpx;
}

.search-type {
	display: flex;
	padding: 0 24rpx 16rpx;
	gap: 12rpx;
}

.type-item {
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 16rpx;
	border-radius: 14rpx;
	background-color: var(--card);
	border: 1rpx solid var(--border);
}

.type-item.active {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	box-shadow: var(--shadow-soft);
}

.type-icon {
	margin-right: 8rpx;
	color: var(--brand-muted);
}

.type-text {
	font-size: 26rpx;
	color: var(--brand-muted);
}

.type-item.active .type-text {
	color: #ffffff;
}

.hot-search, .history {
	padding: 28rpx 24rpx;
	background-color: var(--card);
	margin: 16rpx 20rpx 0;
	border-radius: 18rpx;
	box-shadow: var(--shadow-plain);
	border: 1rpx solid var(--border);
}

.section-title {
	font-size: 28rpx;
	color: var(--brand-ink);
	font-weight: 600;
	margin-bottom: 18rpx;
}

.hot-tags {
	display: flex;
	flex-wrap: wrap;
	gap: 16rpx;
}

.hot-tag {
	font-size: 26rpx;
	color: #06AD56;
	padding: 12rpx 24rpx;
	background-color: rgba(16, 240, 194, 0.12);
	border-radius: 24rpx;
	border: 1rpx solid rgba(16, 240, 194, 0.3);
}

.history-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 18rpx;
}

.clear-history {
	font-size: 26rpx;
	color: var(--brand-muted);
}

.history-list {
	display: flex;
	flex-wrap: wrap;
	gap: 16rpx;
}

.history-item {
	font-size: 26rpx;
	color: #06AD56;
	padding: 12rpx 24rpx;
	background-color: rgba(16, 240, 194, 0.12);
	border-radius: 24rpx;
	border: 1rpx solid rgba(16, 240, 194, 0.3);
}

.results {
	padding: 16rpx 20rpx 0;
}

.result-header {
	margin-bottom: 20rpx;
}

.result-count {
	font-size: 26rpx;
	color: var(--brand-muted);
}

.result-item {
	background-color: var(--card);
	border-radius: 18rpx;
	padding: 24rpx;
	margin-bottom: 18rpx;
	box-shadow: var(--shadow-plain);
	border: 1rpx solid var(--border);
}

.result-title {
	font-size: 32rpx;
	color: var(--brand-ink);
	font-weight: 600;
	display: block;
	margin-bottom: 12rpx;
}

.result-content {
	font-size: 28rpx;
	color: var(--brand-muted);
	line-height: 1.6;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
	margin-bottom: 16rpx;
}

.result-meta {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.result-score {
	font-size: 24rpx;
	color: #06AD56;
}

.result-source {
	font-size: 24rpx;
	color: var(--brand-muted);
}

.empty-result {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 120rpx 48rpx;
}

.empty-icon {
	margin-bottom: 24rpx;
}

.empty-text {
	font-size: 32rpx;
	color: var(--brand-ink);
	margin-bottom: 12rpx;
	font-weight: 600;
}

.empty-tip {
	font-size: 26rpx;
	color: var(--brand-muted);
}

.ai-suggest {
	display: flex;
	align-items: center;
	justify-content: center;
	margin: 0 48rpx;
	padding: 24rpx;
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	border-radius: 16rpx;
	box-shadow: var(--shadow-soft);
	border: 1rpx solid rgba(16, 240, 194, 0.4);
}

.suggest-icon {
	margin-right: 12rpx;
}

.suggest-text {
	font-size: 28rpx;
	color: #fff;
}
</style>
