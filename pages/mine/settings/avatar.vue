<template>
	<view class="avatar-page">
		<view class="section">
			<text class="section-title">AI 头像</text>
			<view class="avatar-card" @click="chooseAIAvatar">
				<view class="avatar-preview">
					<image v-if="aiAvatar && !aiAvatar.startsWith('emoji:')" class="avatar-img" :src="aiAvatar" mode="aspectFill" />
					<text v-else-if="aiAvatar && aiAvatar.startsWith('emoji:')" class="avatar-emoji">{{ aiAvatar.replace('emoji:', '') }}</text>
					<view v-else class="avatar-default ai">
						<text class="avatar-icon">🤖</text>
					</view>
				</view>
				<view class="avatar-info">
					<text class="avatar-label">点击更换 AI 头像</text>
					<text class="avatar-tip">支持从相册选择或拍照</text>
				</view>
				<text class="arrow">›</text>
			</view>
			<view class="reset-btn" @click="resetAIAvatar" v-if="aiAvatar">
				<text>恢复默认</text>
			</view>
		</view>

		<view class="section">
			<text class="section-title">预设 AI 头像</text>
			<view class="preset-grid">
				<view 
					class="preset-item" 
					v-for="(item, index) in presetAvatars" 
					:key="index"
					@click="selectPreset(item)"
					:class="{ active: aiAvatar === 'emoji:' + item.emoji }"
				>
					<text class="preset-emoji">{{ item.emoji }}</text>
					<text class="preset-name">{{ item.name }}</text>
				</view>
			</view>
		</view>

		<view class="preview-section">
			<text class="section-title">预览效果</text>
			<view class="chat-preview">
				<view class="preview-msg user-msg">
					<view class="preview-avatar">
						<image v-if="userAvatar" class="avatar-img" :src="userAvatar" mode="aspectFill" />
						<view v-else class="avatar-default user small">
							<text class="avatar-icon">👤</text>
						</view>
					</view>
					<view class="preview-bubble user-bubble">
						<text>你好，这是用户消息</text>
					</view>
				</view>
				<view class="preview-msg ai-msg">
					<view class="preview-avatar">
						<image v-if="aiAvatar && !aiAvatar.startsWith('emoji:')" class="avatar-img" :src="aiAvatar" mode="aspectFill" />
						<text v-else-if="aiAvatar && aiAvatar.startsWith('emoji:')" class="avatar-emoji-small">{{ aiAvatar.replace('emoji:', '') }}</text>
						<view v-else class="avatar-default ai small">
							<text class="avatar-icon">🤖</text>
						</view>
					</view>
					<view class="preview-bubble ai-bubble">
						<text>你好，这是 AI 回复</text>
					</view>
				</view>
			</view>
		</view>

		<view class="tip-section">
			<text class="tip">💡 用户头像请在「账号设置」中修改</text>
		</view>
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { uploadFile } from '@/api/upload'

const AVATAR_KEY = 'custom_avatars'

const userAvatar = ref('')
const aiAvatar = ref('')

const presetAvatars = [
	{ emoji: '🤖', name: '机器人' },
	{ emoji: '🧠', name: '大脑' },
	{ emoji: '✨', name: '闪亮' },
	{ emoji: '🎯', name: '目标' },
	{ emoji: '🌟', name: '星星' },
	{ emoji: '💡', name: '灵感' },
	{ emoji: '🔮', name: '水晶球' },
	{ emoji: '🎨', name: '艺术' },
]

onMounted(() => {
	loadAvatars()
})

onShow(() => {
	loadAvatars()
})

const loadAvatars = () => {
	try {
		// 用户头像从账号设置获取
		userAvatar.value = uni.getStorageSync('customUserAvatar') || ''
		// AI头像
		const saved = uni.getStorageSync(AVATAR_KEY)
		if (saved) {
			const data = typeof saved === 'string' ? JSON.parse(saved) : saved
			aiAvatar.value = data.aiAvatar || ''
		}
	} catch (e) {}
}

const saveAIAvatar = () => {
	try {
		uni.setStorageSync(AVATAR_KEY, { aiAvatar: aiAvatar.value })
	} catch (e) {}
}

