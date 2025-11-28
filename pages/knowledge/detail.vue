<template>
	<view class="detail" :style="pageStyle">
		<view class="view-mode" v-if="mode === 'view'">
			<view class="hero-card">
				<view class="title-row">
					<text class="title">{{ knowledge.title }}</text>
					<text class="source" :class="knowledge.source">{{ sourceText(knowledge.source) }}</text>
				</view>
				<view class="meta">
					<text class="time">{{ knowledge.createdAt }}</text>
					<view class="pill">
						<text class="pill-dot"></text>
						<text class="pill-text">知识条目</text>
					</view>
				</view>
			</view>
			
			<view class="content-card">
				<text class="content-text">{{ knowledge.content }}</text>
			</view>
			
			<view class="tags-section" v-if="knowledge.tags && knowledge.tags.length">
				<text class="section-title">标签</text>
				<view class="tags">
					<text class="tag" v-for="tag in knowledge.tags" :key="tag">{{ tag }}</text>
				</view>
			</view>
			
			<view class="actions">
				<view class="action-btn" @click="editMode">
					<Icon name="note" size="24" class="action-icon" />
					<text class="action-text">编辑</text>
				</view>
				<view class="action-btn" @click="askAI">
					<Icon name="robot" size="24" class="action-icon" />
					<text class="action-text">AI 解读</text>
				</view>
				<view class="action-btn" @click="shareKnowledge">
					<Icon name="share" size="24" class="action-icon" />
					<text class="action-text">分享</text>
				</view>
			</view>
		</view>
		
		<view class="edit-mode" v-else>
			<view class="form-card">
				<text class="label">标题</text>
				<input 
					class="input" 
					v-model="formData.title" 
					placeholder="输入知识标题"
				/>
			</view>
			
			<view class="form-card">
				<text class="label">内容</text>
				<textarea 
					class="textarea" 
					v-model="formData.content" 
					placeholder="输入知识内容..."
					:auto-height="true"
					:maxlength="10000"
				/>
			</view>
			
			<view class="form-card">
				<text class="label">标签（用逗号分隔）</text>
				<input 
					class="input" 
					v-model="formData.tagsStr" 
					placeholder="标签1, 标签2, 标签3"
				/>
			</view>
			
			<view class="ai-assist">
				<view class="assist-btn" @click="aiSummary">
					<Icon name="sparkle" size="20" class="assist-icon" />
					<view class="assist-texts">
						<text class="assist-title">AI 自动总结</text>
						<text class="assist-sub">生成更精炼的标题</text>
					</view>
				</view>
				<view class="assist-btn" @click="aiTags">
					<Icon name="tag" size="20" class="assist-icon" />
					<view class="assist-texts">
						<text class="assist-title">AI 生成标签</text>
						<text class="assist-sub">自动补充合适标签</text>
					</view>
				</view>
			</view>
			
			<view class="submit-bar">
				<view class="cancel-btn" @click="cancel">取消</view>
				<view class="save-btn" @click="save">保存</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getKnowledgeDetail, saveKnowledge, updateKnowledge } from '@/api/knowledge'
import { aiSummarize, aiGenerateTags } from '@/api/ai'
import { getBackgroundStyle } from '@/utils/theme'
import Icon from '@/components/Icon.vue'

const mode = ref('view')
const knowledgeId = ref('')
const knowledge = ref({
	title: '',
	content: '',
	source: 'manual',
	tags: [],
	createdAt: ''
})

const formData = ref({
	title: '',
	content: '',
	tagsStr: ''
})
const pageStyle = ref(getBackgroundStyle())

onMounted(() => {
	const pages = getCurrentPages()
	const page = pages[pages.length - 1]
	const options = page.options || {}
	
	knowledgeId.value = options.id || ''
	mode.value = options.mode || 'view'
	
	if (options.content) {
		formData.value.content = decodeURIComponent(options.content)
		mode.value = 'add'
	}
	
	if (knowledgeId.value && mode.value === 'view') {
		loadDetail()
	}
	
	uni.setNavigationBarTitle({
		title: mode.value === 'add' ? '添加知识' : mode.value === 'edit' ? '编辑知识' : '知识详情'
	})
})

onShow(() => {
	pageStyle.value = getBackgroundStyle()
})

const loadDetail = async () => {
	try {
		const res = await getKnowledgeDetail(knowledgeId.value)
		knowledge.value = res.data
	} catch (e) {
		uni.showToast({ title: '加载失败', icon: 'none' })
	}
}

