<template>
	<view class="stats" :style="pageStyle">
		<!-- 时间选择 -->
		<view class="time-tabs">
			<view 
				class="tab-item" 
				:class="{ 'active': timeRange === 'week' }"
				@click="timeRange = 'week'"
			>本周</view>
			<view 
				class="tab-item" 
				:class="{ 'active': timeRange === 'month' }"
				@click="timeRange = 'month'"
			>本月</view>
			<view 
				class="tab-item" 
				:class="{ 'active': timeRange === 'year' }"
				@click="timeRange = 'year'"
			>本年</view>
		</view>
		
		<!-- 概览卡片 -->
		<view class="overview-card">
			<view class="overview-item">
				<text class="overview-num">{{ overview.knowledge }}</text>
				<text class="overview-label">知识总数</text>
				<text class="overview-trend up">↑ {{ overview.knowledgeTrend }}%</text>
			</view>
			<view class="overview-divider"></view>
			<view class="overview-item">
				<text class="overview-num">{{ overview.conversation }}</text>
				<text class="overview-label">对话次数</text>
				<text class="overview-trend up">↑ {{ overview.conversationTrend }}%</text>
			</view>
			<view class="overview-divider"></view>
			<view class="overview-item">
				<text class="overview-num">{{ overview.aiCalls }}</text>
				<text class="overview-label">AI调用</text>
				<text class="overview-trend" :class="overview.aiTrend >= 0 ? 'up' : 'down'">
					{{ overview.aiTrend >= 0 ? '↑' : '↓' }} {{ Math.abs(overview.aiTrend) }}%
				</text>
			</view>
		</view>
		
		<!-- 知识来源分布 -->
		<view class="chart-card">
			<text class="chart-title">知识来源分布</text>
			<view class="pie-chart">
				<view class="pie-item" v-for="item in sourceData" :key="item.name">
					<view class="pie-bar" :style="{ width: item.percent + '%', backgroundColor: item.color }"></view>
					<view class="pie-info">
						<view class="pie-dot" :style="{ backgroundColor: item.color }"></view>
						<text class="pie-name">{{ item.name }}</text>
						<text class="pie-value">{{ item.value }} ({{ item.percent }}%)</text>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 每日新增趋势 -->
		<view class="chart-card">
			<text class="chart-title">每日新增知识</text>
			<view class="bar-chart">
				<view class="bar-item" v-for="item in dailyData" :key="item.date">
					<view class="bar" :style="{ height: item.height + '%' }">
						<text class="bar-value">{{ item.value }}</text>
					</view>
					<text class="bar-label">{{ item.label }}</text>
				</view>
			</view>
		</view>
		
		<!-- 热门标签 -->
		<view class="chart-card">
			<text class="chart-title">热门标签 TOP10</text>
			<view class="tag-list">
				<view class="tag-item" v-for="(item, index) in hotTags" :key="item.name">
					<text class="tag-rank" :class="{ 'top3': index < 3 }">{{ index + 1 }}</text>
					<text class="tag-name">{{ item.name }}</text>
					<view class="tag-bar-wrapper">
						<view class="tag-bar" :style="{ width: item.percent + '%' }"></view>
					</view>
					<text class="tag-count">{{ item.count }}</text>
				</view>
			</view>
		</view>
		
		<!-- AI使用统计 -->
		<view class="chart-card">
			<text class="chart-title">AI功能使用</text>
			<view class="ai-stats">
				<view class="ai-item" v-for="item in aiStats" :key="item.name">
					<view class="ai-icon">
						<Icon :name="item.icon" size="20" />
					</view>
					<view class="ai-info">
						<text class="ai-name">{{ item.name }}</text>
						<view class="ai-bar-wrapper">
							<view class="ai-bar" :style="{ width: item.percent + '%' }"></view>
						</view>
					</view>
					<text class="ai-count">{{ item.count }}次</text>
				</view>
			</view>
		</view>
		
		<view class="bottom-spacer" style="height: 120rpx;"></view>
		<CustomTabBar :currentTab="3" />
	</view>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import Icon from '@/components/Icon.vue'
import CustomTabBar from '@/components/CustomTabBar.vue'
import { getStats } from '@/api/user'
import { getKnowledgeList } from '@/api/knowledge'
import { getBackgroundStyle, applyGlobalBackground } from '@/utils/theme'

const timeRange = ref('week')
const loading = ref(false)

const overview = ref({
	knowledge: 0,
	knowledgeTrend: 0,
	conversation: 0,
	conversationTrend: 0,
	aiCalls: 0,
	aiTrend: 0
})

