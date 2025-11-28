<template>
	<view class="account-page">
		<view class="page-header">
			<text class="page-title">账号设置</text>
		</view>

		<!-- 头像设置 -->
		<view class="section">
			<view class="section-title">头像</view>
			<view class="avatar-row" @click="chooseAvatar">
				<view class="current-avatar">
					<image v-if="userAvatar && typeof userAvatar === 'string'" :src="userAvatar" class="avatar-img" mode="aspectFill" />
					<view v-else class="avatar-placeholder">
						<text>{{ userName ? userName[0] : 'U' }}</text>
					</view>
				</view>
				<text class="change-text">点击更换头像</text>
				<text class="arrow">›</text>
			</view>
		</view>

		<!-- 基本信息 -->
		<view class="section">
			<view class="section-title">基本信息</view>
			<view class="card">
				<view class="field">
					<text class="label">用户名</text>
					<input class="input" v-model="username" placeholder="登录账号" />
				</view>
				<view class="field">
					<text class="label">昵称</text>
					<input class="input" v-model="nickname" placeholder="显示名称" />
				</view>
			</view>
			<text class="hint">* 修改用户名后需用新用户名登录</text>
			<view class="btn primary" @click="saveProfile">保存修改</view>
		</view>

		<!-- 修改密码 -->
		<view class="section">
			<view class="section-title">修改密码</view>
			<view class="card">
				<view class="field">
					<text class="label">原密码</text>
					<input class="input" type="password" v-model="oldPassword" placeholder="请输入原密码" />
				</view>
				<view class="field">
					<text class="label">新密码</text>
					<input class="input" type="password" v-model="newPassword" placeholder="至少6位" />
				</view>
				<view class="field">
					<text class="label">确认密码</text>
					<input class="input" type="password" v-model="confirmPassword" placeholder="再次输入新密码" />
				</view>
			</view>
			<view class="btn danger" @click="changePassword">修改密码</view>
		</view>
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getUserInfo, updateProfile, changePassword as changePasswordApi } from '@/api/user'
import { uploadFile } from '@/api/upload'

const username = ref('')
const nickname = ref('')
const userAvatar = ref('')
const userName = ref('')

const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

onMounted(() => {
	loadUserInfo()
})

const loadUserInfo = async () => {
	try {
		const res = await getUserInfo()
		if (res.code === 0) {
			username.value = res.data.username || ''
			nickname.value = res.data.nickname || res.data.name || ''
			// 确保 avatar 是字符串
			const avatar = res.data.avatar
			userAvatar.value = (typeof avatar === 'string') ? avatar : ''
			userName.value = res.data.name || ''
		}
	} catch (e) {
		console.log('加载用户信息失败', e)
	}
}

const chooseAvatar = () => {
	uni.chooseImage({
		count: 1,
		sizeType: ['compressed'],
		sourceType: ['album', 'camera'],
		success: async (res) => {
			const tempPath = res.tempFilePaths[0]
			uni.showLoading({ title: '上传中...' })
			
			try {
				const uploadRes = await uploadFile(tempPath, 'avatar')
				uni.hideLoading()
				if (uploadRes.code === 0 && uploadRes.data?.url) {
					userAvatar.value = uploadRes.data.url
					// 保存到服务器
					try {
						await updateProfile({ avatar: uploadRes.data.url })
					} catch (e) {
						console.log('保存头像失败', e)
					}
					// 同时保存到本地
					uni.setStorageSync('customUserAvatar', uploadRes.data.url)
					uni.showToast({ title: '头像已更新', icon: 'success' })
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

const saveProfile = async () => {
	if (!username.value.trim()) {
		uni.showToast({ title: '请输入用户名', icon: 'none' })
		return
	}
	if (!nickname.value.trim()) {
		uni.showToast({ title: '请输入昵称', icon: 'none' })
		return
	}
	
	try {
		const res = await updateProfile({ 
			username: username.value.trim(),
			nickname: nickname.value.trim() 
		})
		if (res.code === 0) {
			uni.showToast({ title: '保存成功', icon: 'success' })
		} else {
			uni.showToast({ title: res.message || '保存失败', icon: 'none' })
		}
	} catch (e) {
		uni.showToast({ title: e.message || '保存失败', icon: 'none' })
	}
}

const changePassword = async () => {
	if (!oldPassword.value) {
		uni.showToast({ title: '请输入原密码', icon: 'none' })
		return
	}
	if (!newPassword.value || newPassword.value.length < 6) {
		uni.showToast({ title: '新密码至少6位', icon: 'none' })
		return
	}
	if (newPassword.value !== confirmPassword.value) {
		uni.showToast({ title: '两次密码不一致', icon: 'none' })
		return
	}
	
	try {
		const res = await changePasswordApi({
			old_password: oldPassword.value,
			new_password: newPassword.value
		})
		if (res.code === 0) {
			uni.showToast({ title: '密码修改成功', icon: 'success' })
			oldPassword.value = ''
			newPassword.value = ''
			confirmPassword.value = ''
		} else {
			uni.showToast({ title: res.message || '修改失败', icon: 'none' })
		}
	} catch (e) {
		uni.showToast({ title: e.message || '修改失败', icon: 'none' })
	}
}
</script>

<style scoped>
.account-page {
	min-height: 100vh;
	background: #f5f5f5;
	padding: 24rpx;
}

.page-header {
	padding: 24rpx 0 32rpx;
}

.page-title {
	font-size: 36rpx;
	font-weight: 600;
	color: #333;
}

.section {
	margin-bottom: 32rpx;
}

.section-title {
	font-size: 26rpx;
	color: #999;
	margin-bottom: 16rpx;
	padding-left: 8rpx;
}

.avatar-row {
	display: flex;
	align-items: center;
	background: #fff;
	padding: 24rpx;
	border-radius: 16rpx;
}

.current-avatar {
	width: 100rpx;
	height: 100rpx;
	border-radius: 50%;
	overflow: hidden;
	margin-right: 24rpx;
}

.avatar-img {
	width: 100%;
	height: 100%;
}

.avatar-placeholder {
	width: 100%;
	height: 100%;
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	display: flex;
	align-items: center;
	justify-content: center;
	color: #fff;
	font-size: 40rpx;
	font-weight: 600;
}

.change-text {
	flex: 1;
	font-size: 28rpx;
	color: #666;
}

.arrow {
	font-size: 32rpx;
	color: #ccc;
}

.card {
	background: #fff;
	border-radius: 16rpx;
	padding: 8rpx 24rpx;
	margin-bottom: 24rpx;
}

.field {
	display: flex;
	align-items: center;
	padding: 24rpx 0;
	border-bottom: 1rpx solid #f0f0f0;
}

.field:last-child {
	border-bottom: none;
}

.label {
	width: 160rpx;
	font-size: 28rpx;
	color: #333;
}

.value {
	flex: 1;
	font-size: 28rpx;
	color: #333;
	text-align: right;
}

.value.readonly {
	color: #999;
}

.input {
	flex: 1;
	font-size: 28rpx;
	color: #333;
	text-align: right;
}

.hint {
	font-size: 24rpx;
	color: #999;
	margin: 16rpx 0;
	display: block;
}

.btn {
	padding: 24rpx;
	text-align: center;
	border-radius: 12rpx;
	font-size: 28rpx;
	font-weight: 500;
}

.btn.primary {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	color: #fff;
}

.btn.danger {
	background: #fff;
	color: #ff4d4f;
	border: 1rpx solid #ff4d4f;
}
</style>
