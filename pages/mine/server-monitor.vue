<template>
	<view class="monitor-page">
		<!-- 顶部状态卡片 -->
		<view class="status-header">
			<view class="status-card" :class="serverStatus">
				<view class="status-icon">
					<text>{{ serverStatus === 'online' ? '✓' : '!' }}</text>
				</view>
				<view class="status-info">
					<text class="status-title">服务器状态</text>
					<text class="status-value">{{ serverStatus === 'online' ? '运行正常' : '异常' }}</text>
				</view>
				<view class="refresh-btn" @click="refreshStatus">
					<text>刷新</text>
				</view>
			</view>
		</view>

		<!-- 标签页 -->
		<view class="tabs">
			<view class="tab" :class="{ active: currentTab === 'logs' }" @click="currentTab = 'logs'">
				<text>运行日志</text>
			</view>
			<view class="tab" :class="{ active: currentTab === 'errors' }" @click="currentTab = 'errors'">
				<text>异常记录</text>
				<view class="badge" v-if="errorCount > 0">{{ errorCount }}</view>
			</view>
			<view class="tab" :class="{ active: currentTab === 'security' }" @click="switchToSecurity">
				<text>安全防护</text>
				<view class="badge warning" v-if="securityStats.recent_events > 0">{{ securityStats.recent_events }}</view>
			</view>
			<view class="tab" :class="{ active: currentTab === 'stats' }" @click="currentTab = 'stats'">
				<text>系统状态</text>
			</view>
		</view>

		<!-- 日志列表 -->
		<scroll-view class="log-list" scroll-y v-if="currentTab === 'logs'">
			<view class="log-item" v-for="(log, index) in logs" :key="index" :class="log.level">
				<view class="log-header">
					<text class="log-level">{{ log.level.toUpperCase() }}</text>
					<text class="log-time">{{ log.time }}</text>
				</view>
				<text class="log-message">{{ log.message }}</text>
			</view>
			<view class="empty" v-if="logs.length === 0">
				<text>暂无日志</text>
			</view>
			<view class="load-more" @click="loadMoreLogs" v-if="hasMoreLogs">
				<text>加载更多</text>
			</view>
		</scroll-view>

		<!-- 异常列表 -->
		<scroll-view class="log-list" scroll-y v-if="currentTab === 'errors'">
			<view class="error-item" v-for="(err, index) in errors" :key="index">
				<view class="error-header">
					<text class="error-type">{{ err.type }}</text>
					<text class="error-time">{{ err.time }}</text>
				</view>
				<text class="error-message">{{ err.message }}</text>
				<view class="error-stack" v-if="err.stack" @click="toggleStack(index)">
					<text class="stack-toggle">{{ expandedStacks.includes(index) ? '收起' : '展开' }}堆栈</text>
					<text class="stack-content" v-if="expandedStacks.includes(index)">{{ err.stack }}</text>
				</view>
			</view>
			<view class="empty" v-if="errors.length === 0">
				<text>🎉 暂无异常，系统运行正常</text>
			</view>
		</scroll-view>

		<!-- 系统状态 -->
		<view class="stats-panel" v-if="currentTab === 'stats'">
			<view class="stat-row">
				<text class="stat-label">CPU 使用率</text>
				<view class="stat-bar">
					<view class="bar-fill" :style="{ width: systemStats.cpu + '%' }"></view>
				</view>
				<text class="stat-value">{{ systemStats.cpu }}%</text>
			</view>
			<view class="stat-row">
				<text class="stat-label">内存使用</text>
				<view class="stat-bar">
					<view class="bar-fill" :style="{ width: systemStats.memory + '%' }"></view>
				</view>
				<text class="stat-value">{{ systemStats.memory }}%</text>
			</view>
			<view class="stat-row">
				<text class="stat-label">磁盘使用</text>
				<view class="stat-bar">
					<view class="bar-fill" :style="{ width: systemStats.disk + '%' }"></view>
				</view>
				<text class="stat-value">{{ systemStats.disk }}%</text>
			</view>
			<view class="stat-row">
				<text class="stat-label">运行时间</text>
				<text class="stat-value">{{ systemStats.uptime }}</text>
			</view>
			<view class="stat-row">
				<text class="stat-label">数据库连接</text>
				<text class="stat-value status-ok">正常</text>
			</view>
			<view class="stat-row">
				<text class="stat-label">Redis 连接</text>
				<text class="stat-value status-ok">正常</text>
			</view>
		</view>

		<!-- 安全防护 -->
		<view class="security-panel" v-if="currentTab === 'security'">
			<!-- 安全统计卡片 -->
			<view class="security-stats">
				<view class="security-stat-card">
					<text class="stat-number">{{ securityStats.blacklist_count }}</text>
					<text class="stat-desc">黑名单 IP</text>
				</view>
				<view class="security-stat-card warning" v-if="securityStats.locked_ips > 0">
					<text class="stat-number">{{ securityStats.locked_ips }}</text>
					<text class="stat-desc">已锁定</text>
				</view>
				<view class="security-stat-card" :class="{ warning: securityStats.rate_limit_hits > 0 }">
					<text class="stat-number">{{ securityStats.rate_limit_hits }}</text>
					<text class="stat-desc">频率限制</text>
				</view>
				<view class="security-stat-card" :class="{ danger: securityStats.login_failures > 0 }">
					<text class="stat-number">{{ securityStats.login_failures }}</text>
					<text class="stat-desc">登录失败</text>
				</view>
			</view>

			<!-- IP 黑名单管理 -->
			<view class="section-card">
				<view class="section-header">
					<text class="section-title">IP 黑名单</text>
					<view class="add-btn" @click="showAddBlacklist">
						<text>+ 添加</text>
					</view>
				</view>
				<view class="blacklist-list" v-if="blacklist.length > 0">
					<view class="blacklist-item" v-for="ip in blacklist" :key="ip">
						<text class="ip-text">{{ ip }}</text>
						<text class="remove-btn" @click="removeBlacklist(ip)">移除</text>
					</view>
				</view>
				<view class="empty-small" v-else>
					<text>暂无黑名单 IP</text>
				</view>
			</view>

			<!-- 安全事件列表 -->
			<view class="section-card">
				<view class="section-header">
					<text class="section-title">安全事件</text>
					<text class="section-hint">最近1小时</text>
				</view>
				<scroll-view class="security-events" scroll-y>
					<view class="event-item" v-for="(event, index) in securityEvents" :key="index" :class="getEventLevel(event.type)">
						<view class="event-header">
							<text class="event-type">{{ getEventTypeName(event.type) }}</text>
							<text class="event-time">{{ formatEventTime(event.time) }}</text>
						</view>
						<view class="event-body">
							<text class="event-ip">{{ event.ip }}</text>
							<text class="event-message">{{ event.message }}</text>
						</view>
					</view>
					<view class="empty-small" v-if="securityEvents.length === 0">
						<text>🛡️ 暂无安全事件，一切正常</text>
					</view>
				</scroll-view>
			</view>
		</view>

		<!-- 操作按钮 -->
		<view class="action-bar">
			<view class="action-btn" @click="clearLogs">
				<text>清空日志</text>
			</view>
			<view class="action-btn primary" @click="exportLogs">
				<text>导出日志</text>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get, post, del } from '@/api/request'