const sourceData = ref([])
const dailyData = ref([])
const hotTags = ref([])
const aiStats = ref([])
const pageStyle = ref(getBackgroundStyle())

onMounted(() => {
	loadStats(timeRange.value)
	applyGlobalBackground()
})

onShow(() => {
	pageStyle.value = getBackgroundStyle()
	applyGlobalBackground()
})

watch(timeRange, (val) => {
	loadStats(val)
})

const loadStats = async (range) => {
	loading.value = true
	try {
		const [statsRes, knowledgeRes] = await Promise.allSettled([
			getStats(),
			getKnowledgeList({ page: 1, size: 100 })
		])

		if (statsRes.status === 'fulfilled' && statsRes.value.data) {
			const s = statsRes.value.data
			overview.value = {
				knowledge: s.knowledge || 0,
				knowledgeTrend: 0,
				conversation: s.conversation || 0,
				conversationTrend: 0,
				aiCalls: s.aiCalls || 0,
				aiTrend: 0
			}
		}

		const list = (knowledgeRes.status === 'fulfilled' && knowledgeRes.value.data) ? knowledgeRes.value.data : []
		buildSourceData(list)
		buildDailyData(list, range)
		buildTags(list)
		buildAIStats()
	} catch (e) {
		uni.showToast({ title: '统计获取失败', icon: 'none' })
	} finally {
		loading.value = false
	}
}

const buildSourceData = (list) => {
	const map = {
		chat: { name: '聊天提取', color: '#07C160', value: 0 },
		manual: { name: '手动添加', color: '#1890ff', value: 0 },
		import: { name: '文件导入', color: '#06AD56', value: 0 },
		monitor: { name: '监控入库', color: '#10b981', value: 0 }
	}
	list.forEach(item => {
		const key = item.source || 'manual'
		if (map[key]) {
			map[key].value += 1
		} else {
			map.manual.value += 1
		}
	})
	const total = Object.values(map).reduce((s, i) => s + i.value, 0) || 1
	sourceData.value = Object.values(map)
		.filter(i => i.value > 0)
		.map(i => ({ ...i, percent: Math.round((i.value / total) * 100) }))
}

const buildDailyData = (list, range) => {
	const daysMap = {}
	list.forEach(item => {
		if (!item.createdAt) return
		const d = new Date(item.createdAt)
		const key = `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`
		daysMap[key] = (daysMap[key] || 0) + 1
	})
	const limit = range === 'week' ? 7 : range === 'month' ? 30 : 90
	const today = new Date()
	const data = []
	for (let i = limit - 1; i >= 0; i--) {
		const d = new Date(today.getTime() - i * 86400000)
		const key = `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`
		const label = `${(d.getMonth() + 1)}/${d.getDate()}`
		data.push({ date: key, label, value: daysMap[key] || 0 })
	}
	const max = Math.max(...data.map(d => d.value), 1)
	dailyData.value = data.map(d => ({ ...d, height: Math.round((d.value / max) * 100) }))
}

const buildTags = (list) => {
	const counter = {}
	list.forEach(item => {
		(item.tags || []).forEach(tag => {
			if (!tag) return
			counter[tag] = (counter[tag] || 0) + 1
		})
	})
	const sorted = Object.entries(counter)
		.sort((a, b) => b[1] - a[1])
		.slice(0, 10)
	const max = sorted.length ? sorted[0][1] : 1
	hotTags.value = sorted.map(([name, count]) => ({
		name,
		count,
		percent: Math.round((count / max) * 100)
	}))
}

const buildAIStats = () => {
	const items = [
		{ name: '智能对话', icon: 'robot', count: overview.value.aiCalls || 0 },
		{ name: '知识检索', icon: 'search', count: overview.value.knowledge || 0 },
		{ name: '自动总结', icon: 'note', count: 0 },
		{ name: '标签生成', icon: 'tag', count: 0 },
		{ name: '内容整理', icon: 'clipboard', count: 0 }
	]
	const max = Math.max(...items.map(i => i.count), 1)
	aiStats.value = items.map(i => ({
		...i,
		percent: max ? Math.round((i.count / max) * 100) : 0
	}))
}
</script>

<style scoped>
.stats {
	min-height: 100vh;
	background-color: transparent;
	padding-bottom: 48rpx;
	overflow-y: auto;
	-webkit-overflow-scrolling: touch;
}

.time-tabs {
	display: flex;
	background-color: #fff;
	padding: 24rpx 32rpx;
}

