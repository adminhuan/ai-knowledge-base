<template>
	<view class="files-page" :style="pageStyle">
		<!-- 顶部标题 -->
		<view class="page-header">
			<text class="page-title">云端文件</text>
			<text class="file-count">共 {{ totalCount }} 个文件</text>
		</view>
		
		<!-- 分类标签 -->
		<view class="type-tabs">
			<view 
				class="type-tab" 
				:class="{ active: currentType === 'all' }"
				@click="changeType('all')"
			>
				<text class="tab-text">全部</text>
			</view>
			<view 
				class="type-tab" 
				:class="{ active: currentType === 'image' }"
				@click="changeType('image')"
			>
				<Icon name="image" size="16" />
				<text class="tab-text">图片</text>
			</view>
			<view 
				class="type-tab" 
				:class="{ active: currentType === 'document' }"
				@click="changeType('document')"
			>
				<Icon name="file" size="16" />
				<text class="tab-text">文档</text>
			</view>
		</view>
		
		<!-- 文件列表 -->
		<scroll-view class="files-list" scroll-y @scrolltolower="loadMore">
			<!-- 图片类型：网格布局 -->
			<view class="image-grid" v-if="currentType === 'image' || (currentType === 'all' && imageFiles.length > 0)">
				<view class="grid-header" v-if="currentType === 'all'">
					<text class="grid-title">图片 ({{ imageFiles.length }})</text>
				</view>
				<view class="grid-content">
					<view 
						class="image-item" 
						v-for="file in (currentType === 'all' ? imageFiles : files)" 
						:key="file.id"
						@click="previewImage(file)"
						@longpress="showFileActions(file)"
					>
						<image class="image-thumb" :src="file.url" mode="aspectFill" />
						<view class="image-overlay">
							<text class="image-name">{{ file.filename }}</text>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 文档类型：列表布局 -->
			<view class="doc-list" v-if="currentType === 'document' || (currentType === 'all' && docFiles.length > 0)">
				<view class="list-header" v-if="currentType === 'all'">
					<text class="list-title">文档 ({{ docFiles.length }})</text>
				</view>
				<view 
					class="doc-item" 
					v-for="file in (currentType === 'all' ? docFiles : files)" 
					:key="file.id"
					@click="showFileDetail(file)"
					@longpress="showFileActions(file)"
				>
					<view class="doc-icon" :class="getFileTypeClass(file.filename)">
						<text class="doc-ext">{{ getFileExt(file.filename) }}</text>
					</view>
					<view class="doc-info">
						<text class="doc-name">{{ file.filename }}</text>
						<view class="doc-meta">
							<text class="doc-size">{{ formatSize(file.file_size) }}</text>
							<text class="doc-time">{{ formatTime(file.created_at) }}</text>
						</view>
					</view>
					<view class="doc-actions">
						<view class="action-btn download" @click.stop="downloadFile(file)">
							<Icon name="download" size="18" />
						</view>
						<view class="action-btn delete" @click.stop="confirmDelete(file)">
							<Icon name="trash" size="18" />
						</view>
					</view>
				</view>
			</view>
			
			<!-- 空状态 -->
			<view class="empty-state" v-if="files.length === 0 && !loading">
				<Icon name="cloud" size="64" class="empty-icon" />
				<text class="empty-text">暂无{{ currentType === 'image' ? '图片' : currentType === 'document' ? '文档' : '文件' }}</text>
				<text class="empty-tip">在聊天中上传文件后点击"上传云端"即可保存</text>
			</view>
			
			<!-- 加载中 -->
			<view class="loading-more" v-if="loading">
				<text class="loading-text">加载中...</text>
			</view>
			
			<view class="bottom-spacer"></view>
		</scroll-view>
		
		<!-- 图片预览弹窗 -->
		<view class="preview-modal" v-if="previewFile" @click="previewFile = null">
			<view class="preview-content" @click.stop>
				<image class="preview-image" :src="previewFile.url" mode="aspectFit" />
				<view class="preview-info">
					<text class="preview-name">{{ previewFile.filename }}</text>
					<text class="preview-meta">{{ formatSize(previewFile.file_size) }} · {{ formatTime(previewFile.created_at) }}</text>
				</view>
				<view class="preview-actions">
					<view class="preview-btn" @click="downloadFile(previewFile)">
						<Icon name="download" size="20" />
						<text>下载</text>
					</view>
					<view class="preview-btn delete" @click="confirmDelete(previewFile)">
						<Icon name="trash" size="20" />
						<text>删除</text>
					</view>
				</view>
			</view>
			<view class="preview-close" @click="previewFile = null">
				<Icon name="close" size="24" />
			</view>
		</view>
		
		<CustomTabBar :currentTab="2" />
	</view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import Icon from '@/components/Icon.vue'