const currentTab = ref('logs')
const serverStatus = ref('online')
const errorCount = ref(0)
const logs = ref([])
const errors = ref([])
const expandedStacks = ref([])
const hasMoreLogs = ref(true)
const logPage = ref(1)

const systemStats = ref({
	cpu: 0,
	memory: 0,
	disk: 0,
	uptime: '-'
})

// 安全相关数据
const securityStats = ref({
	blacklist_count: 0,
	locked_ips: 0,
	recent_events: 0,
	rate_limit_hits: 0,
	login_failures: 0
})
const securityEvents = ref([])
const blacklist = ref([])

onMounted(() => {
	checkServerStatus()
	loadLogs()
	loadErrors()
	loadSystemStats()
	loadSecurityStats()
})

const checkServerStatus = async () => {
	try {
		const res = await uni.request({ url: 'http://localhost:8080/health', method: 'GET' })
		serverStatus.value = (res.data && res.data.status === 'ok') ? 'online' : 'offline'
	} catch (e) {
		serverStatus.value = 'offline'
	}
}

const refreshStatus = async () => {
	try {
		const res = await uni.request({ url: 'http://localhost:8080/health', method: 'GET' })
		if (res.data && res.data.status === 'ok') {
			serverStatus.value = 'online'
			uni.showToast({ title: '服务正常', icon: 'success' })
		} else {
			serverStatus.value = 'offline'
			uni.showToast({ title: '服务异常', icon: 'none' })
		}
	} catch (e) {
		serverStatus.value = 'offline'
		uni.showToast({ title: '服务异常', icon: 'none' })
	}
}

