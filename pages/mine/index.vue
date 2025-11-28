<template>
	<view class="admin-panel" :style="pageStyle">
		<!-- 头部：管理员概览 -->
		<view class="header-card">
			<view class="header-row">
				<view class="user-info">
					<text class="welcome-text">欢迎回来,</text>
					<text class="username">{{ userInfo.name || 'Admin' }}</text>
				</view>
				<view class="avatar-circle" @click="goAccountSettings">
					<image v-if="userInfo.avatar" :src="userInfo.avatar" class="avatar-img" mode="aspectFill" />
					<text v-else class="avatar-initial">{{ userInfo.name ? userInfo.name[0] : 'A' }}</text>
				</view>
			</view>
			<view class="role-badge">
				<text class="role-text">超级管理员</text>
			</view>
		</view>
		
		<!-- 核心指标 Dashboard -->
		<view class="dashboard-grid">
			<view class="stat-box">
				<text class="stat-label">知识条目</text>
				<text class="stat-value">{{ stats.knowledge }}</text>
				<view class="trend-row up">
					<text class="trend-arrow">↑</text>
					<text class="trend-val">12%</text>
					<text class="trend-desc">周环比</text>
				</view>
			</view>
			<view class="stat-box">
				<text class="stat-label">AI 调用次数</text>
				<text class="stat-value">{{ stats.aiCalls }}</text>
				<view class="trend-row up">
					<text class="trend-arrow">↑</text>
					<text class="trend-val">5%</text>
					<text class="trend-desc">周环比</text>
				</view>
			</view>
			<view class="stat-box">
				<text class="stat-label">活跃会话</text>
				<text class="stat-value">{{ stats.conversation }}</text>
				<view class="trend-row down">
					<text class="trend-arrow">↓</text>
					<text class="trend-val">2%</text>
					<text class="trend-desc">周环比</text>
				</view>
			</view>
		</view>
		
		<!-- 管理菜单 -->
		<view class="menu-section">
			<view class="section-title">系统管理</view>
			<view class="menu-list">
				<view class="menu-row" @click="goPage('/pages/knowledge/index')">
					<text class="menu-name">知识库索引管理</text>
					<text class="menu-status normal">运行中</text>
				</view>
				<view class="menu-row" @click="goPage('/pages/mine/server-monitor')">
					<text class="menu-name">后台监控</text>
					<text class="menu-desc">日志 · 异常</text>
				</view>
				<view class="menu-row" @click="goDataSync">
					<text class="menu-name">数据同步与备份</text>
					<text class="menu-arrow">></text>
				</view>
				<view class="menu-row" @click="goExport">
					<text class="menu-name">审计日志导出</text>
					<text class="menu-arrow">></text>
				</view>
			</view>
		</view>
		
		<view class="menu-section">
			<view class="section-title">模型配置</view>
			<view class="menu-list">
				<view class="menu-row" @click="goAISettings">
					<text class="menu-name">LLM 参数设置</text>
					<text class="menu-desc">GPT-4o</text>
				</view>
				<view class="menu-row" @click="goMonitor">
					<text class="menu-name">敏感词监控</text>
					<view class="switch-text" :class="{ on: monitorEnabled }">{{ monitorEnabled ? 'ON' : 'OFF' }}</view>
				</view>
				<view class="menu-row" @click="goAIUsage">
					<text class="menu-name">AI 使用监控</text>
					<text class="menu-arrow">›</text>
				</view>
			</view>
		</view>

		<view class="menu-section">
			<view class="section-title">设置</view>
			<view class="menu-list">
				<view class="menu-row" @click="goAccountSettings">
					<text class="menu-name">账号设置</text>
					<text class="menu-desc">修改头像、密码</text>
				</view>
				<view class="menu-row" @click="goSettings">
					<text class="menu-name">通用设置</text>
					<text class="menu-arrow">›</text>
				</view>
			</view>
		</view>

		<view class="logout-area" @click="logout">
			<text class="logout-text">退出登录</text>
		</view>
		
		<view class="bottom-spacer" style="height: 120rpx;"></view>
		<CustomTabBar :currentTab="4" />
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getUserInfo, getStats } from '@/api/user'
import { getBackgroundStyle, applyGlobalBackground } from '@/utils/theme'
import CustomTabBar from '@/components/CustomTabBar.vue'

const userInfo = ref({
	id: '',
	name: '',
	avatar: '',
	desc: ''
})

const stats = ref({
	knowledge: 0,
	conversation: 0,
	aiCalls: 0
})

const monitorEnabled = ref(true)
const pageStyle = ref(getBackgroundStyle())

onMounted(() => {
	loadUserInfo()
	loadStats()
	pageStyle.value = getBackgroundStyle()
	applyGlobalBackground()
})

onShow(() => {
	pageStyle.value = getBackgroundStyle()
	applyGlobalBackground()
})

const loadUserInfo = async () => {
	try {
		const res = await getUserInfo()
		userInfo.value = res.data
	} catch (e) {
		userInfo.value = {
			id: '1',
			name: 'Admin',
			desc: 'Administrator'
		}
	}
}

const loadStats = async () => {
	try {
		const res = await getStats()
		stats.value = res.data
	} catch (e) {
		stats.value = {
			knowledge: 1285,
			conversation: 563,
			aiCalls: 23401
		}
	}
}

const logout = () => {
	uni.showModal({
		title: '确认退出',
		content: '退出后需要重新登录',
		confirmColor: '#D54941',
		success: (res) => {
			if (res.confirm) {
				uni.removeStorageSync('token')
				uni.removeStorageSync('userInfo')
				uni.showToast({ title: '已退出', icon: 'success' })
				setTimeout(() => {
					uni.reLaunch({ url: '/pages/login/index' })
				}, 1000)
			}
		}
	})
}