import CustomTabBar from '@/components/CustomTabBar.vue'
import { getBackgroundStyle, applyGlobalBackground } from '@/utils/theme'
import { get, del } from '@/api/request'

const pageStyle = ref(getBackgroundStyle())
const files = ref([])
const currentType = ref('all')
const loading = ref(false)
const page = ref(1)
const hasMore = ref(true)
const previewFile = ref(null)
const totalCount = ref(0)

// 按类型筛选
const imageFiles = computed(() => files.value.filter(f => f.file_type === 'image'))
const docFiles = computed(() => files.value.filter(f => f.file_type !== 'image'))

onMounted(() => {
	loadFiles()
	applyGlobalBackground()
})

onShow(() => {
	pageStyle.value = getBackgroundStyle()
	// 刷新列表
	page.value = 1
	files.value = []
	loadFiles()
	applyGlobalBackground()
})

const loadFiles = async () => {
	if (loading.value) return
	loading.value = true
	
	try {
		const params = { page: page.value, page_size: 20 }
		if (currentType.value !== 'all') {
			params.file_type = currentType.value
		}
		
		const res = await get('/api/upload/files', params)
		if (res.code === 0) {
			const list = res.data.list || []
			if (page.value === 1) {
				files.value = list
			} else {
				files.value = [...files.value, ...list]
			}
			hasMore.value = list.length === 20
			totalCount.value = files.value.length
		}
	} catch (e) {
		uni.showToast({ title: '加载失败', icon: 'none' })
	} finally {
		loading.value = false
	}
}

const loadMore = () => {
	if (hasMore.value && !loading.value) {
		page.value++
		loadFiles()
	}
}

const changeType = (type) => {
	if (currentType.value === type) return
	currentType.value = type
	page.value = 1
	files.value = []
	loadFiles()
}

const previewImage = (file) => {
	if (file.file_type === 'image') {
		previewFile.value = file
	}
}

const showFileDetail = (file) => {
	uni.showActionSheet({
		itemList: ['在线预览', '下载文件', '删除'],
		success: (res) => {
			if (res.tapIndex === 0) {
				previewDocument(file)
			} else if (res.tapIndex === 1) {
				downloadFile(file)
			} else if (res.tapIndex === 2) {
				confirmDelete(file)
			}
		}
	})
}

// 在线预览文档
const previewDocument = (file) => {
	const ext = file.filename.split('.').pop().toLowerCase()
	const url = encodeURIComponent(file.url)
	
	let previewUrl = ''
	
	if (ext === 'pdf') {
		// PDF 直接打开
		previewUrl = file.url
	} else if (['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'].includes(ext)) {
		// Office 文件用微软在线预览
		previewUrl = `https://view.officeapps.live.com/op/view.aspx?src=${url}`
	} else {
		uni.showToast({ title: '该文件类型暂不支持预览', icon: 'none' })
		return
	}
	
	// #ifdef H5
	window.open(previewUrl, '_blank')
	// #endif
	
	// #ifndef H5
	uni.navigateTo({
		url: `/pages/webview/index?url=${encodeURIComponent(previewUrl)}&title=${encodeURIComponent(file.filename)}`
	})
	// #endif
}