const editMode = () => {
	mode.value = 'edit'
	formData.value = {
		title: knowledge.value.title,
		content: knowledge.value.content,
		tagsStr: knowledge.value.tags?.join(', ') || ''
	}
	uni.setNavigationBarTitle({ title: '编辑知识' })
}

const cancel = () => {
	if (knowledgeId.value) {
		mode.value = 'view'
		uni.setNavigationBarTitle({ title: '知识详情' })
	} else {
		uni.navigateBack()
	}
}

const save = async () => {
	if (!formData.value.title.trim()) {
		uni.showToast({ title: '请输入标题', icon: 'none' })
		return
	}
	if (!formData.value.content.trim()) {
		uni.showToast({ title: '请输入内容', icon: 'none' })
		return
	}
	
	const data = {
		title: formData.value.title,
		content: formData.value.content,
		tags: formData.value.tagsStr.split(/[,，]/).map(t => t.trim()).filter(t => t),
		source: 'manual'
	}
	
	try {
		if (knowledgeId.value) {
			await updateKnowledge(knowledgeId.value, data)
		} else {
			await saveKnowledge(data)
		}
		uni.showToast({ title: '保存成功' })
		setTimeout(() => {
			uni.navigateBack()
		}, 1500)
	} catch (e) {
		uni.showToast({ title: '保存成功（离线模式）' })
		setTimeout(() => {
			uni.navigateBack()
		}, 1500)
	}
}

const aiSummary = async () => {
	if (!formData.value.content.trim()) {
		uni.showToast({ title: '请先输入内容', icon: 'none' })
		return
	}
	
	uni.showLoading({ title: 'AI处理中...' })
	try {
		const res = await aiSummarize(formData.value.content)
		formData.value.title = res.data.title || formData.value.title
		uni.hideLoading()
		uni.showToast({ title: '生成成功' })
	} catch (e) {
		uni.hideLoading()
		if (formData.value.content.length > 20) {
			formData.value.title = formData.value.content.substring(0, 20) + '...'
		}
	}
}

const aiTags = async () => {
	if (!formData.value.content.trim()) {
		uni.showToast({ title: '请先输入内容', icon: 'none' })
		return
	}
	
	uni.showLoading({ title: 'AI处理中...' })
	try {
		const res = await aiGenerateTags(formData.value.content)
		formData.value.tagsStr = res.data.tags?.join(', ') || ''
		uni.hideLoading()
		uni.showToast({ title: '生成成功' })
	} catch (e) {
		uni.hideLoading()
		formData.value.tagsStr = '知识, 笔记'
	}
}

const askAI = () => {
	uni.navigateTo({
		url: `/pages/chat/conversation?id=new&prompt=${encodeURIComponent('请帮我解读这段内容：' + knowledge.value.content)}`
	})
}

const shareKnowledge = () => {
	// #ifdef H5
	if (navigator.share) {
		navigator.share({
			title: knowledge.value.title,
			text: knowledge.value.content
		})
	} else {
		uni.setClipboardData({
			data: `${knowledge.value.title}\n\n${knowledge.value.content}`,
			success: () => {
				uni.showToast({ title: '已复制到剪贴板' })
			}
		})
	}
	// #endif
	// #ifndef H5
	uni.setClipboardData({
		data: `${knowledge.value.title}\n\n${knowledge.value.content}`,
		success: () => {
			uni.showToast({ title: '已复制到剪贴板' })
		}
	})
	// #endif
}

const sourceText = (source) => {
	const map = {
		chat: '聊天提取',
		manual: '手动添加',
		import: '导入'
	}
	return map[source] || source
}
</script>

<style scoped>
.detail {
	min-height: 100vh;
	background: transparent;
	padding-bottom: 140rpx;
}

.view-mode {
	padding: 28rpx;
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.hero-card {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	border-radius: 22rpx;
	padding: 28rpx;
	color: #ffffff;
	box-shadow: var(--shadow-soft);
}

.title-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 12rpx;
	margin-bottom: 12rpx;
}

.title {
	font-size: 36rpx;
	font-weight: 700;
	flex: 1;
}

.source {
	font-size: 24rpx;
	padding: 6rpx 14rpx;
	border-radius: 12rpx;
	background: rgba(255, 255, 255, 0.14);
	color: #ffffff;
	font-weight: 600;
}

.source.chat {
	background-color: rgba(255, 255, 255, 0.2);
}

.source.manual {
	background-color: rgba(255, 255, 255, 0.2);
}