.tab-item {
	flex: 1;
	text-align: center;
	padding: 16rpx;
	font-size: 28rpx;
	color: #666;
	border-radius: 8rpx;
}

.tab-item.active {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	color: #fff;
}

.overview-card {
	display: flex;
	margin: 24rpx;
	padding: 32rpx;
	background-color: #fff;
	border-radius: 16rpx;
}

.overview-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
}

.overview-num {
	font-size: 48rpx;
	color: #333;
	font-weight: 600;
}

.overview-label {
	font-size: 24rpx;
	color: #999;
	margin: 8rpx 0;
}

.overview-trend {
	font-size: 22rpx;
	padding: 4rpx 12rpx;
	border-radius: 16rpx;
}

.overview-trend.up {
	color: #07C160;
	background-color: #e8f5e9;
}

.overview-trend.down {
	color: #ff4d4f;
	background-color: #fff2f0;
}

.overview-divider {
	width: 1rpx;
	background-color: #f0f0f0;
	margin: 0 16rpx;
}

.chart-card {
	margin: 24rpx;
	padding: 32rpx;
	background-color: #fff;
	border-radius: 16rpx;
}

.chart-title {
	font-size: 30rpx;
	color: #333;
	font-weight: 500;
	margin-bottom: 32rpx;
	display: block;
}

/* 饼图样式 */
.pie-chart {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.pie-item {
	display: flex;
	flex-direction: column;
	gap: 12rpx;
}

.pie-bar {
	height: 24rpx;
	border-radius: 12rpx;
}

.pie-info {
	display: flex;
	align-items: center;
}

.pie-dot {
	width: 16rpx;
	height: 16rpx;
	border-radius: 50%;
	margin-right: 12rpx;
}

.pie-name {
	font-size: 26rpx;
	color: #666;
	margin-right: 16rpx;
}

.pie-value {
	font-size: 26rpx;
	color: #999;
}

/* 柱状图 */
.bar-chart {
	display: flex;
	justify-content: space-between;
	align-items: flex-end;
	height: 300rpx;
	padding-top: 40rpx;
}

.bar-item {
	display: flex;
	flex-direction: column;
	align-items: center;
	width: 60rpx;
}

.bar {
	width: 40rpx;
	background: linear-gradient(180deg, #07C160 0%, #06AD56 100%);
	border-radius: 8rpx 8rpx 0 0;
	display: flex;
	justify-content: center;
	min-height: 20rpx;
}

.bar-value {
	font-size: 22rpx;
	color: #fff;
	margin-top: -32rpx;
}

.bar-label {
	font-size: 22rpx;
	color: #999;
	margin-top: 12rpx;
}

/* 热门标签 */
.tag-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.tag-item {
	display: flex;
	align-items: center;
}

.tag-rank {
	width: 40rpx;
	font-size: 26rpx;
	color: #999;
	font-weight: 500;
}

.tag-rank.top3 {
	color: #07C160;
}

.tag-name {
	width: 140rpx;
	font-size: 26rpx;
	color: #333;
}

.tag-bar-wrapper {
	flex: 1;
	height: 20rpx;
	background-color: #f5f5f5;
	border-radius: 10rpx;
	margin: 0 20rpx;
	overflow: hidden;
}

.tag-bar {
	height: 100%;
	background: linear-gradient(90deg, #07C160 0%, #06AD56 100%);
	border-radius: 10rpx;
}

.tag-count {
	width: 60rpx;
	font-size: 26rpx;
	color: #999;
	text-align: right;
}

/* AI统计 */
.ai-stats {
	display: flex;
	flex-direction: column;
	gap: 24rpx;
}

.ai-item {
	display: flex;
	align-items: center;
}

.ai-icon {
	width: 60rpx;
	height: 60rpx;
	background-color: #f5f5f5;
	border-radius: 12rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 16rpx;
	color: #07C160;
}

.ai-info {
	flex: 1;
}

.ai-name {
	font-size: 28rpx;
	color: #333;
	display: block;
	margin-bottom: 8rpx;
}

.ai-bar-wrapper {
	height: 12rpx;
	background-color: #f5f5f5;
	border-radius: 6rpx;
	overflow: hidden;
}

.ai-bar {
	height: 100%;
	background: linear-gradient(90deg, #059669 0%, #047857 100%);
	border-radius: 6rpx;
}

.ai-count {
	width: 100rpx;
	font-size: 26rpx;
	color: #666;
	text-align: right;
}
</style>
