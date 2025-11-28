<template>
	<view class="settings-page" :style="pageStyle">
		<view class="section">
			<text class="section-title">通用</text>
			<view class="card">
				<view class="row" @click="goAvatar">
					<view class="row-texts">
						<text class="row-title">头像设置</text>
						<text class="row-desc">自定义用户和 AI 头像</text>
					</view>
					<text class="row-arrow">›</text>
				</view>
				<view class="row" @click="goBackground">
					<view class="row-texts">
						<text class="row-title">背景设置</text>
						<text class="row-desc">自定义页面背景颜色/渐变/图片</text>
					</view>
					<text class="row-arrow">›</text>
				</view>
			</view>
		</view>

		<view class="section">
			<text class="section-title">AI</text>
			<view class="card">
				<view class="row" @click="goAI">
					<view class="row-texts">
						<text class="row-title">AI 配置</text>
						<text class="row-desc">模型、温度、接口 Key 等</text>
					</view>
					<text class="row-arrow">›</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref } from 'vue'
import { getBackgroundStyle, applyGlobalBackground } from '@/utils/theme'

const pageStyle = ref(getBackgroundStyle())

applyGlobalBackground()

const goAvatar = () => {
	uni.navigateTo({
		url: '/pages/mine/settings/avatar'
	})
}

const goBackground = () => {
	uni.navigateTo({
		url: '/pages/mine/settings/background'
	})
}

const goAI = () => {
	uni.navigateTo({
		url: '/pages/mine/settings/ai'
	})
}
</script>

<style scoped>
.settings-page {
	min-height: 100vh;
	padding: 16px;
	background: transparent;
}

.section {
	margin-bottom: 18px;
}

.section-title {
	font-size: 14px;
	color: var(--brand-muted);
	margin-bottom: 8px;
	display: block;
}

.card {
	background: var(--card);
	border: 1px solid var(--border);
	border-radius: 14px;
	box-shadow: var(--shadow-plain);
	overflow: hidden;
}

.row {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 16px;
	border-bottom: 1px solid var(--border);
}

.row:last-child {
	border-bottom: none;
}

.row-texts {
	display: flex;
	flex-direction: column;
	gap: 4px;
}

.row-title {
	font-size: 16px;
	color: var(--brand-ink);
	font-weight: 600;
}

.row-desc {
	font-size: 13px;
	color: var(--brand-muted);
}

.row-arrow {
	font-size: 20px;
	color: var(--brand-muted);
}
</style>