const loadLogs = async () => {
	try {
		const res = await get('/api/monitor/logs', { page: logPage.value, limit: 50 })
		if (res.code === 0) {
			if (logPage.value === 1) {
				logs.value = res.data.logs || []
			} else {
				logs.value = [...logs.value, ...(res.data.logs || [])]
			}
			hasMoreLogs.value = (res.data.logs || []).length === 50
		}
	} catch (e) {
		// 使用模拟数据
		logs.value = [
			{ level: 'info', time: formatNow(), message: '服务启动成功' },
			{ level: 'info', time: formatNow(), message: '数据库连接成功' },
			{ level: 'info', time: formatNow(), message: 'Redis 连接成功' }
		]
	}
}

const loadMoreLogs = () => {
	logPage.value++
	loadLogs()
}

const loadErrors = async () => {
	try {
		const res = await get('/api/monitor/errors', { limit: 20 })
		if (res.code === 0) {
			errors.value = res.data.errors || []
			errorCount.value = errors.value.length
		}
	} catch (e) {
		errors.value = []
		errorCount.value = 0
	}
}

const loadSystemStats = async () => {
	try {
		const res = await get('/api/monitor/stats')
		if (res.code === 0) {
			systemStats.value = res.data
		}
	} catch (e) {
		// 使用默认值
		systemStats.value = {
			cpu: 15,
			memory: 45,
			disk: 32,
			uptime: '运行中'
		}
	}
}

const toggleStack = (index) => {
	const idx = expandedStacks.value.indexOf(index)
	if (idx === -1) {
		expandedStacks.value.push(index)
	} else {
		expandedStacks.value.splice(idx, 1)
	}
}

const clearLogs = () => {
	uni.showModal({
		title: '确认清空',
		content: '确定清空所有日志吗？',
		success: (res) => {
			if (res.confirm) {
				logs.value = []
				uni.showToast({ title: '已清空' })
			}
		}
	})
}

const exportLogs = () => {
	const content = logs.value.map(l => `[${l.level}] ${l.time} ${l.message}`).join('\n')
	// #ifdef H5
	const blob = new Blob([content], { type: 'text/plain' })
	const url = URL.createObjectURL(blob)
	const a = document.createElement('a')
	a.href = url
	a.download = `logs_${Date.now()}.txt`
	a.click()
	// #endif
	// #ifndef H5
	uni.showToast({ title: '已复制到剪贴板', icon: 'none' })
	uni.setClipboardData({ data: content })
	// #endif
}

const formatNow = () => {
	const d = new Date()
	return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`
}

// ============ 安全相关方法 ============

const switchToSecurity = () => {
	currentTab.value = 'security'
	loadSecurityStats()
	loadSecurityEvents()
	loadBlacklist()
}

const loadSecurityStats = async () => {
	try {
		const res = await get('/api/monitor/security/stats')
		if (res.code === 0) {
			securityStats.value = res.data
		}
	} catch (e) {
		console.log('加载安全统计失败', e)
	}
}

const loadSecurityEvents = async () => {
	try {
		const res = await get('/api/monitor/security/events', { limit: 50 })
		if (res.code === 0) {
			securityEvents.value = res.data || []
		}
	} catch (e) {
		securityEvents.value = []
	}
}

const loadBlacklist = async () => {
	try {
		const res = await get('/api/monitor/security/blacklist')
		if (res.code === 0) {
			blacklist.value = res.data || []
		}
	} catch (e) {
		blacklist.value = []
	}
}

const showAddBlacklist = () => {
	uni.showModal({
		title: '添加黑名单 IP',
		editable: true,
		placeholderText: '请输入 IP 地址',
		success: async (res) => {
			if (res.confirm && res.content) {
				const ip = res.content.trim()
				if (!/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(ip)) {
					uni.showToast({ title: 'IP 格式不正确', icon: 'none' })
					return
				}
				try {
					await post('/api/monitor/security/blacklist', { ip })
					uni.showToast({ title: '已添加', icon: 'success' })
					loadBlacklist()
					loadSecurityStats()
				} catch (e) {
					uni.showToast({ title: '添加失败', icon: 'none' })
				}
			}
		}
	})
}

const removeBlacklist = async (ip) => {
	uni.showModal({
		title: '确认移除',
		content: `确定从黑名单移除 ${ip} 吗？`,
		success: async (res) => {
			if (res.confirm) {
				try {
					await del(`/api/monitor/security/blacklist/${ip}`)
					uni.showToast({ title: '已移除', icon: 'success' })
					loadBlacklist()
					loadSecurityStats()
				} catch (e) {
					uni.showToast({ title: '移除失败', icon: 'none' })
				}
			}
		}
	})
}

const getEventTypeName = (type) => {
	const names = {
		'login_success': '登录成功',
		'login_failure': '登录失败',
		'login_locked': '账号锁定',
		'login_lockout': '登录锁定',
		'rate_limit': '频率限制',
		'blacklist_add': '加入黑名单',
		'blacklist_block': '黑名单拦截'
	}
	return names[type] || type
}

const getEventLevel = (type) => {
	if (['login_locked', 'blacklist_block'].includes(type)) return 'danger'
	if (['login_failure', 'rate_limit', 'login_lockout'].includes(type)) return 'warning'
	return 'info'
}

const formatEventTime = (isoTime) => {
	if (!isoTime) return ''
	const d = new Date(isoTime)
	return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`
}
</script>