const chooseAIAvatar = () => {
	uni.chooseImage({
		count: 1,
		sizeType: ['compressed'],
		sourceType: ['album', 'camera'],
		success: async (res) => {
			uni.showLoading({ title: '上传中...' })
			try {
				const uploadRes = await uploadFile(res.tempFilePaths[0], 'avatar')
				uni.hideLoading()
				if (uploadRes.code === 0 && uploadRes.data?.url) {
					aiAvatar.value = uploadRes.data.url
					saveAIAvatar()
					uni.showToast({ title: '已保存', icon: 'success' })
				} else {
					uni.showToast({ title: '上传失败', icon: 'none' })
				}
			} catch (e) {
				uni.hideLoading()
				uni.showToast({ title: '上传失败', icon: 'none' })
			}
		}
	})
}

const selectPreset = (item) => {
	aiAvatar.value = 'emoji:' + item.emoji
	saveAIAvatar()
	uni.showToast({ title: '已保存', icon: 'success' })
}

const resetAIAvatar = () => {
	aiAvatar.value = ''
	saveAIAvatar()
	uni.showToast({ title: '已恢复默认', icon: 'success' })
}
</script>

<style scoped>
.avatar-page {
	min-height: 100vh;
	background: #f5f5f5;
	padding: 24rpx;
}

.section {
	margin-bottom: 32rpx;
}

.section-title {
	font-size: 28rpx;
	color: #666;
	margin-bottom: 16rpx;
	display: block;
	padding-left: 8rpx;
}

.avatar-card {
	background: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
	display: flex;
	align-items: center;
}

.avatar-preview {
	width: 100rpx;
	height: 100rpx;
	border-radius: 50%;
	overflow: hidden;
	margin-right: 24rpx;
	flex-shrink: 0;
}

.avatar-img {
	width: 100%;
	height: 100%;
}

.avatar-emoji {
	width: 100rpx;
	height: 100rpx;
	font-size: 60rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	background: #e8f5e9;
	border-radius: 50%;
}

.avatar-default {
	width: 100%;
	height: 100%;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 50%;
}

.avatar-default.ai {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
}

.avatar-default.user {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.avatar-icon {
	font-size: 48rpx;
}

.avatar-info {
	flex: 1;
}

.avatar-label {
	font-size: 30rpx;
	color: #333;
	display: block;
	margin-bottom: 8rpx;
}

.avatar-tip {
	font-size: 24rpx;
	color: #999;
}

.arrow {
	font-size: 36rpx;
	color: #ccc;
}

.reset-btn {
	margin-top: 16rpx;
	text-align: center;
}

.reset-btn text {
	font-size: 26rpx;
	color: #999;
}

.preset-grid {
	display: grid;
	grid-template-columns: repeat(4, 1fr);
	gap: 16rpx;
	background: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
}

.preset-item {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 16rpx;
	border-radius: 12rpx;
	background: #f8f8f8;
}

.preset-item.active {
	background: #e8f5e9;
	border: 2rpx solid #07C160;
}

.preset-emoji {
	font-size: 48rpx;
	margin-bottom: 8rpx;
}

.preset-name {
	font-size: 22rpx;
	color: #666;
}

.preview-section {
	margin-top: 32rpx;
}

.chat-preview {
	background: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
}

.preview-msg {
	display: flex;
	align-items: flex-start;
	margin-bottom: 20rpx;
}

.preview-msg:last-child {
	margin-bottom: 0;
}

.user-msg {
	flex-direction: row-reverse;
}

.preview-avatar {
	width: 64rpx;
	height: 64rpx;
	border-radius: 50%;
	overflow: hidden;
	flex-shrink: 0;
}

.preview-avatar .avatar-img {
	width: 100%;
	height: 100%;
}

.avatar-emoji-small {
	width: 64rpx;
	height: 64rpx;
	font-size: 36rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	background: #e8f5e9;
	border-radius: 50%;
}

.avatar-default.small {
	width: 64rpx;
	height: 64rpx;
}

.avatar-default.small .avatar-icon {
	font-size: 32rpx;
}

.preview-bubble {
	max-width: 60%;
	padding: 16rpx 20rpx;
	border-radius: 16rpx;
	margin: 0 16rpx;
}

.preview-bubble text {
	font-size: 26rpx;
}

.user-bubble {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	color: #fff;
	border-top-right-radius: 4rpx;
}

.ai-bubble {
	background: #f0f0f0;
	color: #333;
	border-top-left-radius: 4rpx;
}

.tip-section {
	margin-top: 40rpx;
	text-align: center;
}

.tip {
	font-size: 24rpx;
	color: #999;
}
</style>