const showFileActions = (file) => {
	uni.showActionSheet({
		itemList: ['下载', '删除'],
		success: (res) => {
			if (res.tapIndex === 0) {
				downloadFile(file)
			} else if (res.tapIndex === 1) {
				confirmDelete(file)
			}
		}
	})
}

const downloadFile = (file) => {
	// #ifdef H5
	// H5 直接打开新窗口下载
	window.open(file.url, '_blank')
	// #endif
	
	// #ifndef H5
	// 小程序下载
	uni.showLoading({ title: '下载中...' })
	uni.downloadFile({
		url: file.url,
		success: (res) => {
			if (res.statusCode === 200) {
				if (file.file_type === 'image') {
					uni.saveImageToPhotosAlbum({
						filePath: res.tempFilePath,
						success: () => {
							uni.showToast({ title: '已保存到相册' })
						},
						fail: () => {
							uni.showToast({ title: '保存失败', icon: 'none' })
						}
					})
				} else {
					uni.openDocument({
						filePath: res.tempFilePath,
						showMenu: true,
						success: () => {
							uni.hideLoading()
						},
						fail: () => {
							uni.showToast({ title: '打开失败', icon: 'none' })
						}
					})
				}
			}
		},
		fail: () => {
			uni.showToast({ title: '下载失败', icon: 'none' })
		},
		complete: () => {
			uni.hideLoading()
		}
	})
	// #endif
}

const confirmDelete = (file) => {
	previewFile.value = null
	uni.showModal({
		title: '确认删除',
		content: `确定删除 "${file.filename}" 吗？删除后无法恢复。`,
		confirmColor: '#ff4d4f',
		success: async (res) => {
			if (res.confirm) {
				try {
					const result = await del(`/api/upload/files/${file.id}`)
					if (result.code === 0) {
						files.value = files.value.filter(f => f.id !== file.id)
						totalCount.value = files.value.length
						uni.showToast({ title: '已删除' })
					} else {
						uni.showToast({ title: result.message || '删除失败', icon: 'none' })
					}
				} catch (e) {
					uni.showToast({ title: '删除失败', icon: 'none' })
				}
			}
		}
	})
}

const formatSize = (bytes) => {
	if (!bytes) return '0 B'
	const units = ['B', 'KB', 'MB', 'GB']
	let i = 0
	while (bytes >= 1024 && i < units.length - 1) {
		bytes /= 1024
		i++
	}
	return bytes.toFixed(i > 0 ? 1 : 0) + ' ' + units[i]
}

const formatTime = (dateStr) => {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	const now = new Date()
	const diff = now - date
	
	if (diff < 60000) return '刚刚'
	if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
	if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
	if (diff < 604800000) return Math.floor(diff / 86400000) + '天前'
	
	return `${date.getMonth() + 1}/${date.getDate()}`
}

const getFileExt = (filename) => {
	const ext = filename.split('.').pop().toUpperCase()
	return ext.length > 4 ? ext.substring(0, 4) : ext
}

const getFileTypeClass = (filename) => {
	const ext = filename.split('.').pop().toLowerCase()
	if (['pdf'].includes(ext)) return 'pdf'
	if (['doc', 'docx'].includes(ext)) return 'word'
	if (['xls', 'xlsx'].includes(ext)) return 'excel'
	if (['ppt', 'pptx'].includes(ext)) return 'ppt'
	return 'other'
}
</script>

<style scoped>
.files-page {
	min-height: 100vh;
	background-color: #f5f5f5;
	padding-bottom: 120rpx;
}

.page-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 32rpx;
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
}

.page-title {
	font-size: 36rpx;
	color: #fff;
	font-weight: 600;
}

.file-count {
	font-size: 26rpx;
	color: rgba(255, 255, 255, 0.8);
}

.type-tabs {
	display: flex;
	padding: 20rpx 24rpx;
	gap: 20rpx;
	background: #fff;
}

.type-tab {
	display: flex;
	align-items: center;
	gap: 8rpx;
	padding: 16rpx 32rpx;
	background: #f5f5f5;
	border-radius: 32rpx;
	color: #666;
}

.type-tab.active {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	color: #fff;
}