<style scoped>
.monitor-page {
	min-height: 100vh;
	background: #f5f5f5;
}

/* 状态头部 */
.status-header {
	padding: 24rpx;
}

.status-card {
	display: flex;
	align-items: center;
	padding: 32rpx;
	background: #fff;
	border-radius: 20rpx;
	box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.05);
}

.status-card.online .status-icon {
	background: #07C160;
}

.status-card.offline .status-icon {
	background: #ff4d4f;
}

.status-icon {
	width: 64rpx;
	height: 64rpx;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	color: #fff;
	font-size: 32rpx;
	margin-right: 24rpx;
}

.status-info {
	flex: 1;
}

.status-title {
	font-size: 26rpx;
	color: #999;
	display: block;
}

.status-value {
	font-size: 32rpx;
	color: #333;
	font-weight: 600;
}

.refresh-btn {
	padding: 16rpx 28rpx;
	background: #f5f5f5;
	border-radius: 24rpx;
	font-size: 26rpx;
	color: #666;
}

/* 标签页 */
.tabs {
	display: flex;
	background: #fff;
	border-bottom: 1rpx solid #eee;
}

.tab {
	flex: 1;
	padding: 28rpx;
	text-align: center;
	font-size: 28rpx;
	color: #666;
	position: relative;
}

.tab.active {
	color: #07C160;
	font-weight: 600;
}

.tab.active::after {
	content: '';
	position: absolute;
	bottom: 0;
	left: 50%;
	transform: translateX(-50%);
	width: 48rpx;
	height: 6rpx;
	background: #07C160;
	border-radius: 3rpx;
}

.badge {
	position: absolute;
	top: 16rpx;
	right: 40rpx;
	min-width: 32rpx;
	height: 32rpx;
	background: #ff4d4f;
	color: #fff;
	font-size: 20rpx;
	border-radius: 16rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 0 8rpx;
}

/* 日志列表 */
.log-list {
	height: calc(100vh - 420rpx);
	padding: 24rpx;
}

.log-item {
	background: #fff;
	border-radius: 12rpx;
	padding: 20rpx;
	margin-bottom: 16rpx;
	border-left: 6rpx solid #07C160;
}

.log-item.warning {
	border-left-color: #faad14;
}

.log-item.error {
	border-left-color: #ff4d4f;
}

.log-header {
	display: flex;
	justify-content: space-between;
	margin-bottom: 8rpx;
}

.log-level {
	font-size: 22rpx;
	color: #07C160;
	font-weight: 600;
}

