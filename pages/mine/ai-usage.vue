<template>
	<view class="usage-page" :style="pageStyle">
		<view class="header">
			<text class="title">AI 使用监控</text>
			<text class="subtitle">{{ data.period }} 调用统计</text>
		</view>

		<!-- 时间筛选 -->
		<view class="time-tabs">
			<view 
				class="time-tab" 
				:class="{ active: days === 1 }" 
				@click="changeDays(1)"
			>今日</view>
			<view 
				class="time-tab" 
				:class="{ active: days === 7 }" 
				@click="changeDays(7)"
			>近7天</view>
			<view 
				class="time-tab" 
				:class="{ active: days === 30 }" 
				@click="changeDays(30)"
			>近30天</view>
		</view>

		<!-- 总览卡片 -->
		<view class="summary-card">
			<view class="summary-row">
				<view class="summary-item">
					<text class="label">调用次数</text>
					<text class="value">{{ data.summary.calls }}</text>
				</view>
				<view class="divider"></view>
				<view class="summary-item">
					<text class="label">总 Token</text>
					<text class="value">{{ formatNumber(data.summary.tokens) }}</text>
				</view>
				<view class="divider"></view>
				<view class="summary-item">
					<text class="label">总成本</text>
					<text class="value cost">¥{{ data.summary.cost }}</text>
				</view>
			</view>
			
			<view class="token-detail">
				<view class="token-item">
					<text class="token-label">输入</text>
					<text class="token-value">{{ formatNumber(data.summary.inputTokens) }}</text>
				</view>
				<view class="token-item">
					<text class="token-label">输出</text>
					<text class="token-value">{{ formatNumber(data.summary.outputTokens) }}</text>
				</view>
				<view class="token-item">
					<text class="token-label">缓存命中</text>
					<text class="token-value highlight">{{ formatNumber(data.summary.cachedTokens) }}</text>
				</view>
			</view>
		</view>

		<!-- 模型统计 -->
		<view class="card">
			<view class="card-header">
				<text class="card-title">模型分布</text>
			</view>
			<view class="model-list">
				<view class="model-row" v-for="(item, index) in data.models" :key="index">
					<view class="model-main">
						<view class="model-name-row">
							<text class="model-name">{{ item.model }}</text>
							<text class="provider-tag">{{ getProviderName(item.provider) }}</text>
						</view>
						<text class="model-stats">
							{{ item.calls }}次 · {{ formatNumber(item.tokens) }} Token
						</text>
					</view>
					<view class="model-right">
						<view class="model-detail">
							<text class="detail-item">输入 {{ formatNumber(item.inputTokens) }}</text>
							<text class="detail-item">输出 {{ formatNumber(item.outputTokens) }}</text>
							<text class="detail-item cached" v-if="item.cachedTokens > 0">
								缓存 {{ formatNumber(item.cachedTokens) }}
							</text>
						</view>
						<text class="model-cost">¥{{ item.cost }}</text>
					</view>
				</view>
				<view class="empty" v-if="!data.models.length">
					<text>暂无调用记录</text>
				</view>
			</view>
		</view>

		<!-- 费用说明 -->
		<view class="card tips-card">
			<view class="card-header">
				<text class="card-title">💡 费用说明</text>
			</view>
			<view class="tips">
				<view class="tip-row">
					<text class="tip-model">智谱 glm-4.5-flash</text>
					<text class="tip-price free">免费</text>
				</view>
				<view class="tip-row">
					<text class="tip-model">通义 qwen-turbo</text>
					<text class="tip-price">¥0.3/M输入 ¥0.6/M输出</text>
				</view>
				<view class="tip-row">
					<text class="tip-model">DeepSeek chat</text>
					<text class="tip-price">¥1/M输入 ¥2/M输出</text>
				</view>
				<view class="tip-row">
					<text class="tip-model">缓存命中</text>
					<text class="tip-price free">节省 80% 输入费用</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getAIUsage } from '@/api/user'
import { applyGlobalBackground, getBackgroundStyle } from '@/utils/theme'

const days = ref(1)

const data = reactive({
	period: '今日',
	summary: {
		calls: 0,
		tokens: 0,
		inputTokens: 0,
		outputTokens: 0,
	cachedTokens: 0,
	cost: 0
	},
	models: []
})
const pageStyle = getBackgroundStyle()

const providerNames = {
	zhipu: '智谱',
	qwen: '通义',
	deepseek: 'DeepSeek',
	openai: 'OpenAI',
	kimi: 'Kimi',
	unknown: '未知'
}

const getProviderName = (provider) => {
	return providerNames[provider] || provider || '未知'
}

const formatNumber = (num) => {
	if (!num) return '0'
	if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
	if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
	return num.toString()
}