.tab-text {
	font-size: 26rpx;
}

.files-list {
	height: calc(100vh - 280rpx);
}

/* 图片网格 */
.image-grid {
	padding: 24rpx;
}

.grid-header, .list-header {
	margin-bottom: 20rpx;
}

.grid-title, .list-title {
	font-size: 28rpx;
	color: #333;
	font-weight: 500;
}

.grid-content {
	display: flex;
	flex-wrap: wrap;
	gap: 16rpx;
}

.image-item {
	width: 216rpx;
	height: 216rpx;
	border-radius: 12rpx;
	overflow: hidden;
	position: relative;
	background: #f0f0f0;
}

.image-thumb {
	width: 216rpx;
	height: 216rpx;
}

.image-overlay {
	position: absolute;
	bottom: 0;
	left: 0;
	right: 0;
	padding: 12rpx;
	background: linear-gradient(transparent, rgba(0,0,0,0.6));
}

.image-name {
	font-size: 20rpx;
	color: #fff;
	display: block;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

/* 文档列表 */
.doc-list {
	padding: 24rpx;
}

.doc-item {
	display: flex;
	align-items: center;
	padding: 24rpx;
	background: #fff;
	border-radius: 16rpx;
	margin-bottom: 16rpx;
}

.doc-icon {
	width: 80rpx;
	height: 80rpx;
	border-radius: 12rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 20rpx;
}

.doc-icon.pdf { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%); }
.doc-icon.word { background: linear-gradient(135deg, #4a90d9 0%, #357abd 100%); }
.doc-icon.excel { background: linear-gradient(135deg, #27ae60 0%, #219a52 100%); }
.doc-icon.ppt { background: linear-gradient(135deg, #e67e22 0%, #d35400 100%); }
.doc-icon.other { background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%); }

.doc-ext {
	font-size: 20rpx;
	color: #fff;
	font-weight: 600;
}

.doc-info {
	flex: 1;
	min-width: 0;
}

.doc-name {
	font-size: 28rpx;
	color: #333;
	display: block;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
	margin-bottom: 8rpx;
}

.doc-meta {
	display: flex;
	gap: 20rpx;
}

.doc-size, .doc-time {
	font-size: 24rpx;
	color: #999;
}

.doc-actions {
	display: flex;
	gap: 16rpx;
}

.action-btn {
	width: 64rpx;
	height: 64rpx;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
}

.action-btn.download {
	background: #e8f5e9;
	color: #07C160;
}

.action-btn.delete {
	background: #ffebee;
	color: #ff4d4f;
}

/* 空状态 */
.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 120rpx 40rpx;
}

.empty-icon {
	color: #ddd;
	margin-bottom: 24rpx;
}

.empty-text {
	font-size: 32rpx;
	color: #999;
	margin-bottom: 12rpx;
}

.empty-tip {
	font-size: 26rpx;
	color: #ccc;
	text-align: center;
}

.loading-more {
	text-align: center;
	padding: 32rpx;
}

.loading-text {
	font-size: 26rpx;
	color: #999;
}

.bottom-spacer {
	height: 120rpx;
}

/* 图片预览弹窗 */
.preview-modal {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.9);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 999;
}

.preview-content {
	width: 100%;
	max-width: 700rpx;
}

.preview-image {
	width: 100%;
	max-height: 70vh;
}

.preview-info {
	padding: 24rpx;
	text-align: center;
}

.preview-name {
	font-size: 28rpx;
	color: #fff;
	display: block;
	margin-bottom: 8rpx;
}

.preview-meta {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.6);
}

.preview-actions {
	display: flex;
	justify-content: center;
	gap: 48rpx;
	padding: 24rpx;
}

.preview-btn {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 8rpx;
	color: #fff;
	font-size: 24rpx;
}

.preview-btn.delete {
	color: #ff4d4f;
}

.preview-close {
	position: absolute;
	top: 60rpx;
	right: 32rpx;
	width: 64rpx;
	height: 64rpx;
	background: rgba(255, 255, 255, 0.2);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	color: #fff;
}
</style>