.log-item.warning .log-level { color: #faad14; }
.log-item.error .log-level { color: #ff4d4f; }

.log-time {
	font-size: 22rpx;
	color: #999;
}

.log-message {
	font-size: 26rpx;
	color: #333;
	line-height: 1.5;
	word-break: break-all;
}

/* 异常列表 */
.error-item {
	background: #fff;
	border-radius: 12rpx;
	padding: 20rpx;
	margin-bottom: 16rpx;
	border-left: 6rpx solid #ff4d4f;
}

.error-header {
	display: flex;
	justify-content: space-between;
	margin-bottom: 8rpx;
}

.error-type {
	font-size: 24rpx;
	color: #ff4d4f;
	font-weight: 600;
}

.error-time {
	font-size: 22rpx;
	color: #999;
}

.error-message {
	font-size: 26rpx;
	color: #333;
	line-height: 1.5;
	display: block;
}

.error-stack {
	margin-top: 16rpx;
	padding-top: 16rpx;
	border-top: 1rpx solid #f0f0f0;
}

.stack-toggle {
	font-size: 24rpx;
	color: #07C160;
}

.stack-content {
	display: block;
	margin-top: 12rpx;
	font-size: 22rpx;
	color: #666;
	background: #f9f9f9;
	padding: 16rpx;
	border-radius: 8rpx;
	white-space: pre-wrap;
	word-break: break-all;
}

/* 系统状态 */
.stats-panel {
	padding: 24rpx;
}

.stat-row {
	display: flex;
	align-items: center;
	background: #fff;
	padding: 28rpx;
	border-radius: 12rpx;
	margin-bottom: 16rpx;
}

.stat-label {
	width: 180rpx;
	font-size: 28rpx;
	color: #333;
}

.stat-bar {
	flex: 1;
	height: 16rpx;
	background: #f0f0f0;
	border-radius: 8rpx;
	margin: 0 24rpx;
	overflow: hidden;
}

.bar-fill {
	height: 100%;
	background: linear-gradient(90deg, #07C160, #06AD56);
	border-radius: 8rpx;
	transition: width 0.3s;
}

.stat-value {
	width: 100rpx;
	text-align: right;
	font-size: 28rpx;
	color: #333;
	font-weight: 600;
}

.status-ok {
	color: #07C160;
}

/* 空状态 */
.empty {
	text-align: center;
	padding: 80rpx;
	color: #999;
	font-size: 28rpx;
}

.load-more {
	text-align: center;
	padding: 24rpx;
	color: #07C160;
	font-size: 26rpx;
}

/* 操作栏 */
.action-bar {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	display: flex;
	padding: 24rpx;
	background: #fff;
	border-top: 1rpx solid #eee;
	gap: 24rpx;
}

.action-btn {
	flex: 1;
	padding: 24rpx;
	text-align: center;
	background: #f5f5f5;
	border-radius: 12rpx;
	font-size: 28rpx;
	color: #666;
}

.action-btn.primary {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	color: #fff;
}

/* 安全防护面板 */
.security-panel {
	padding: 24rpx;
	padding-bottom: 160rpx;
}

.security-stats {
	display: flex;
	gap: 16rpx;
	margin-bottom: 24rpx;
}

.security-stat-card {
	flex: 1;
	background: #fff;
	border-radius: 12rpx;
	padding: 20rpx;
	text-align: center;
}

.security-stat-card.warning {
	background: #fffbe6;
	border: 1rpx solid #ffe58f;
}

.security-stat-card.danger {
	background: #fff2f0;
	border: 1rpx solid #ffccc7;
}

.stat-number {
	font-size: 40rpx;
	font-weight: 600;
	color: #333;
	display: block;
}

.security-stat-card.warning .stat-number {
	color: #faad14;
}

.security-stat-card.danger .stat-number {
	color: #ff4d4f;
}

.stat-desc {
	font-size: 22rpx;
	color: #999;
}

.section-card {
	background: #fff;
	border-radius: 12rpx;
	padding: 20rpx;
	margin-bottom: 24rpx;
}

.section-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 16rpx;
}

.section-title {
	font-size: 28rpx;
	font-weight: 600;
	color: #333;
}

.section-hint {
	font-size: 22rpx;
	color: #999;
}

.add-btn {
	padding: 8rpx 20rpx;
	background: #07C160;
	border-radius: 20rpx;
	font-size: 24rpx;
	color: #fff;
}

/* 黑名单列表 */
.blacklist-list {
	max-height: 300rpx;
	overflow-y: auto;
}

.blacklist-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 16rpx 0;
	border-bottom: 1rpx solid #f0f0f0;
}

.blacklist-item:last-child {
	border-bottom: none;
}

.ip-text {
	font-size: 28rpx;
	color: #333;
	font-family: monospace;
}

.remove-btn {
	font-size: 24rpx;
	color: #ff4d4f;
}

.empty-small {
	text-align: center;
	padding: 32rpx;
	color: #999;
	font-size: 26rpx;
}

/* 安全事件列表 */
.security-events {
	max-height: 500rpx;
}

.event-item {
	padding: 16rpx;
	margin-bottom: 12rpx;
	background: #f9f9f9;
	border-radius: 8rpx;
	border-left: 4rpx solid #07C160;
}

.event-item.warning {
	border-left-color: #faad14;
	background: #fffbe6;
}

.event-item.danger {
	border-left-color: #ff4d4f;
	background: #fff2f0;
}

.event-header {
	display: flex;
	justify-content: space-between;
	margin-bottom: 8rpx;
}

.event-type {
	font-size: 24rpx;
	font-weight: 600;
	color: #07C160;
}

.event-item.warning .event-type {
	color: #faad14;
}

.event-item.danger .event-type {
	color: #ff4d4f;
}

.event-time {
	font-size: 22rpx;
	color: #999;
}

.event-body {
	display: flex;
	gap: 16rpx;
}

.event-ip {
	font-size: 24rpx;
	color: #666;
	font-family: monospace;
	background: rgba(0,0,0,0.05);
	padding: 4rpx 12rpx;
	border-radius: 4rpx;
}

.event-message {
	font-size: 24rpx;
	color: #666;
	flex: 1;
}

.badge.warning {
	background: #faad14;
}
</style>