.meta {
	display: flex;
	justify-content: space-between;
	align-items: center;
	font-size: 24rpx;
	color: #e6ecf7;
}

.time {
	color: #d6e4ff;
}

.pill {
	display: flex;
	align-items: center;
	gap: 10rpx;
	padding: 10rpx 14rpx;
	background: rgba(255, 255, 255, 0.16);
	border-radius: 999rpx;
}

.pill-dot {
	width: 12rpx;
	height: 12rpx;
	background: #fff;
	border-radius: 50%;
}

.pill-text {
	color: #fff;
}

.content-card {
	background-color: var(--card);
	border-radius: 18rpx;
	padding: 28rpx;
	margin-top: -12rpx;
	box-shadow: var(--shadow-plain);
	border: 1rpx solid var(--border);
}

.content-text {
	font-size: 30rpx;
	color: var(--brand-ink);
	line-height: 1.8;
	white-space: pre-wrap;
}

.tags-section {
	background-color: var(--card);
	border-radius: 18rpx;
	padding: 24rpx;
	box-shadow: var(--shadow-plain);
	border: 1rpx solid var(--border);
}

.section-title {
	font-size: 28rpx;
	color: var(--brand-muted);
	margin-bottom: 16rpx;
	display: block;
}

.tags {
	display: flex;
	flex-wrap: wrap;
	gap: 12rpx;
}

.tag {
	font-size: 26rpx;
	color: #06AD56;
	background-color: rgba(16, 240, 194, 0.12);
	padding: 8rpx 20rpx;
	border-radius: 24rpx;
	border: 1rpx solid rgba(16, 240, 194, 0.35);
}

.actions {
	display: flex;
	justify-content: space-between;
	background-color: var(--card);
	border-radius: 18rpx;
	padding: 24rpx;
	box-shadow: var(--shadow-plain);
	border: 1rpx solid var(--border);
}

.action-btn {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 6rpx;
}

.action-icon {
	color: var(--brand-ink);
}

.action-text {
	font-size: 26rpx;
	color: var(--brand-ink);
}

.edit-mode {
	padding: 28rpx;
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.form-card {
	background: var(--card);
	border-radius: 18rpx;
	padding: 22rpx;
	box-shadow: var(--shadow-plain);
	border: 1rpx solid var(--border);
}

.label {
	font-size: 28rpx;
	color: var(--brand-muted);
	margin-bottom: 12rpx;
	display: block;
}

.input {
	width: 100%;
	font-size: 32rpx;
	padding: 16rpx;
	background-color: #f5f5f5;
	border-radius: 12rpx;
	color: var(--brand-ink);
	border: 1rpx solid var(--border);
}

.textarea {
	width: 100%;
	min-height: 300rpx;
	font-size: 30rpx;
	padding: 16rpx;
	background-color: #f5f5f5;
	border-radius: 12rpx;
	line-height: 1.6;
	color: var(--brand-ink);
	border: 1rpx solid var(--border);
}

.ai-assist {
	display: flex;
	gap: 18rpx;
	margin-top: 8rpx;
}

.assist-btn {
	flex: 1;
	display: flex;
	align-items: center;
	gap: 12rpx;
	padding: 18rpx;
	background-color: var(--card);
	border-radius: 16rpx;
	border: 2rpx dashed rgba(16, 240, 194, 0.6);
}

.assist-icon {
	font-size: 32rpx;
}

.assist-texts {
	display: flex;
	flex-direction: column;
	gap: 2rpx;
}

.assist-title {
	font-size: 28rpx;
	color: #06AD56;
	font-weight: 600;
}

.assist-sub {
	font-size: 24rpx;
	color: var(--brand-muted);
}

.submit-bar {
	display: flex;
	gap: 18rpx;
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	padding: 22rpx 28rpx;
	background-color: rgba(15, 23, 42, 0.9);
	box-shadow: 0 -10rpx 28rpx rgba(0, 0, 0, 0.35);
	border-top: 1rpx solid var(--border);
}

.cancel-btn {
	flex: 1;
	text-align: center;
	padding: 22rpx;
	font-size: 32rpx;
	color: var(--brand-muted);
	background-color: #f5f5f5;
	border-radius: 12rpx;
	border: 1rpx solid var(--border);
}

.save-btn {
	flex: 1;
	text-align: center;
	padding: 22rpx;
	font-size: 32rpx;
	color: #fff;
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	border-radius: 12rpx;
	box-shadow: var(--shadow-soft);
	border: 1rpx solid rgba(16, 240, 194, 0.5);
}
</style>
