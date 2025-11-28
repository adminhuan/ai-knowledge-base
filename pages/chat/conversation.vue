<template>
	<view class="conversation" :style="pageStyle">
		<view class="conversation-hero">
			<view class="hero-left">
				<text class="hero-title">知识库对话</text>
				<text class="hero-desc">引用知识片段、追问细节，保持上下文连贯。</text>
			</view>
			<view class="hero-chip">
				<view class="chip-dot"></view>
				<text class="chip-text">{{ messages.length }} 条消息</text>
			</view>
		</view>

		<scroll-view 
			class="message-list" 
			scroll-y 
			:scroll-top="scrollTop"
			scroll-with-animation
			@scrolltoupper="loadMore"
			@scroll="onScroll"
		>
			<view class="message-wrapper">
				<view 
					class="message-item" 
					:class="{ 'is-user': msg.role === 'user' }"
					v-for="(msg, index) in messages" 
					:key="index"
				>
					<view class="avatar">
						<Icon :name="msg.role === 'user' ? 'user' : 'robot'" size="26" />
					</view>
					<view class="bubble" :class="{ 'user-bubble': msg.role === 'user' }">
						<text class="bubble-text">{{ msg.content }}</text>
						<view class="references" v-if="msg.references && msg.references.length > 0">
							<view class="ref-title">
								<Icon name="book" size="18" />
								<text class="ref-text">引用了知识</text>
							</view>
							<view 
								class="ref-item" 
								v-for="(ref, idx) in msg.references" 
								:key="idx"
								@click="goKnowledge(ref.id)"
							>
								<text class="ref-text">{{ ref.title }}</text>
							</view>
						</view>
					</view>
				</view>
				
				<view class="message-item" v-if="isTyping">
					<view class="avatar">
						<Icon name="robot" size="26" />
					</view>
					<view class="bubble typing">
						<view class="typing-dots">
							<view class="dot"></view>
							<view class="dot"></view>
							<view class="dot"></view>
						</view>
					</view>
				</view>
			</view>
		</scroll-view>
		
		<view class="quick-actions" v-if="messages.length === 0">
			<text class="qa-title">快捷提问</text>
			<view class="qa-grid">
				<view class="action-item" @click="quickAction('总结一下最近的知识')">
					<Icon name="clipboard" size="24" class="action-icon" />
					<text class="action-text">总结知识</text>
				</view>
				<view class="action-item" @click="quickAction('帮我检索相关内容')">
					<Icon name="search" size="24" class="action-icon" />
					<text class="action-text">检索知识</text>
				</view>
				<view class="action-item" @click="quickAction('整理今天的内容')">
					<Icon name="note" size="24" class="action-icon" />
					<text class="action-text">整理内容</text>
				</view>
			</view>
		</view>
		
		<view class="input-bar">
			<view class="input-wrapper">
				<textarea 
					class="input-field"
					v-model="inputText"
					placeholder="输入你想询问的内容，按回车发送"
					:auto-height="true"
					:maxlength="2000"
					@confirm="sendMessage"
				/>
			</view>
			<view class="send-btn" :class="{ 'active': inputText.trim() }" @click="sendMessage">
				<Icon name="send" size="22" class="send-icon" />
			</view>
		</view>
		
		<view class="safe-bottom"></view>
	</view>
</template>

<script setup>
import { ref, onMounted, nextTick, getCurrentInstance } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getMessages, sendChatMessage } from '@/api/chat'
import { getBackgroundStyle } from '@/utils/theme'
import Icon from '@/components/Icon.vue'

const props = defineProps({
	id: {
		type: String,
		default: 'new'
	}
})

const messages = ref([])
const inputText = ref('')
const isTyping = ref(false)
const scrollTop = ref(0)
const conversationId = ref('')
const pageStyle = ref(getBackgroundStyle())
const page = ref(1)
const pageSize = 50
const hasMore = ref(true)
const loadingMore = ref(false)
const currentScroll = ref(0)
const instance = getCurrentInstance()

onMounted(() => {
	const pages = getCurrentPages()
	const page = pages[pages.length - 1]
	conversationId.value = page.options?.id || 'new'
	
	if (conversationId.value !== 'new') {
		loadMessages()
	} else {
		messages.value = [{
			role: 'assistant',
			content: '你好！我是知识库 AI 助手。\n\n我可以帮你：\n- 检索知识库内容\n- 整理和总结信息\n- 回答问题并提供参考\n\n有什么可以帮助你的吗？'
		}]
	}
})