const loadUsage = async () => {
	try {
		const res = await getAIUsage(days.value)
		if (res.data) {
			data.period = res.data.period || '今日'
			data.summary = res.data.summary || data.summary
			data.models = res.data.models || []
		}
	} catch (e) {
		console.log('加载失败', e)
	}
}

const changeDays = (d) => {
	days.value = d
	loadUsage()
}

onMounted(() => {
	loadUsage()
	applyGlobalBackground()
})

onShow(() => {
	loadUsage()
	applyGlobalBackground()
})
</script>

<style scoped>
.usage-page {
	min-height: 100vh;
	background: #f5f5f5;
	padding: 24rpx;
	padding-bottom: 120rpx;
	box-sizing: border-box;
}

.header {
	margin-bottom: 20rpx;
}

.title {
	font-size: 36rpx;
	font-weight: 700;
	color: #333;
	display: block;
}

.subtitle {
	font-size: 26rpx;
	color: #666;
	margin-top: 4rpx;
}

/* 时间筛选 */
.time-tabs {
	display: flex;
	background: #fff;
	border-radius: 12rpx;
	padding: 8rpx;
	margin-bottom: 20rpx;
}

.time-tab {
	flex: 1;
	text-align: center;
	padding: 16rpx 0;
	font-size: 26rpx;
	color: #666;
	border-radius: 8rpx;
}

.time-tab.active {
	background: #07C160;
	color: #fff;
	font-weight: 500;
}

/* 总览卡片 */
.summary-card {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	border-radius: 16rpx;
	padding: 28rpx;
	margin-bottom: 20rpx;
	color: #fff;
}

.summary-row {
	display: flex;
	align-items: center;
	margin-bottom: 24rpx;
}

.summary-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
}

.summary-item .label {
	font-size: 24rpx;
	opacity: 0.9;
	margin-bottom: 8rpx;
}

.summary-item .value {
	font-size: 36rpx;
	font-weight: 700;
}

.summary-item .value.cost {
	color: #FFE066;
}

.divider {
	width: 1rpx;
	height: 60rpx;
	background: rgba(255,255,255,0.3);
}

.token-detail {
	display: flex;
	justify-content: space-around;
	background: rgba(255,255,255,0.15);
	border-radius: 12rpx;
	padding: 16rpx;
}

.token-item {
	display: flex;
	flex-direction: column;
	align-items: center;
}

.token-label {
	font-size: 22rpx;
	opacity: 0.8;
}

.token-value {
	font-size: 26rpx;
	font-weight: 600;
	margin-top: 4rpx;
}

.token-value.highlight {
	color: #FFE066;
}

/* 卡片 */
.card {
	background: #fff;
	border-radius: 16rpx;
	margin-bottom: 20rpx;
	overflow: hidden;
}

.card-header {
	padding: 24rpx;
	border-bottom: 1rpx solid #f5f5f5;
}

.card-title {
	font-size: 30rpx;
	color: #333;
	font-weight: 600;
}

/* 模型列表 */
.model-list {
	padding: 0 24rpx;
}

.model-row {
	display: flex;
	justify-content: space-between;
	padding: 20rpx 0;
	border-bottom: 1rpx solid #f5f5f5;
}

.model-row:last-child {
	border-bottom: none;
}

.model-main {
	flex: 1;
}

.model-name-row {
	display: flex;
	align-items: center;
	gap: 12rpx;
	margin-bottom: 6rpx;
}

.model-name {
	font-size: 28rpx;
	color: #333;
	font-weight: 600;
}

.provider-tag {
	font-size: 20rpx;
	color: #07C160;
	background: #E8F8EE;
	padding: 4rpx 12rpx;
	border-radius: 6rpx;
}

.model-stats {
	font-size: 24rpx;
	color: #888;
}

.model-right {
	display: flex;
	flex-direction: column;
	align-items: flex-end;
}

.model-detail {
	display: flex;
	gap: 16rpx;
	margin-bottom: 6rpx;
}

.detail-item {
	font-size: 22rpx;
	color: #999;
}

.detail-item.cached {
	color: #07C160;
}

.model-cost {
	font-size: 28rpx;
	color: #FF9500;
	font-weight: 600;
}

/* 空状态 */
.empty {
	padding: 60rpx;
	text-align: center;
	color: #999;
	font-size: 26rpx;
}

/* 费用说明 */
.tips-card {
	margin-top: 20rpx;
}

.tips {
	padding: 16rpx 24rpx;
}

.tip-row {
	display: flex;
	justify-content: space-between;
	padding: 12rpx 0;
	border-bottom: 1rpx solid #f8f8f8;
}

.tip-row:last-child {
	border-bottom: none;
}

.tip-model {
	font-size: 26rpx;
	color: #666;
}

.tip-price {
	font-size: 26rpx;
	color: #999;
}

.tip-price.free {
	color: #07C160;
	font-weight: 500;
}
</style>
