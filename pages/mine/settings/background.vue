<template>
	<view class="bg-page" :style="pageStyle">
		<view class="card">
			<text class="title">背景设置</text>
			<text class="desc">支持输入颜色（#ffffff）、CSS 渐变（linear-gradient）或图片 URL</text>
			<input 
				class="input" 
				v-model="backgroundInput" 
				placeholder="示例：#ffffff 或 linear-gradient(...) 或 https://xxx.jpg"
			/>
			<view class="btn-row">
				<view class="btn primary" @click="applyBackground">应用</view>
				<view class="btn" @click="resetBackground">恢复默认</view>
			</view>
			<view class="btn-row">
				<view class="btn" @click="pickImage">上传图片</view>
			</view>
			<view class="preview" :style="previewStyle">
				<text class="preview-text">预览</text>
			</view>
		</view>
	</view>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getBackgroundStyle, getBackgroundSetting, setBackgroundSetting, applyGlobalBackground } from '@/utils/theme'

const backgroundInput = ref('')
const pageStyle = ref(getBackgroundStyle())

onShow(() => {
	const bg = getBackgroundSetting()
	backgroundInput.value = bg.value || ''
	pageStyle.value = getBackgroundStyle()
	applyGlobalBackground()
})

const previewStyle = computed(() => {
	const val = backgroundInput.value.trim()
	if (!val) return { background: '#ffffff' }
	if (/^https?:\/\//.test(val) || val.startsWith('data:')) {
		return {
			backgroundImage: `url(${val})`,
			backgroundSize: 'cover',
			backgroundPosition: 'center',
			backgroundRepeat: 'no-repeat',
			backgroundColor: '#ffffff'
		}
	}
	return { background: val }
})

const applyBackground = () => {
	const val = backgroundInput.value.trim()
	if (!val) {
		uni.showToast({ title: '请输入背景值', icon: 'none' })
		return
	}
	const type = /^https?:\/\//.test(val) || val.startsWith('data:') ? 'image' : 'color'
	setBackgroundSetting({ type, value: val })
	pageStyle.value = getBackgroundStyle()
	uni.showToast({ title: '背景已应用', icon: 'none' })
}

const resetBackground = () => {
	const setting = setBackgroundSetting({ type: 'color', value: '#ffffff' })
	backgroundInput.value = setting.value
	pageStyle.value = getBackgroundStyle()
	uni.showToast({ title: '已恢复默认', icon: 'none' })
}

const pickImage = () => {
	uni.chooseImage({
		count: 1,
		success: async (res) => {
			const filePath = res.tempFilePaths?.[0]
			if (!filePath) {
				uni.showToast({ title: '选择失败', icon: 'none' })
				return
			}
			try {
				const dataUrl = await toBase64(filePath)
				backgroundInput.value = dataUrl
			} catch (e) {
				backgroundInput.value = filePath
			}
			applyBackground()
		},
		fail: () => {
			uni.showToast({ title: '选择失败', icon: 'none' })
		}
	})
}

const toBase64 = (filePath) => {
	return new Promise((resolve, reject) => {
		// H5: 直接用 fetch 转 base64
		// #ifdef H5
		fetch(filePath)
			.then(res => res.blob())
			.then(blob => {
				const reader = new FileReader()
				reader.onload = () => resolve(reader.result)
				reader.onerror = reject
				reader.readAsDataURL(blob)
			})
			.catch(reject)
		// #endif
		// 小程序/App
		// #ifndef H5
		try {
			const fs = uni.getFileSystemManager()
			fs.readFile({
				filePath,
				encoding: 'base64',
				success: (res) => {
					const ext = filePath.split('.').pop() || 'jpg'
					resolve(`data:image/${ext};base64,${res.data}`)
				},
				fail: reject
			})
		} catch (e) {
			reject(e)
		}
		// #endif
	})
}
</script>

<style scoped>
.bg-page {
	min-height: 100vh;
	padding: 16px;
	background: transparent;
}

.card {
	background: var(--card);
	border: 1px solid var(--border);
	border-radius: 14px;
	box-shadow: var(--shadow-plain);
	padding: 16px;
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.title {
	font-size: 18px;
	font-weight: 700;
	color: var(--brand-ink);
}

.desc {
	font-size: 13px;
	color: var(--brand-muted);
}

.input {
	width: 100%;
	height: 44px;
	border-radius: 10px;
	border: 1px solid var(--border);
	padding: 0 12px;
	font-size: 14px;
	color: var(--brand-ink);
	background-color: #f8fafc;
}

.btn-row {
	display: flex;
	gap: 12px;
}

.btn {
	flex: 1;
	text-align: center;
	padding: 12px 0;
	border-radius: 10px;
	border: 1px solid var(--border);
	color: var(--brand-ink);
	background-color: #f5f7fa;
	font-size: 14px;
}

.btn.primary {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	color: #ffffff;
	border: none;
	box-shadow: 0 10px 24px rgba(16, 240, 194, 0.25);
}

.preview {
	margin-top: 8px;
	height: 140px;
	border-radius: 12px;
	border: 1px solid var(--border);
	display: flex;
	align-items: center;
	justify-content: center;
	overflow: hidden;
}

.preview-text {
	color: var(--brand-muted);
}
</style>