onShow(() => {
	pageStyle.value = getBackgroundStyle()
})

const loadMessages = async () => {
	try {
		const res = await getMessages(conversationId.value, { page: page.value, size: pageSize })
		const list = res.data || []
		if (page.value === 1) {
			messages.value = list
			scrollToBottom()
		} else {
			messages.value = [...list, ...messages.value]
		}
		hasMore.value = res.hasMore !== false && list.length === pageSize
	} catch (e) {
		console.error('加载消息失败', e)
	}
}

const sendMessage = async () => {
	const text = inputText.value.trim()
	if (!text || isTyping.value) return
	
	messages.value.push({
		role: 'user',
		content: text
	})
	inputText.value = ''
	scrollToBottom()
	
	isTyping.value = true
	
	try {
		const res = await sendChatMessage({
			conversationId: conversationId.value,
			message: text
		})
		
		isTyping.value = false
		
		messages.value.push({
			role: 'assistant',
			content: res.data.reply,
			references: res.data.references || []
		})
		
		if (res.data.conversationId) {
			conversationId.value = res.data.conversationId
		}
	} catch (e) {
		isTyping.value = false
		messages.value.push({
			role: 'assistant',
			content: '抱歉，网络异常，请稍后再试。（离线模式）'
		})
	}
	
	scrollToBottom()
}

const quickAction = (text) => {
	inputText.value = text
	sendMessage()
}

const goKnowledge = (id) => {
	uni.navigateTo({
		url: `/pages/knowledge/detail?id=${id}`
	})
}

const loadMore = () => {
	if (!hasMore.value || loadingMore.value) return
	loadOlderMessages()
}

const scrollToBottom = () => {
	nextTick(() => {
		scrollTop.value = 99999
	})
}

const onScroll = (e) => {
	currentScroll.value = e.detail.scrollTop
}

const getWrapperHeight = () => {
	return new Promise((resolve) => {
		const query = uni.createSelectorQuery().in(instance?.proxy)
		query.select('.message-wrapper').boundingClientRect((res) => {
			resolve(res?.height || 0)
		}).exec()
	})
}

const loadOlderMessages = async () => {
	loadingMore.value = true
	const prevHeight = await getWrapperHeight()
	const prevScroll = currentScroll.value
	page.value += 1
	await loadMessages()
	nextTick(async () => {
		const newHeight = await getWrapperHeight()
		const delta = newHeight - prevHeight
		scrollTop.value = prevScroll + delta
		loadingMore.value = false
	})
}

const loadMore = async () => {
	if (!hasMore.value || loadingMore.value) return
	loadingMore.value = true
	page.value += 1
	await loadMessages()
	loadingMore.value = false
}
</script>

<style scoped>
.conversation {
	display: flex;
	flex-direction: column;
	height: 100vh;
	background: transparent;
}

