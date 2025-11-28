<template>
	<view class="login-page">
		<view class="login-container">
			<!-- Logo -->
			<view class="logo-section">
				<view class="logo-icon">
					<text class="logo-text">K</text>
				</view>
				<text class="app-name">知识库</text>
				<text class="app-desc">个人知识管理助手</text>
			</view>
			
			<!-- 登录表单 -->
			<view class="form-section" v-if="!isRegister">
				<view class="form-item">
					<text class="form-label">账号</text>
					<input 
						class="form-input" 
						type="text"
						v-model="loginForm.username"
						placeholder="请输入账号"
						@confirm="handleLogin"
					/>
				</view>
				
				<view class="form-item">
					<text class="form-label">密码</text>
					<input 
						class="form-input" 
						type="password"
						v-model="loginForm.password"
						placeholder="请输入密码"
						@confirm="handleLogin"
					/>
				</view>
				
				<view class="submit-btn" @click="handleLogin">
					<text class="submit-text">登 录</text>
				</view>
				
				<view class="switch-row">
					<text class="switch-text">还没有账号？</text>
					<text class="switch-link" @click="isRegister = true">立即注册</text>
				</view>
			</view>
			
			<!-- 注册表单 -->
			<view class="form-section" v-else>
				<view class="form-item">
					<text class="form-label">账号</text>
					<input 
						class="form-input" 
						type="text"
						v-model="registerForm.username"
						placeholder="请输入账号"
					/>
				</view>
				
				<view class="form-item">
					<text class="form-label">昵称</text>
					<input 
						class="form-input" 
						type="text"
						v-model="registerForm.nickname"
						placeholder="请输入昵称（选填）"
					/>
				</view>
				
				<view class="form-item">
					<text class="form-label">密码</text>
					<input 
						class="form-input" 
						type="password"
						v-model="registerForm.password"
						placeholder="请输入密码"
					/>
				</view>
				
				<view class="form-item">
					<text class="form-label">确认密码</text>
					<input 
						class="form-input" 
						type="password"
						v-model="registerForm.confirmPassword"
						placeholder="请再次输入密码"
						@confirm="handleRegister"
					/>
				</view>
				
				<view class="submit-btn" @click="handleRegister">
					<text class="submit-text">注 册</text>
				</view>
				
				<view class="switch-row">
					<text class="switch-text">已有账号？</text>
					<text class="switch-link" @click="isRegister = false">返回登录</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { login, register } from '@/api/user'

const isRegister = ref(false)

onMounted(() => {
	// 已登录则跳转主页
	const token = uni.getStorageSync('token')
	if (token) {
		uni.switchTab({ url: '/pages/chat/index' })
	}
})

const loginForm = ref({
	username: '',
	password: ''
})

const registerForm = ref({
	username: '',
	nickname: '',
	password: '',
	confirmPassword: ''
})

const handleLogin = async () => {
	if (!loginForm.value.username.trim()) {
		uni.showToast({ title: '请输入账号', icon: 'none' })
		return
	}
	if (!loginForm.value.password) {
		uni.showToast({ title: '请输入密码', icon: 'none' })
		return
	}
	
	uni.showLoading({ title: '登录中...' })
	
	try {
		const res = await login({
			username: loginForm.value.username,
			password: loginForm.value.password
		})
		
		uni.hideLoading()
		
		// 保存 token
		uni.setStorageSync('token', res.data.access_token)
		uni.setStorageSync('userInfo', res.data.user)
		
		uni.showToast({ title: '登录成功', icon: 'success' })
		
		setTimeout(() => {
			uni.switchTab({ url: '/pages/chat/index' })
		}, 1000)
	} catch (e) {
		uni.hideLoading()
		uni.showToast({ title: e.detail || '登录失败', icon: 'none' })
	}
}

const handleRegister = async () => {
	if (!registerForm.value.username.trim()) {
		uni.showToast({ title: '请输入账号', icon: 'none' })
		return
	}
	if (!registerForm.value.password) {
		uni.showToast({ title: '请输入密码', icon: 'none' })
		return
	}
	if (registerForm.value.password.length < 6) {
		uni.showToast({ title: '密码至少6位', icon: 'none' })
		return
	}
	if (registerForm.value.password !== registerForm.value.confirmPassword) {
		uni.showToast({ title: '两次密码不一致', icon: 'none' })
		return
	}
	
	uni.showLoading({ title: '注册中...' })
	
	try {
		await register({
			username: registerForm.value.username,
			password: registerForm.value.password,
			nickname: registerForm.value.nickname || registerForm.value.username
		})
		
		uni.hideLoading()
		uni.showToast({ title: '注册成功', icon: 'success' })
		
		// 切换到登录
		setTimeout(() => {
			isRegister.value = false
			loginForm.value.username = registerForm.value.username
			loginForm.value.password = ''
		}, 1000)
	} catch (e) {
		uni.hideLoading()
		uni.showToast({ title: e.detail || '注册失败', icon: 'none' })
	}
}
</script>

<style scoped>
* {
	box-sizing: border-box;
}

.login-page {
	min-height: 100vh;
	background: transparent;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 32rpx;
	box-sizing: border-box;
}

.login-container {
	width: 100%;
	max-width: 600rpx;
	box-sizing: border-box;
}

.logo-section {
	display: flex;
	flex-direction: column;
	align-items: center;
	margin-bottom: 80rpx;
}

.logo-icon {
	width: 140rpx;
	height: 140rpx;
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	border-radius: 32rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 24rpx;
	box-shadow: 0 8rpx 32rpx rgba(7, 193, 96, 0.3);
}

.logo-text {
	font-size: 72rpx;
	font-weight: bold;
	color: #fff;
}

.app-name {
	font-size: 44rpx;
	font-weight: 600;
	color: #333;
	margin-bottom: 12rpx;
}

.app-desc {
	font-size: 28rpx;
	color: #666;
}

.form-section {
	background-color: #fff;
	border-radius: 24rpx;
	padding: 40rpx 32rpx;
	box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.06);
	box-sizing: border-box;
}

.form-item {
	margin-bottom: 24rpx;
}

.form-label {
	display: block;
	font-size: 28rpx;
	color: #333;
	margin-bottom: 16rpx;
	font-weight: 500;
}

.form-input {
	width: 100%;
	height: 88rpx;
	padding: 0 24rpx;
	background-color: #f5f7f5;
	border-radius: 12rpx;
	font-size: 30rpx;
	border: 2rpx solid transparent;
	transition: border-color 0.2s;
	box-sizing: border-box;
}

.form-input:focus {
	border-color: #07C160;
	background-color: #fff;
}

.submit-btn {
	width: 100%;
	height: 88rpx;
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	border-radius: 12rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-top: 40rpx;
	box-shadow: 0 4rpx 16rpx rgba(7, 193, 96, 0.3);
}

.submit-btn:active {
	opacity: 0.9;
	transform: scale(0.98);
}

.submit-text {
	font-size: 32rpx;
	font-weight: 500;
	color: #fff;
	letter-spacing: 8rpx;
}

.switch-row {
	display: flex;
	align-items: center;
	justify-content: center;
	margin-top: 32rpx;
}

.switch-text {
	font-size: 26rpx;
	color: #999;
}

.switch-link {
	font-size: 26rpx;
	color: #07C160;
	margin-left: 8rpx;
}
</style>