const goPage = (url) => {
	uni.navigateTo({ url })
}

const goDataSync = () => {
	uni.showToast({ title: '开始同步...', icon: 'none' })
}

const goExport = () => {
	uni.showToast({ title: '生成报告中...', icon: 'none' })
}

const goAISettings = () => {
	uni.navigateTo({
		url: '/pages/mine/settings/ai'
	})
}

const goAIUsage = () => {
	uni.navigateTo({
		url: '/pages/mine/ai-usage'
	})
}

const goMonitor = () => {
	monitorEnabled.value = !monitorEnabled.value
}

const goSettings = () => {
	uni.navigateTo({
		url: '/pages/mine/settings'
	})
}

const goAccountSettings = () => {
	uni.navigateTo({
		url: '/pages/mine/settings/account'
	})
}
</script>

<style scoped>
.admin-panel {
	min-height: 100vh;
	background-color: transparent;
	padding: 44px 16px 24px 16px;
	overflow-y: auto;
	-webkit-overflow-scrolling: touch;
}

.header-card {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	padding: 20px;
	border-radius: 14px;
	margin-bottom: 16px;
	border: 1px solid rgba(255, 255, 255, 0.14);
	box-shadow: 0 16px 32px rgba(0, 0, 0, 0.35);
	color: #ffffff;
}

.header-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 8px;
}

.welcome-text {
	font-size: 12px;
	color: #ffffff;
	display: block;
	margin-bottom: 4px;
}

.username {
	font-size: 20px;
	font-weight: 600;
	color: #ffffff;
}

.avatar-circle {
	width: 40px;
	height: 40px;
	background-color: rgba(255, 255, 255, 0.22);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	color: #ffffff;
	font-weight: 600;
	overflow: hidden;
}

.avatar-img {
	width: 100%;
	height: 100%;
}

.role-badge {
	display: inline-block;
	background-color: rgba(255, 255, 255, 0.16);
	padding: 6px 10px;
	border-radius: 999px;
	border: 1px solid rgba(255, 255, 255, 0.24);
}

.role-text {
	font-size: 12px;
	color: #ffffff;
	font-weight: 600;
}

.dashboard-grid {
	display: flex;
	justify-content: space-between;
	gap: 12px;
	margin-bottom: 24px;
}

.stat-box {
	flex: 1;
	background-color: var(--card);
	padding: 16px;
	border-radius: 12px;
	border: 1px solid var(--border);
	box-shadow: var(--shadow-plain);
}

.stat-label {
	font-size: 12px;
	color: var(--brand-muted);
	display: block;
	margin-bottom: 8px;
}

.stat-value {
	font-size: 20px;
	font-weight: 600;
	color: var(--brand-ink);
	font-family: monospace;
	display: block;
	margin-bottom: 8px;
}

.trend-row {
	display: flex;
	align-items: center;
	font-size: 12px;
}

.trend-row.up { color: #2BA471; }
.trend-row.down { color: #D54941; }

.trend-arrow { margin-right: 2px; }
.trend-val { margin-right: 4px; font-weight: 500; }
.trend-desc { color: var(--brand-muted); }

.menu-section {
	margin-bottom: 24px;
}

.section-title {
	font-size: 12px;
	color: var(--brand-muted);
	font-weight: 600;
	margin-bottom: 8px;
	padding-left: 4px;
}

.menu-list {
	background-color: var(--card);
	border: 1px solid var(--border);
	border-radius: 12px;
	box-shadow: var(--shadow-plain);
}

.menu-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 16px;
	border-bottom: 1px solid var(--border);
}

.menu-row:last-child {
	border-bottom: none;
}

.menu-row:active {
	background-color: rgba(255, 255, 255, 0.04);
}

.menu-name {
	font-size: 14px;
	color: var(--brand-ink);
}

.menu-status {
	font-size: 12px;
}
.menu-status.normal { color: #06AD56; }

.menu-arrow, .menu-desc {
	font-size: 12px;
	color: var(--brand-muted);
}

.switch-text {
	font-size: 12px;
	font-weight: 600;
	color: var(--brand-muted);
}

.switch-text.on {
	color: #06AD56;
}

.setting-card {
	background-color: var(--card);
	border: 1px solid var(--border);
	border-radius: 12px;
	padding: 14px;
	box-shadow: var(--shadow-plain);
}

.setting-label {
	font-size: 14px;
	color: var(--brand-ink);
	font-weight: 600;
	display: block;
	margin-bottom: 8px;
}

.setting-input {
	width: 100%;
	height: 40px;
	border-radius: 10px;
	border: 1px solid var(--border);
	padding: 0 12px;
	font-size: 14px;
	color: var(--brand-ink);
	background-color: #f8fafc;
	margin-bottom: 10px;
}

.setting-actions {
	display: flex;
	gap: 10px;
	margin-bottom: 8px;
}

.setting-btn {
	flex: 1;
	text-align: center;
	padding: 10px 0;
	border-radius: 10px;
	border: 1px solid var(--border);
	color: var(--brand-ink);
	background-color: #f5f7fa;
	font-size: 14px;
}

.setting-btn.primary {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	color: #ffffff;
	border: none;
	box-shadow: 0 10px 24px rgba(16, 240, 194, 0.25);
}

.setting-tip {
	font-size: 12px;
	color: var(--brand-muted);
}

.logout-area {
	text-align: center;
	padding: 16px;
	border-radius: 12px;
	border: 1px solid var(--border);
	background-color: var(--card);
	box-shadow: var(--shadow-plain);
}

.logout-text {
	font-size: 14px;
	color: #D54941;
}
</style>