.conversation-hero {
	padding: 28rpx 28rpx 14rpx;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.hero-left {
	display: flex;
	flex-direction: column;
	gap: 6rpx;
}

.hero-title {
	font-size: 34rpx;
	font-weight: 700;
	color: var(--brand-ink);
}

.hero-desc {
	font-size: 24rpx;
	color: var(--brand-muted);
}

.hero-chip {
	display: flex;
	align-items: center;
	gap: 10rpx;
	padding: 14rpx 18rpx;
	border-radius: 999rpx;
	background: rgba(16, 240, 194, 0.08);
	border: 1rpx solid rgba(16, 240, 194, 0.2);
	box-shadow: 0 10rpx 24rpx rgba(0, 0, 0, 0.32);
}

.chip-dot {
	width: 14rpx;
	height: 14rpx;
	background: #06AD56;
	border-radius: 50%;
	box-shadow: 0 0 8rpx rgba(16, 240, 194, 0.5);
}

.chip-text {
	font-size: 24rpx;
	color: var(--brand-ink);
}

.message-list {
	flex: 1;
	padding: 0 24rpx 24rpx;
	min-height: 0;
	overflow-y: auto;
	-webkit-overflow-scrolling: touch;
}

.message-wrapper {
	display: flex;
	flex-direction: column;
	gap: 18rpx;
}

.message-item {
	display: flex;
	align-items: flex-start;
}

.message-item.is-user {
	flex-direction: row-reverse;
}

.avatar {
	width: 72rpx;
	height: 72rpx;
	border-radius: 18rpx;
	background: radial-gradient(circle at 30% 30%, #06AD56 0%, #07C160 70%);
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
	box-shadow: 0 10rpx 22rpx rgba(0, 0, 0, 0.4), 0 0 0 1rpx rgba(16, 240, 194, 0.25);
}

.is-user .avatar {
	background: radial-gradient(circle at 30% 30%, #07C160 0%, #0b2042 70%);
}

.avatar-icon {
	font-size: 36rpx;
	color: #fff;
}

.bubble {
	max-width: 72%;
	padding: 20rpx 24rpx;
	background-color: var(--card);
	border-radius: 18rpx;
	margin-left: 16rpx;
	box-shadow: var(--shadow-plain);
	border: 1rpx solid var(--border);
}

.user-bubble {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	margin-left: 0;
	margin-right: 16rpx;
}

.bubble-text {
	font-size: 30rpx;
	color: var(--brand-ink);
	line-height: 1.6;
	white-space: pre-wrap;
	word-break: break-all;
}

.user-bubble .bubble-text {
	color: #ffffff;
}

.references {
	margin-top: 16rpx;
	padding-top: 14rpx;
	border-top: 1rpx solid var(--border);
}

.ref-title {
	display: flex;
	align-items: center;
	gap: 8rpx;
	font-size: 24rpx;
	color: var(--brand-muted);
	margin-bottom: 10rpx;
}

.ref-item {
	padding: 10rpx 16rpx;
	background-color: var(--card-strong);
	border-radius: 12rpx;
	margin-bottom: 8rpx;
	border: 1rpx solid var(--border);
}

.ref-text {
	font-size: 24rpx;
	color: #06AD56;
}

.typing {
	padding: 24rpx;
}

.typing-dots {
	display: flex;
	align-items: center;
}

.dot {
	width: 12rpx;
	height: 12rpx;
	background-color: #7c8aa4;
	border-radius: 50%;
	margin-right: 8rpx;
	animation: typing 1.4s infinite;
}

.dot:nth-child(2) {
	animation-delay: 0.2s;
}

.dot:nth-child(3) {
	animation-delay: 0.4s;
	margin-right: 0;
}

@keyframes typing {
	0%, 60%, 100% {
		transform: translateY(0);
		opacity: 0.6;
	}
	30% {
		transform: translateY(-8rpx);
		opacity: 1;
	}
}

.quick-actions {
	padding: 20rpx 28rpx 0;
}

.qa-title {
	font-size: 26rpx;
	color: var(--brand-muted);
	margin-bottom: 12rpx;
}

.qa-grid {
	display: flex;
	gap: 18rpx;
}

.action-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 24rpx 20rpx;
	background-color: var(--card);
	border-radius: 16rpx;
	box-shadow: var(--shadow-plain);
	border: 1rpx solid var(--border);
}

.action-icon {
	margin-bottom: 10rpx;
	color: var(--brand-ink);
}

.action-text {
	font-size: 26rpx;
	color: var(--brand-ink);
}

.input-bar {
	display: flex;
	align-items: flex-end;
	padding: 18rpx 24rpx;
	background-color: var(--card);
	border-top: 1rpx solid var(--border);
	box-shadow: 0 -6rpx 16rpx rgba(0, 0, 0, 0.08);
}

.input-wrapper {
	flex: 1;
	background-color: var(--card-strong);
	border-radius: 28rpx;
	padding: 10rpx 18rpx;
	margin-right: 16rpx;
	border: 1rpx solid var(--border);
	box-shadow: inset 0 0 0 1rpx rgba(16, 240, 194, 0.08);
}

.input-field {
	width: 100%;
	font-size: 30rpx;
	min-height: 80rpx;
	line-height: 1.5;
	color: var(--brand-ink);
}

.send-btn {
	width: 80rpx;
	height: 80rpx;
	background: radial-gradient(circle at 30% 30%, #06AD56 0%, #07C160 80%);
	border-radius: 20rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: background-color 0.2s, transform 0.1s;
	box-shadow: 0 12rpx 26rpx rgba(16, 240, 194, 0.25);
	border: 1rpx solid rgba(16, 240, 194, 0.4);
}

.send-btn.active {
	transform: translateY(-2rpx);
	box-shadow: 0 14rpx 30rpx rgba(16, 240, 194, 0.35);
}

.send-icon {
	font-size: 32rpx;
	color: #ffffff;
	font-weight: 700;
}

.safe-bottom {
	height: env(safe-area-inset-bottom);
	background-color: var(--card);
}
</style>
