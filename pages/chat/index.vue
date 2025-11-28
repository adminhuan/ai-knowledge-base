<template>
	<view class="chat-page" :style="pageStyle">
		<!-- 顶部栏（固定） -->
		<view class="header-fixed">
			<view class="header-left" @click="showHistory = true">
				<Icon name="menu" class="icon-btn" />
			</view>
			<text class="header-title">{{ currentModeTitle }}</text>
			<view class="header-right">
				<view class="mode-switch" :class="{ 'active': webSearchMode }" @click="toggleWebSearch">
					<Icon name="globe" size="18" />
				</view>
				<view class="mode-switch" :class="{ 'active': searchMode }" @click="toggleMode" style="margin-left: 16rpx;">
					<Icon name="search" size="18" />
				</view>
			</view>
		</view>
		
		<!-- 模式提示 -->
		<view class="mode-tip" :class="{ 'web': webSearchMode && !searchMode, 'combined': webSearchMode && searchMode }" v-if="searchMode || webSearchMode">
			<Icon :name="webSearchMode ? 'globe' : 'search'" size="16" />
			<text>{{ currentModeTitle }}</text>
		</view>
		
		<!-- 消息列表（原生滚动） -->
		<view class="message-list">
			<!-- 欢迎信息 -->
			<view class="welcome" v-if="messages.length === 0">
				<view class="welcome-icon">
					<Icon name="robot" size="52" />
				</view>
				<text class="welcome-title">AI 知识助手</text>
				<text class="welcome-desc">我可以帮你检索知识库、整理信息、回答问题</text>
				
				<view class="quick-actions">
					<view class="action-item" @click="quickAsk('总结一下最近的知识')">
						<Icon name="clipboard" size="24" class="action-icon" />
						<text class="action-text">总结知识</text>
					</view>
					<view class="action-item" @click="quickAsk('帮我检索相关内容')">
						<Icon name="search" size="24" class="action-icon" />
						<text class="action-text">检索知识</text>
					</view>
					<view class="action-item" @click="quickAsk('整理今天的内容')">
						<Icon name="note" size="24" class="action-icon" />
						<text class="action-text">整理内容</text>
					</view>
				</view>
			</view>
			
			<!-- 消息气泡 -->
			<view class="message-wrapper">
				<view 
					class="message-item" 
					:class="{ 'is-user': msg.role === 'user', 'is-selected': selectMode && selectedMsgs.includes(index) }"
					v-for="(msg, index) in messages" 
					:key="index"
					@longpress="onMsgLongPress(index)"
					@click="onMsgClick(index)"
				>
					<!-- 多选复选框 -->
					<view class="select-checkbox" v-if="selectMode" @click.stop="toggleSelect(index)">
						<view class="checkbox" :class="{ 'checked': selectedMsgs.includes(index) }">
							<text v-if="selectedMsgs.includes(index)">✓</text>
						</view>
					</view>
					<view class="avatar" :class="{ 'user-avatar': msg.role === 'user', 'ai-avatar': msg.role !== 'user' }">
						<image v-if="msg.role === 'user' && userAvatar && !userAvatar.startsWith('emoji:')" class="avatar-img" :src="userAvatar" mode="aspectFill" />
						<image v-else-if="msg.role !== 'user' && aiAvatar && !aiAvatar.startsWith('emoji:')" class="avatar-img" :src="aiAvatar" mode="aspectFill" />
						<text v-else-if="msg.role === 'user' && userAvatar && userAvatar.startsWith('emoji:')" class="avatar-emoji">{{ userAvatar.replace('emoji:', '') }}</text>
						<text v-else-if="msg.role !== 'user' && aiAvatar && aiAvatar.startsWith('emoji:')" class="avatar-emoji">{{ aiAvatar.replace('emoji:', '') }}</text>
						<Icon v-else :name="msg.role === 'user' ? 'user' : 'robot'" size="28" />
					</view>
					<view class="bubble-wrapper">
						<!-- 转发的聊天记录卡片 -->
						<view class="chat-record-card" v-if="msg.chatRecords" @click="showRecordDetail(msg)">
							<view class="record-header">
								<Icon name="chat" size="16" />
								<text class="record-title">聊天记录</text>
							</view>
							<view class="record-preview">
								<view class="record-item" v-for="(r, ri) in msg.chatRecords.slice(0, 3)" :key="ri">
									<text class="record-name">{{ r.name }}：</text>
									<text class="record-text">{{ r.content.length > 20 ? r.content.slice(0, 20) + '...' : r.content }}</text>
								</view>
								<text class="record-more" v-if="msg.chatRecords.length > 3">共 {{ msg.chatRecords.length }} 条消息</text>
							</view>
							<view class="record-footer">
								<text class="record-label">聊天记录</text>
							</view>
						</view>
						<!-- 普通消息气泡 -->
						<view class="bubble" :class="{ 'user-bubble': msg.role === 'user', 'ai-bubble': msg.role === 'assistant' }" v-else>
							<!-- 引用内容显示 -->
							<view class="msg-quote" v-if="msg.quote" @click="scrollToQuotedMsg(msg.quote)">
								<view class="msg-quote-bar"></view>
								<view class="msg-quote-content">
									<text class="msg-quote-role">{{ msg.quote.role === 'assistant' ? 'AI' : '我' }}</text>
									<text class="msg-quote-text">{{ msg.quote.content.length > 60 ? msg.quote.content.substring(0, 60) + '...' : msg.quote.content }}</text>
								</view>
							</view>
							<!-- 文件/图片预览 -->
							<view class="msg-file" v-if="msg.file && !isInvalidBlobUrl(msg.file.path)">
								<image 
									v-if="msg.file.type === 'image'" 
									class="msg-image" 
									:src="msg.file.path" 
									mode="widthFix"
									@click="previewImage(msg.file.path)"
								/>
								<view v-else class="msg-file-icon">
									<Icon :name="getFileIcon(msg.file.type)" size="32" />
									<text class="msg-file-ext">{{ getFileExt(msg.file.name) }}</text>
								</view>
							</view>
							<!-- AI 回复 (Markdown 渲染) -->
							<rich-text class="bubble-text markdown-content" v-if="msg.role === 'assistant'" :nodes="parseMarkdown(msg.content)"></rich-text>
							<!-- 用户消息 -->
							<text class="bubble-text" v-else-if="!msg.file || msg.content.includes('\n')">{{ getDisplayContent(msg) }}</text>
						</view>
						<!-- 消息操作 -->
						<view class="msg-actions">
							<!-- 文件/图片消息：显示上传云端 -->
							<view class="msg-action-group" v-if="msg.file && !msg.uploaded">
								<text class="msg-action upload-btn" @click="uploadToCOS(msg, index)">
									{{ msg.uploading ? '上传中...' : '☁️ 上传云端' }}
								</text>
							</view>
							<view class="msg-action-group" v-if="msg.file && msg.uploaded">
								<text class="msg-action uploaded">✓ 已上传</text>
							</view>
							<!-- AI 回复：复制 + 引用 + 存知识库 -->
							<view class="msg-action-group" v-if="msg.role === 'assistant'">
								<text class="msg-action" @click="copyText(msg.content)">复制</text>
								<text class="msg-action quote-btn" @click="quoteMessage(msg)">引用</text>
								<text class="msg-action" @click="saveToKnowledge(msg)">存入知识库</text>
							</view>
							<!-- 用户纯文本：引用 + 存知识库 -->
							<view class="msg-action-group" v-if="msg.role === 'user' && !msg.file">
								<text class="msg-action quote-btn" @click="quoteMessage(msg)">引用</text>
								<text class="msg-action" @click="saveToKnowledge(msg)">存入知识库</text>
							</view>
							<view class="msg-action-group pin-group">
								<text class="msg-action" @click="pinMessage(msg)">♥</text>
								<text class="msg-action danger" @click="scheduleRemoval(msg)">×</text>
							</view>
						</view>
						<!-- 知识库引用 -->
						<view class="references" v-if="msg.references && msg.references.length > 0">
							<view class="ref-label">
								<Icon name="book" size="18" />
								<text class="ref-text">参考：</text>
							</view>
							<text 
								class="ref-item" 
								v-for="(ref, idx) in msg.references" 
								:key="idx"
								@click="goKnowledge(ref.id)"
							>{{ ref.title }}</text>
						</view>
					</view>
				</view>
				
				<!-- AI 正在输入 -->
				<view class="message-item" v-if="isTyping">
					<view class="avatar">
						<Icon name="robot" size="28" />
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
			
			<!-- 底部占位 -->
			<view class="bottom-placeholder"></view>
		</view>
		
		<!-- 输入栏容器 -->
		<view class="input-container">
			<!-- 引用预览（在输入框上方） -->
			<view class="quote-preview" v-if="quotedMsg">
				<view class="quote-preview-bar"></view>
				<view class="quote-preview-content">
					<view class="quote-preview-header">
						<text class="quote-preview-role">{{ quotedMsg.role === 'assistant' ? 'AI' : '我' }}</text>
					</view>
					<text class="quote-preview-text">{{ quotedMsg.content.length > 100 ? quotedMsg.content.substring(0, 100) + '...' : quotedMsg.content }}</text>
				</view>
				<view class="quote-preview-close" @click="cancelQuote">
					<Icon name="close" size="16" />
				</view>
			</view>
			
			<!-- 文件预览（在输入框上方） -->
			<view class="file-preview" v-if="selectedFile">
				<view class="file-preview-content">
					<!-- 图片预览 -->
					<image 
						v-if="selectedFile.type === 'image'" 
						class="preview-image" 
						:src="selectedFile.path" 
						mode="aspectFill"
					/>
					<!-- 文件图标预览 -->
					<view v-else class="preview-file">
						<Icon :name="getFileIcon(selectedFile.type)" size="36" />
						<text class="preview-ext">{{ getFileExt(selectedFile.name) }}</text>
					</view>
					<text class="preview-name">{{ selectedFile.name }}</text>
				</view>
				<view class="file-remove" @click="removeFile">
					<Icon name="close" size="18" />
				</view>
			</view>
			
			<!-- 多选模式操作栏 -->
			<view class="select-action-bar" v-if="selectMode">
				<view class="select-info">
					<text class="select-count">已选 {{ selectedMsgs.length }} 条</text>
				</view>
				<view class="select-actions">
					<view class="select-action-btn" @click="forwardSelected">
						<Icon name="send" size="20" />
						<text>转发给AI</text>
					</view>
					<view class="select-action-btn" @click="saveSelectedToKnowledge">
						<Icon name="book" size="20" />
						<text>存知识库</text>
					</view>
					<view class="select-action-btn cancel" @click="exitSelectMode">
						<Icon name="close" size="20" />
						<text>取消</text>
					</view>
				</view>
			</view>
			
			<!-- 输入栏 -->
			<view class="input-bar" v-if="!selectMode">
				<view class="add-btn" @click="showAddMenu">
					<Icon name="plus" size="24" />
				</view>
				<view class="input-wrapper">
					<input 
						class="input-field"
						type="text"
						v-model="inputText"
						:placeholder="selectedFile ? '描述一下你想问的...' : inputPlaceholder"
						:adjust-position="true"
						:cursor-spacing="20"
						confirm-type="send"
						@confirm="sendMessage"
					/>
				</view>
				<view class="send-btn" :class="{ 'active': inputText.trim() || selectedFile }" @click="sendMessage">
					<Icon name="send" size="22" class="send-icon" />
				</view>
			</view>
		</view>
		
		<!-- 底部安全区 -->
		<view class="safe-bottom"></view>
		
		<!-- 历史记录侧边栏 -->
		<view class="history-mask" v-if="showHistory" @click="showHistory = false"></view>
			<view class="history-sidebar" :class="{ 'show': showHistory }">
			<view class="sidebar-header">
				<text class="sidebar-title">聊天记录</text>
				<view class="sidebar-close" @click="showHistory = false">
					<Icon name="close" size="20" />
				</view>
			</view>
			
			<scroll-view class="history-list" scroll-y>
				<view 
					class="history-item"
					:class="{ 'active': currentSessionId === item.id }"
					v-for="item in historyList" 
					:key="item.id"
					@click="loadSession(item)"
				>
					<text class="history-title">{{ item.title }}</text>
					<text class="history-time">{{ formatTime(item.updatedAt) }}</text>
					<text class="history-preview">{{ item.lastMessage }}</text>
				</view>
				
				<view class="history-empty" v-if="historyList.length === 0">
					<text>暂无历史记录</text>
				</view>
			</scroll-view>
			
			<view class="sidebar-footer">
				<view class="new-chat-btn" @click="startNewChat">
					<text class="new-chat-icon">+</text>
					<text class="new-chat-text">新建对话</text>
				</view>
			</view>
		</view>
		
		<!-- 聊天记录详情弹窗 -->
		<view class="record-detail-mask" v-if="showRecordPopup" @click="showRecordPopup = false"></view>
		<view class="record-detail-popup" :class="{ 'show': showRecordPopup }">
			<view class="popup-header">
				<text class="popup-title">{{ currentRecord.title || '聊天记录' }}</text>
				<view class="popup-close" @click="showRecordPopup = false">
					<Icon name="close" size="20" />
				</view>
			</view>
			<scroll-view class="popup-content" scroll-y>
				<view class="popup-msg" v-for="(item, idx) in currentRecord.records" :key="idx">
					<view class="popup-msg-row">
						<view class="popup-avatar" :style="{ background: item.role === 'user' ? '#07C160' : '#059669' }">
							<Icon :name="item.role === 'user' ? 'user' : 'robot'" size="18" />
						</view>
						<view class="popup-msg-main">
							<view class="popup-msg-header">
								<text class="popup-name">{{ item.name }}</text>
								<text class="popup-time">{{ item.time }}</text>
							</view>
							<view class="popup-msg-content">
								<text>{{ item.content }}</text>
							</view>
						</view>
					</view>
				</view>
			</scroll-view>
			<view class="popup-actions">
				<view class="popup-action-btn" @click="forwardRecordToAI">
					<Icon name="send" size="18" />
					<text>发给AI分析</text>
				</view>
				<view class="popup-action-btn" @click="saveRecordToKnowledge">
					<Icon name="book" size="18" />
					<text>存知识库</text>
				</view>
			</view>
		</view>
		
		<!-- 底部导航 -->
		<CustomTabBar :currentTab="0" />
	</view>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import CustomTabBar from '@/components/CustomTabBar.vue'
import { onShow, onPageScroll } from '@dcloudio/uni-app'
import { getConversations, getMessages, sendChatMessage, createConversation, deleteMessage, updateMessageFile } from '@/api/chat'
import { saveKnowledge, searchKnowledge } from '@/api/knowledge'
import { parseImage, parseFile, uploadFileToCOS } from '@/api/upload'
import { getBackgroundStyle, applyGlobalBackground } from '@/utils/theme'
import Icon from '@/components/Icon.vue'

const LAST_SESSION_KEY = 'last_session_id'
const LAST_SCROLL_PREFIX = 'last_session_scroll_'
const MODES_KEY = 'chat_modes'
const PIN_PREFIX = 'pinned_msgs_'
const REMOVE_PREFIX = 'removed_msgs_'
const AVATAR_KEY = 'custom_avatars'

const messages = ref([])
const userAvatar = ref('')
const aiAvatar = ref('')
const inputText = ref('')
const isTyping = ref(false)
const showHistory = ref(false)
const historyList = ref([])
const currentSessionId = ref('')
const searchMode = ref(false)
const webSearchMode = ref(false)

// 多选模式
const selectMode = ref(false)
const selectedMsgs = ref([])

// 引用消息
const quotedMsg = ref(null)

// 聊天记录弹窗
const showRecordPopup = ref(false)
const currentRecord = ref({ title: '', records: [] })

const currentModeTitle = computed(() => {
	const modes = []
	if (webSearchMode.value) modes.push('联网')
	if (searchMode.value) modes.push('知识库')
	if (modes.length === 0) return 'AI 知识助手'
	return modes.join('+') + '搜索'
})

const inputPlaceholder = computed(() => {
	if (webSearchMode.value && searchMode.value) return '联网+知识库搜索...'
	if (webSearchMode.value) return '联网搜索...'
	if (searchMode.value) return '搜索知识库...'
	return '输入消息...'
})

const toggleMode = () => {
	searchMode.value = !searchMode.value
	saveModes()
}

const toggleWebSearch = () => {
	webSearchMode.value = !webSearchMode.value
	saveModes()
}

// 文件上传相关
const selectedFile = ref(null)

const showAddMenu = () => {
	uni.showActionSheet({
		itemList: ['拍照', '从相册选择', '上传文档 (Word/Excel/PDF)'],
		success: (res) => {
			if (res.tapIndex === 0) {
				// 拍照
				chooseImage('camera')
			} else if (res.tapIndex === 1) {
				// 相册
				chooseImage('album')
			} else if (res.tapIndex === 2) {
				// 文档
				chooseDocument()
			}
		}
	})
}

const chooseImage = (sourceType) => {
	// #ifdef H5
	// H5 使用 input file 以获取 File 对象
	const input = document.createElement('input')
	input.type = 'file'
	input.accept = 'image/*'
	if (sourceType === 'camera') {
		input.capture = 'environment'
	}
	input.onchange = (e) => {
		const file = e.target.files[0]
		if (file) {
			selectedFile.value = {
				path: URL.createObjectURL(file),
				name: file.name,
				size: file.size,
				type: 'image',
				file: file
			}
		}
	}
	input.click()
	// #endif
	
	// #ifndef H5
	uni.chooseImage({
		count: 1,
		sourceType: [sourceType],
		success: (res) => {
			const file = res.tempFiles[0]
			selectedFile.value = {
				path: file.path,
				name: file.path.split('/').pop(),
				size: file.size,
				type: 'image'
			}
		}
	})
	// #endif
}

const chooseDocument = () => {
	// #ifdef H5
	// H5 使用 input file
	const input = document.createElement('input')
	input.type = 'file'
	input.accept = '.doc,.docx,.xls,.xlsx,.pdf'
	input.onchange = (e) => {
		const file = e.target.files[0]
		if (file) {
			selectedFile.value = {
				path: URL.createObjectURL(file),
				name: file.name,
				size: file.size,
				type: getFileType(file.name),
				file: file
			}
		}
	}
	input.click()
	// #endif
	
	// #ifdef MP-WEIXIN || APP-PLUS
	uni.chooseMessageFile({
		count: 1,
		type: 'file',
		extension: ['doc', 'docx', 'xls', 'xlsx', 'pdf'],
		success: (res) => {
			const file = res.tempFiles[0]
			selectedFile.value = {
				path: file.path,
				name: file.name,
				size: file.size,
				type: getFileType(file.name)
			}
		}
	})
	// #endif
}

const getFileType = (filename) => {
	const ext = filename.split('.').pop().toLowerCase()
	if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)) return 'image'
	if (['doc', 'docx'].includes(ext)) return 'word'
	if (['xls', 'xlsx'].includes(ext)) return 'excel'
	if (ext === 'pdf') return 'pdf'
	return 'file'
}

const isInvalidBlobUrl = (url) => {
	if (!url) return true
	// blob URL 在页面刷新后会失效
	if (url.startsWith('blob:')) return true
	return false
}

const getDisplayContent = (msg) => {
	// 如果有解析出的 displayContent（引用消息），使用它
	if (msg.displayContent !== undefined) {
		return msg.displayContent
	}
	// 如果是文件消息，去掉第一行（文件信息）
	if (msg.file) {
		return msg.content.split('\n').slice(1).join('\n')
	}
	// 普通消息
	return msg.content
}

const getFileIcon = (type) => {
	const icons = {
		'image': 'image',
		'word': 'file',
		'excel': 'chart',
		'pdf': 'file',
		'file': 'file'
	}
	return icons[type] || 'file'
}

const getFileExt = (filename) => {
	return filename.split('.').pop().toUpperCase()
}

// Markdown 转 HTML 渲染
const parseMarkdown = (text) => {
	if (!text) return ''
	
	let html = text
		// 转义 HTML 特殊字符
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		// 代码块
		.replace(/```(\w*)\n([\s\S]*?)```/g, '<div class="code-block"><pre>$2</pre></div>')
		// 行内代码
		.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
		// 标题 (### -> h3)
		.replace(/^### (.+)$/gm, '<div class="md-h3">$1</div>')
		.replace(/^## (.+)$/gm, '<div class="md-h2">$1</div>')
		.replace(/^# (.+)$/gm, '<div class="md-h1">$1</div>')
		// 粗体
		.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
		// 斜体
		.replace(/\*([^*]+)\*/g, '<em>$1</em>')
		// 分隔线
		.replace(/^---$/gm, '<div class="md-hr"></div>')
		// 列表项
		.replace(/^- (.+)$/gm, '<div class="md-li">• $1</div>')
		.replace(/^\d+\. (.+)$/gm, '<div class="md-li">$1</div>')
		// 换行
		.replace(/\n/g, '<br/>')
	
	return html
}

const removeFile = () => {
	selectedFile.value = null
}

const previewImage = (url) => {
	uni.previewImage({
		urls: [url],
		current: url
	})
}

// 格式化 AI 回复内容
const formatAIContent = (content) => {
	if (!content) return ''
	
	let html = content
		// 转义 HTML
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
	
	// 代码块 ```code```
	html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, '<pre class="code-block"><code>$2</code></pre>')
	
	// 行内代码 `code`
	html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
	
	// 粗体 **text**
	html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
	
	// 标题 ### 
	html = html.replace(/^### (.+)$/gm, '<div class="ai-h3">$1</div>')
	html = html.replace(/^## (.+)$/gm, '<div class="ai-h2">$1</div>')
	html = html.replace(/^# (.+)$/gm, '<div class="ai-h1">$1</div>')
	
	// 有序列表 1. 2. 3.
	html = html.replace(/^(\d+)\. (.+)$/gm, '<div class="ai-list-item"><span class="list-num">$1.</span> $2</div>')
	
	// 无序列表 - 或 •
	html = html.replace(/^[-•] (.+)$/gm, '<div class="ai-list-item"><span class="list-dot">•</span> $1</div>')
	
	// 换行
	html = html.replace(/\n/g, '<br>')
	
	return html
}

const pageStyle = ref(getBackgroundStyle())
let scrollSaveTimer = null

onMounted(() => {
	loadModes()
	loadAvatars()
	initChat()
	applyGlobalBackground()
})

const loadAvatars = () => {
	try {
		// 用户头像从账号设置获取
		userAvatar.value = uni.getStorageSync('customUserAvatar') || ''
		// AI头像单独设置
		const saved = uni.getStorageSync(AVATAR_KEY)
		if (saved) {
			const data = typeof saved === 'string' ? JSON.parse(saved) : saved
			aiAvatar.value = data.aiAvatar || ''
		}
	} catch (e) {}
}

onShow(() => {
	pageStyle.value = getBackgroundStyle()
	applyGlobalBackground()
	loadAvatars()
	// 如果正在输入/等待AI回复，不要重新加载（避免消息混乱）
	if (isTyping.value) return
	// 重新加载当前会话消息，确保数据一致
	if (currentSessionId.value) {
		loadSessionMessages(currentSessionId.value)
	}
})

const initChat = async () => {
	try {
		const res = await getConversations()
		historyList.value = res.data || []

		if (historyList.value.length === 0) return

		const storedId = getStoredSessionId()
		const match = storedId ? historyList.value.find(item => item.id === storedId) : null
		const target = match || historyList.value[0]

		currentSessionId.value = target.id
		setLastSessionId(target.id)
		await loadSessionMessages(target.id)
	} catch (e) {
		console.log('初始化聊天', e)
	}
}

const loadHistory = async () => {
	try {
		const res = await getConversations()
		historyList.value = res.data || []
	} catch (e) {
		historyList.value = []
	}
}

const loadSession = async (item) => {
	currentSessionId.value = item.id
	setLastSessionId(item.id)
	await loadSessionMessages(item.id)
	showHistory.value = false
}

const loadSessionMessages = async (sessionId) => {
	try {
		const res = await getMessages(sessionId, { page: 1, size: 200 })
		messages.value = applyMessageState(res.data || [], sessionId)
		setLastSessionId(sessionId)
		restoreScroll(sessionId)
	} catch (e) {
		console.error('加载消息失败', e)
	}
}

const getMsgKey = (msg) => {
	if (msg.id) return `id:${msg.id}`
	if (msg._localId) return msg._localId
	const key = `local:${Date.now()}-${Math.random().toString(16).slice(2)}`
	msg._localId = key
	return key
}

const getPinnedKey = () => `${PIN_PREFIX}${currentSessionId.value || 'temp'}`
const getRemoveKey = () => `${REMOVE_PREFIX}${currentSessionId.value || 'temp'}`

const loadPinned = () => {
	try {
		const stored = uni.getStorageSync(getPinnedKey())
		return typeof stored === 'string' ? JSON.parse(stored) : (stored || {})
	} catch (e) {
		return {}
	}
}

const savePinned = (obj) => {
	try {
		uni.setStorageSync(getPinnedKey(), obj)
	} catch (e) {}
}

const loadRemoved = () => {
	try {
		const stored = uni.getStorageSync(getRemoveKey())
		return typeof stored === 'string' ? JSON.parse(stored) : (stored || {})
	} catch (e) {
		return {}
	}
}

const saveRemoved = (obj) => {
	try {
		uni.setStorageSync(getRemoveKey(), obj)
	} catch (e) {}
}

// 解析编码的聊天记录
const parseChatRecords = (msg) => {
	if (msg.content && msg.content.startsWith('[CHAT_RECORDS]')) {
		try {
			const jsonStr = msg.content.substring('[CHAT_RECORDS]'.length)
			msg.chatRecords = JSON.parse(jsonStr)
		} catch (e) {
			console.error('解析聊天记录失败:', e)
		}
	}
	return msg
}

// 过滤掉重复的转发消息（AI分析请求）
const filterDuplicateRecords = (list) => {
	return list.filter(msg => {
		// 跳过旧格式的转发消息（[转发的聊天记录]）
		if (msg.content && msg.content.startsWith('[转发的聊天记录]')) {
			return false
		}
		return true
	})
}

const applyMessageState = (list, sessionId) => {
	const removed = loadRemoved()
	const pinned = loadPinned()
	const now = Date.now()
	let changed = false
	const filtered = filterDuplicateRecords(list || []).filter((msg) => {
		const key = getMsgKey(msg)
		if (removed[key]) {
			if (removed[key] <= now) {
				delete removed[key]
				changed = true
			}
			return false
		}
		return true
	}).map(parseChatRecords) // 解析聊天记录

	// 清理过期删除标记
	if (changed) saveRemoved(removed)

	// 补充常显消息
	const existingKeys = new Set(filtered.map(m => getMsgKey(m)))
	Object.entries(pinned).forEach(([key, val]) => {
		if (removed[key]) return
		if (!existingKeys.has(key)) {
			const msg = { ...(val || {}) }
			msg._localId = key
			filtered.push(msg)
		}
	})

	// 按消息ID排序（ID越大越新），确保消息顺序正确
	// 没有 id 的本地消息放到最后（保持新增顺序）
	filtered.sort((a, b) => {
		// 如果都有 id，按 id 排序
		if (a.id && b.id) return a.id - b.id
		// 如果只有一个有 id，有 id 的在前
		if (a.id && !b.id) return -1
		if (!a.id && b.id) return 1
		// 都没有 id，保持原顺序
		return 0
	})

	// 恢复文件信息和引用信息（从数据库加载的消息）
	filtered.forEach(msg => {
		if (msg.fileUrl && !msg.file) {
			msg.file = {
				path: msg.fileUrl,
				cosUrl: msg.fileUrl,
				type: msg.fileType || 'image',
				name: msg.content?.match(/\[(图片|文件)\]\s*([^\n]+)/)?.[2] || '文件'
			}
			msg.uploaded = true
		}
		
		// 解析引用信息
		if (msg.content && !msg.quote) {
			const quoteMatch = msg.content.match(/\[引用(AI|用户)的消息\]\n([\s\S]*?)\n\[引用结束\]\n\n([\s\S]*)/)
			if (quoteMatch) {
				msg.quote = {
					role: quoteMatch[1] === 'AI' ? 'assistant' : 'user',
					content: quoteMatch[2]
				}
				// 提取引用后的实际内容
				msg.displayContent = quoteMatch[3]
			}
		}
	})

	return filtered
}

const startNewChat = async () => {
	messages.value = []
	currentSessionId.value = ''
	showHistory.value = false
}

const sendMessage = async () => {
	const text = inputText.value.trim()
	const file = selectedFile.value
	const quote = quotedMsg.value
	
	// 必须有文字或文件
	if (!text && !file) return
	if (isTyping.value) return
	
	// 构建用户消息显示
	let userContent = text
	if (file) {
		userContent = file.type === 'image' 
			? `[图片] ${file.name}${text ? '\n' + text : ''}`
			: `[文件] ${file.name}${text ? '\n' + text : ''}`
	}
	
	// 添加用户消息（包含引用信息）
	const userMsg = {
		role: 'user',
		content: userContent,
		file: file,  // 保存文件信息用于显示
		quote: quote  // 保存引用信息
	}
	getMsgKey(userMsg)
	messages.value.push(userMsg)
	
	// 清空输入和引用
	inputText.value = ''
	const currentFile = file
	const currentQuote = quote
	selectedFile.value = null
	quotedMsg.value = null
	scrollToBottom()
	
	// 显示 AI 正在输入
	isTyping.value = true
	
	try {
		// 如果有图片，调用图片解析 API
		if (currentFile && currentFile.type === 'image') {
			const prompt = text || '请描述这张图片的内容'
			
			try {
				// H5 用 File 对象，小程序用 path
				const fileData = currentFile.file || currentFile.path
				const res = await parseImage(fileData, prompt)
				isTyping.value = false
				
				const aiContent = res.data.content
				const aiMsg = {
					role: 'assistant',
					content: aiContent,
					references: []
				}
				getMsgKey(aiMsg)
				messages.value.push(aiMsg)
				
				// 保存到后端对话历史（用户消息和AI回复分开保存）
				try {
					const saveRes = await sendChatMessage({
						conversationId: currentSessionId.value || null,
						message: `[图片] ${currentFile.name}\n${prompt}`,
						aiReply: aiContent,
						saveOnly: true
					})
					if (saveRes.data?.conversationId) {
						currentSessionId.value = saveRes.data.conversationId
						setLastSessionId(saveRes.data.conversationId)
					}
					// 记录消息ID，用于后续上传时更新
					const userMsgIndex = messages.value.length - 2
					if (userMsgIndex >= 0 && messages.value[userMsgIndex].file) {
						messages.value[userMsgIndex].dbMessageId = saveRes.data?.userMessageId
					}
				} catch (e) { console.error('保存文件上下文失败:', e) }
			} catch (err) {
				isTyping.value = false
				const aiMsg = {
					role: 'assistant',
					content: `图片解析失败: ${err.message || '未知错误'}`
				}
				getMsgKey(aiMsg)
				messages.value.push(aiMsg)
			}
			
			scrollToBottom()
			return
		}
		
		// 如果有其他文件（PDF/Word/Excel/PPT）
		if (currentFile && currentFile.type !== 'image') {
			const prompt = text || '请描述这个文件的内容'
			
			try {
				// H5 用 File 对象，小程序用 path
				const fileData = currentFile.file || currentFile.path
				const res = await parseFile(fileData, prompt)
				isTyping.value = false
				
				const aiContent = res.data.content
				const aiMsg = {
					role: 'assistant',
					content: aiContent,
					references: []
				}
				getMsgKey(aiMsg)
				messages.value.push(aiMsg)
				
				// 保存到后端对话历史（用户消息和AI回复分开保存）
				try {
					const res = await sendChatMessage({
						conversationId: currentSessionId.value || null,
						message: `[文件] ${currentFile.name}\n${prompt}`,
						aiReply: aiContent,
						saveOnly: true
					})
					if (res.data?.conversationId) {
						currentSessionId.value = res.data.conversationId
						setLastSessionId(res.data.conversationId)
					}
				} catch (e) { console.error('保存文件上下文失败:', e) }
			} catch (err) {
				isTyping.value = false
				const aiMsg = {
					role: 'assistant',
					content: `文档解析失败: ${err.message || '未知错误'}`
				}
				getMsgKey(aiMsg)
				messages.value.push(aiMsg)
			}
			
			scrollToBottom()
			return
		}
		
		if (searchMode.value && !webSearchMode.value) {
			// 仅知识库搜索模式：直接搜索知识库
			const res = await searchKnowledge({ query: text })
			isTyping.value = false
			
			if (res.data && res.data.length > 0) {
				let reply = '找到以下内容：\n\n'
				res.data.forEach((item, idx) => {
					reply += `${idx + 1}. ${item.title}\n${item.content}\n\n`
				})
				const aiMsg = {
					role: 'assistant',
					content: reply.trim()
				}
				getMsgKey(aiMsg)
				messages.value.push(aiMsg)
			} else {
				const emptyMsg = {
					role: 'assistant',
					content: '未找到相关内容'
				}
				getMsgKey(emptyMsg)
				messages.value.push(emptyMsg)
			}
		} else {
			// AI 对话（可选联网搜索）
			// 如果有引用，把引用内容加到消息前面
			let messageToSend = text
			if (currentQuote) {
				const quoteRole = currentQuote.role === 'assistant' ? 'AI' : '用户'
				const quoteContent = currentQuote.content.length > 500 
					? currentQuote.content.substring(0, 500) + '...' 
					: currentQuote.content
				messageToSend = `[引用${quoteRole}的消息]\n${quoteContent}\n[引用结束]\n\n${text}`
			}
			
			const res = await sendChatMessage({
				conversationId: currentSessionId.value || null,
				message: messageToSend,
				webSearch: webSearchMode.value
			})
			
			isTyping.value = false
			
			// 添加 AI 回复
			const aiMsg = {
				role: 'assistant',
				content: res.data.reply,
				references: res.data.references || []
			}
			getMsgKey(aiMsg)
			messages.value.push(aiMsg)
			
			// 更新会话 ID
			if (res.data.conversationId) {
				currentSessionId.value = res.data.conversationId
				setLastSessionId(res.data.conversationId)
			}
			
			// 刷新历史列表
			loadHistory()
		}
	} catch (e) {
		isTyping.value = false
		const errMsg = {
			role: 'assistant',
			content: '抱歉，网络异常，请稍后再试。'
		}
		getMsgKey(errMsg)
		messages.value.push(errMsg)
	}
	
	scrollToBottom()
}

const quickAsk = (text) => {
	inputText.value = text
	sendMessage()
}

const clearChat = () => {
	uni.showModal({
		title: '清空对话',
		content: '确定要清空当前对话吗？',
		success: (res) => {
			if (res.confirm) {
				messages.value = []
				currentSessionId.value = ''
			}
		}
	})
}

// 引用消息
const quoteMessage = (msg) => {
	quotedMsg.value = {
		role: msg.role,
		content: msg.content
	}
	uni.showToast({ title: '已引用', icon: 'none', duration: 1000 })
}

const cancelQuote = () => {
	quotedMsg.value = null
}

const scrollToQuotedMsg = (quote) => {
	// 点击引用时的操作（可扩展：滚动到原消息）
	uni.showToast({ 
		title: `${quote.role === 'assistant' ? 'AI' : '用户'}的消息`, 
		icon: 'none',
		duration: 1000 
	})
}

const copyText = (text) => {
	uni.setClipboardData({
		data: text,
		success: () => {
			uni.showToast({ title: '已复制' })
		}
	})
}

// ========== 多选模式功能 ==========
const onMsgLongPress = (index) => {
	if (!selectMode.value) {
		selectMode.value = true
		selectedMsgs.value = [index]
		uni.vibrateShort()
	}
}

const onMsgClick = (index) => {
	if (selectMode.value) {
		toggleSelect(index)
	}
}

const toggleSelect = (index) => {
	const idx = selectedMsgs.value.indexOf(index)
	if (idx === -1) {
		selectedMsgs.value.push(index)
	} else {
		selectedMsgs.value.splice(idx, 1)
	}
}

const exitSelectMode = () => {
	selectMode.value = false
	selectedMsgs.value = []
}

// 转发选中消息 - 创建聊天记录卡片
const forwardSelected = async () => {
	if (selectedMsgs.value.length === 0) {
		uni.showToast({ title: '请选择消息', icon: 'none' })
		return
	}
	
	// 按顺序排列选中的消息
	const sortedIndexes = [...selectedMsgs.value].sort((a, b) => a - b)
	const now = new Date()
	const timeStr = `${now.getMonth() + 1}-${now.getDate()} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
	
	// 构建聊天记录数据
	const chatRecords = sortedIndexes.map(i => {
		const msg = messages.value[i]
		return {
			role: msg.role,
			name: msg.role === 'user' ? '我' : 'AI助手',
			content: msg.content,
			time: timeStr
		}
	})
	
	// 退出多选模式
	exitSelectMode()
	
	// 创建聊天记录卡片消息（将数据编码到 content 中以便持久化）
	const encodedContent = `[CHAT_RECORDS]${JSON.stringify(chatRecords)}`
	const recordMsg = {
		role: 'user',
		content: encodedContent,
		chatRecords: chatRecords
	}
	getMsgKey(recordMsg)
	messages.value.push(recordMsg)
	scrollToBottom()
	
	// 保存到后端
	try {
		await sendChatMessage({
			conversationId: currentSessionId.value || null,
			message: encodedContent,
			saveOnly: true
		})
	} catch (e) {
		console.error('保存聊天记录失败:', e)
	}
	
	// 显示详情弹窗
	currentRecord.value = {
		title: `${chatRecords.length} 条聊天记录`,
		records: chatRecords
	}
	showRecordPopup.value = true
}

// 显示聊天记录详情
const showRecordDetail = (msg) => {
	if (msg.chatRecords) {
		currentRecord.value = {
			title: `${msg.chatRecords.length} 条聊天记录`,
			records: msg.chatRecords
		}
		showRecordPopup.value = true
	}
}

// 从弹窗发送给 AI 分析
const forwardRecordToAI = async () => {
	if (!currentRecord.value.records.length) return
	
	showRecordPopup.value = false
	
	// 构建文本内容
	const content = currentRecord.value.records.map(r => 
		`【${r.name}】${r.content}`
	).join('\n\n')
	
	// 发送给 AI
	isTyping.value = true
	try {
		const res = await sendChatMessage({
			conversationId: currentSessionId.value || null,
			message: `[转发的聊天记录]\n${content}\n\n请帮我分析或总结这段对话`
		})
		isTyping.value = false
		
		const aiMsg = {
			role: 'assistant',
			content: res.data.reply,
			references: res.data.references || []
		}
		getMsgKey(aiMsg)
		messages.value.push(aiMsg)
		
		if (res.data.conversationId) {
			currentSessionId.value = res.data.conversationId
			setLastSessionId(res.data.conversationId)
		}
	} catch (e) {
		isTyping.value = false
		const errMsg = { role: 'assistant', content: '分析失败，请重试' }
		getMsgKey(errMsg)
		messages.value.push(errMsg)
	}
	scrollToBottom()
}

// 从弹窗保存到知识库
const saveRecordToKnowledge = async () => {
	if (!currentRecord.value.records.length) return
	
	const content = currentRecord.value.records.map(r => 
		`【${r.name}】${r.content}`
	).join('\n\n')
	
	try {
		await saveKnowledge({
			title: `聊天记录 ${new Date().toLocaleDateString()}`,
			content: content,
			source: 'chat',
			tags: ['聊天记录']
		})
		uni.showToast({ title: '已存入知识库' })
		showRecordPopup.value = false
	} catch (e) {
		uni.showToast({ title: '保存失败', icon: 'none' })
	}
}

// 保存选中消息到知识库
const saveSelectedToKnowledge = async () => {
	if (selectedMsgs.value.length === 0) {
		uni.showToast({ title: '请选择消息', icon: 'none' })
		return
	}
	
	const sortedIndexes = [...selectedMsgs.value].sort((a, b) => a - b)
	const selectedContent = sortedIndexes.map(i => {
		const msg = messages.value[i]
		const role = msg.role === 'user' ? '用户' : 'AI'
		return `【${role}】${msg.content}`
	}).join('\n\n')
	
	uni.showModal({
		title: '存入知识库',
		content: `确定将选中的 ${selectedMsgs.value.length} 条消息存入知识库吗？`,
		success: async (res) => {
			if (res.confirm) {
				try {
					await saveKnowledge({
						title: `聊天记录 ${new Date().toLocaleDateString()}`,
						content: selectedContent,
						source: 'chat',
						tags: ['聊天记录']
					})
					uni.showToast({ title: '已存入知识库' })
					exitSelectMode()
				} catch (e) {
					uni.showToast({ title: '保存失败', icon: 'none' })
				}
			}
		}
	})
}

const saveToKnowledge = async (msg) => {
	uni.showModal({
		title: '存入知识库',
		content: '确定将此回复存入知识库吗？',
		success: async (res) => {
			if (res.confirm) {
				try {
					await saveKnowledge({
						title: msg.content.substring(0, 30) + '...',
						content: msg.content,
						source: 'chat'
					})
					uni.showToast({ title: '已存入知识库' })
				} catch (e) {
					uni.showToast({ title: '保存成功（离线）' })
				}
			}
		}
	})
}

// 上传文件到腾讯云 COS
const uploadToCOS = async (msg, index) => {
	if (!msg.file || msg.uploading || msg.uploaded) return
	
	// 标记上传中
	messages.value[index].uploading = true
	
	try {
		// 获取文件数据（base64）
		let fileData = ''
		const filePath = msg.file.path
		
		// #ifdef H5
		// H5: 从 blob URL 读取数据
		const response = await fetch(filePath)
		const blob = await response.blob()
		fileData = await new Promise((resolve) => {
			const reader = new FileReader()
			reader.onloadend = () => {
				const base64 = reader.result.split(',')[1]
				resolve(base64)
			}
			reader.readAsDataURL(blob)
		})
		// #endif
		
		// #ifndef H5
		// 小程序: 使用 uni.getFileSystemManager
		const fs = uni.getFileSystemManager()
		const base64Data = fs.readFileSync(filePath, 'base64')
		fileData = base64Data
		// #endif
		
		// 调用上传 API
		const res = await uploadFileToCOS(
			fileData,
			msg.file.name,
			msg.file.type,
			msg.content
		)
		
		const cosUrl = res.data.url
		messages.value[index].uploaded = true
		messages.value[index].file.cosUrl = cosUrl
		
		// 更新数据库中的消息，保存文件URL（这样刷新后图片还能显示）
		const msgId = msg.id || msg.dbMessageId
		if (msgId) {
			try {
				await updateMessageFile(msgId, cosUrl, msg.file.type || 'image')
			} catch (e) {
				console.error('更新消息文件URL失败:', e)
			}
		}
		
		uni.showToast({ title: '上传成功', icon: 'success' })
	} catch (e) {
		console.error('上传失败:', e)
		uni.showToast({ title: e.message || '上传失败', icon: 'none' })
	} finally {
		messages.value[index].uploading = false
	}
}

const goKnowledge = (id) => {
	uni.navigateTo({
		url: `/pages/knowledge/detail?id=${id}`
	})
}

const pinMessage = (msg) => {
	const key = getMsgKey(msg)
	const pinned = loadPinned()
	if (!pinned[key]) {
		pinned[key] = {
			...msg,
			_localId: key
		}
		savePinned(pinned)
	}
	uni.showToast({ title: '已标记常显', icon: 'none' })
}

const scheduleRemoval = async (msg) => {
	const key = getMsgKey(msg)
	
	// 如果消息有 id，从数据库真正删除
	if (msg.id) {
		try {
			await deleteMessage(msg.id)
		} catch (e) {
			console.error('删除消息失败:', e)
		}
	}
	
	// 清理本地状态
	const removed = loadRemoved()
	removed[key] = Date.now() + 3 * 24 * 60 * 60 * 1000
	saveRemoved(removed)
	const pinned = loadPinned()
	if (pinned[key]) {
		delete pinned[key]
		savePinned(pinned)
	}
	messages.value = messages.value.filter(m => getMsgKey(m) !== key)
	uni.showToast({ title: '已删除', icon: 'none' })
}

const scrollToBottom = () => {
	nextTick(() => {
		if (currentSessionId.value) {
			setLastScroll(currentSessionId.value, 99999)
		}
		uni.pageScrollTo({
			scrollTop: 99999,
			duration: 0
		})
	})
}

const formatTime = (time) => {
	if (!time) return ''
	const date = new Date(time)
	const now = new Date()
	const diff = now.getTime() - date.getTime()
	
	if (diff < 86400000) {
		return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
	} else if (diff < 172800000) {
		return '昨天'
	} else {
		return `${date.getMonth() + 1}/${date.getDate()}`
	}
}

const getStoredSessionId = () => {
	try {
		return uni.getStorageSync(LAST_SESSION_KEY) || ''
	} catch (e) {
		return ''
	}
}

const setLastSessionId = (id) => {
	try {
		uni.setStorageSync(LAST_SESSION_KEY, id || '')
	} catch (e) {}
}

function loadModes() {
	try {
		const stored = uni.getStorageSync(MODES_KEY)
		if (stored) {
			const data = typeof stored === 'string' ? JSON.parse(stored) : stored
			searchMode.value = !!data.searchMode
			webSearchMode.value = !!data.webSearchMode
		}
	} catch (e) {}
}

function saveModes() {
	try {
		uni.setStorageSync(MODES_KEY, {
			searchMode: searchMode.value,
			webSearchMode: webSearchMode.value
		})
	} catch (e) {}
}

const getLastScroll = (sessionId) => {
	if (!sessionId) return 0
	try {
		const val = uni.getStorageSync(LAST_SCROLL_PREFIX + sessionId)
		return typeof val === 'number' ? val : Number(val) || 0
	} catch (e) {
		return 0
	}
}

const setLastScroll = (sessionId, val) => {
	if (!sessionId) return
	try {
		uni.setStorageSync(LAST_SCROLL_PREFIX + sessionId, val || 0)
	} catch (e) {}
}

const restoreScroll = (sessionId) => {
	const saved = getLastScroll(sessionId)
	nextTick(() => {
		uni.pageScrollTo({
			scrollTop: saved || 99999,
			duration: 0
		})
	})
}

onPageScroll((e) => {
	if (!currentSessionId.value) return
	if (scrollSaveTimer) return
	scrollSaveTimer = setTimeout(() => {
		setLastScroll(currentSessionId.value, e.scrollTop)
		scrollSaveTimer = null
	}, 200)
})
</script>

<style scoped>
.chat-page {
	min-height: 100vh;
	background-color: transparent;
	box-sizing: border-box;
	padding-top: 100rpx;
	padding-bottom: 220rpx;
	overflow-y: auto;
	-webkit-overflow-scrolling: touch;
}

/* 顶部栏（固定） */
.header-fixed {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 20rpx 32rpx;
	background-color: #fff;
	border-bottom: 1rpx solid #eee;
	z-index: 100;
}

.header-left, .header-right {
	width: 60rpx;
	height: 60rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.icon-btn {
	color: #333;
}

.header-title {
	font-size: 34rpx;
	font-weight: 600;
	color: #333;
}

.mode-switch {
	width: 60rpx;
	height: 60rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 50%;
	background: #f5f5f5;
	color: #666;
}

.mode-switch.active {
	background: #07C160;
	color: #fff;
}

.mode-tip {
	position: fixed;
	top: 100rpx;
	left: 0;
	right: 0;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8rpx;
	padding: 16rpx;
	background: #E8F5E9;
	color: #07C160;
	font-size: 24rpx;
	z-index: 99;
}

.mode-tip.web {
	background: #E3F2FD;
	color: #1976D2;
}

.mode-tip.combined {
	background: linear-gradient(90deg, #E3F2FD, #E8F5E9);
	color: #333;
}

/* 消息列表 */
.message-list {
	padding: 24rpx;
}

/* 欢迎界面 */
.welcome {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 80rpx 40rpx;
}

.welcome-icon {
	font-size: 120rpx;
	margin-bottom: 24rpx;
}

.welcome-title {
	font-size: 40rpx;
	font-weight: 600;
	color: #333;
	margin-bottom: 16rpx;
}

.welcome-desc {
	font-size: 28rpx;
	color: #666;
	text-align: center;
	margin-bottom: 48rpx;
}

.quick-actions {
	display: flex;
	flex-wrap: wrap;
	justify-content: center;
	gap: 24rpx;
}

.action-item {
	display: flex;
	align-items: center;
	padding: 20rpx 32rpx;
	background-color: #fff;
	border-radius: 40rpx;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
}

.action-icon {
	font-size: 32rpx;
	margin-right: 12rpx;
}

.action-text {
	font-size: 28rpx;
	color: #333;
}

/* 消息气泡 */
.message-wrapper {
	display: flex;
	flex-direction: column;
}

.message-item {
	display: flex;
	margin-bottom: 32rpx;
}

.message-item.is-user {
	flex-direction: row-reverse;
}

.avatar {
	width: 76rpx;
	height: 76rpx;
	border-radius: 20rpx;
	background: linear-gradient(135deg, #059669 0%, #047857 100%);
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
	box-shadow: 0 4rpx 12rpx rgba(102, 126, 234, 0.3);
	overflow: hidden;
}

.avatar.user-avatar {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	box-shadow: 0 4rpx 12rpx rgba(7, 193, 96, 0.3);
}

.avatar.ai-avatar {
	background: linear-gradient(135deg, #059669 0%, #047857 100%);
}

.is-user .avatar {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	box-shadow: 0 4rpx 12rpx rgba(7, 193, 96, 0.3);
}

.avatar-img {
	width: 76rpx;
	height: 76rpx;
	border-radius: 20rpx;
}

.avatar-emoji {
	font-size: 40rpx;
}

/* 多选模式样式 */
.message-item.is-selected {
	background-color: rgba(7, 193, 96, 0.1);
	border-radius: 16rpx;
	margin-left: -16rpx;
	margin-right: -16rpx;
	padding: 16rpx;
}

.select-checkbox {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 60rpx;
	flex-shrink: 0;
}

.checkbox {
	width: 44rpx;
	height: 44rpx;
	border-radius: 50%;
	border: 3rpx solid #ccc;
	display: flex;
	align-items: center;
	justify-content: center;
	background: #fff;
	transition: all 0.2s;
}

.checkbox.checked {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	border-color: #07C160;
	color: #fff;
	font-size: 24rpx;
	font-weight: bold;
}

.avatar-icon {
	font-size: 36rpx;
}

.bubble-wrapper {
	max-width: 75%;
	margin: 0 16rpx;
}

.bubble {
	padding: 24rpx 28rpx;
	background-color: #fff;
	border-radius: 4rpx 20rpx 20rpx 20rpx;
	box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.user-bubble {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	border-radius: 20rpx 4rpx 20rpx 20rpx;
}

.ai-bubble {
	background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
	border: 1rpx solid #e8e8e8;
}

.bubble-text {
	font-size: 30rpx;
	color: #333;
	line-height: 1.7;
	white-space: pre-wrap;
	word-break: break-all;
}

.user-bubble .bubble-text {
	color: #fff;
}

/* AI 回复内容格式化 */
.ai-content {
	font-size: 30rpx;
	color: #333;
	line-height: 1.8;
	word-break: break-all;
}

/* Markdown 渲染样式 */
.markdown-content {
	font-size: 30rpx;
	color: #333;
	line-height: 1.8;
}

:deep(.md-h1) {
	font-size: 40rpx;
	font-weight: bold;
	color: #1a1a1a;
	margin: 24rpx 0 16rpx;
	padding-bottom: 12rpx;
	border-bottom: 2rpx solid #e0e0e0;
}

:deep(.md-h2) {
	font-size: 36rpx;
	font-weight: bold;
	color: #2a2a2a;
	margin: 20rpx 0 12rpx;
}

:deep(.md-h3) {
	font-size: 32rpx;
	font-weight: bold;
	color: #3a3a3a;
	margin: 16rpx 0 10rpx;
}

:deep(strong) {
	font-weight: bold;
	color: #1a1a1a;
}

:deep(em) {
	font-style: italic;
	color: #555;
}

:deep(.md-hr) {
	height: 2rpx;
	background: linear-gradient(90deg, transparent, #ddd, transparent);
	margin: 20rpx 0;
}

:deep(.md-li) {
	padding-left: 8rpx;
	margin: 8rpx 0;
	line-height: 1.6;
}

:deep(.code-block) {
	background: #f6f8fa;
	border-radius: 12rpx;
	padding: 20rpx;
	margin: 16rpx 0;
	overflow-x: auto;
}

:deep(.code-block pre) {
	font-family: 'Monaco', 'Menlo', monospace;
	font-size: 26rpx;
	color: #24292e;
	white-space: pre-wrap;
	word-break: break-all;
}

:deep(.inline-code) {
	background: #f0f0f0;
	padding: 4rpx 10rpx;
	border-radius: 6rpx;
	font-family: 'Monaco', 'Menlo', monospace;
	font-size: 26rpx;
	color: #e83e8c;
}

/* 消息中的文件/图片 */
.msg-file {
	margin-bottom: 12rpx;
}

.msg-image {
	max-width: 100%;
	border-radius: 12rpx;
}

.msg-file-icon {
	width: 120rpx;
	height: 120rpx;
	background: rgba(255, 255, 255, 0.2);
	border-radius: 12rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	color: #fff;
}

.user-bubble .msg-file-icon {
	background: rgba(255, 255, 255, 0.3);
}

.msg-file-ext {
	font-size: 20rpx;
	font-weight: 600;
	margin-top: 4rpx;
}

.msg-actions {
	display: flex;
	justify-content: space-between;
	margin-top: 12rpx;
	align-items: center;
}

.msg-action-group {
	display: flex;
	gap: 24rpx;
}

.pin-group {
	margin-left: auto;
}

.msg-action {
	font-size: 24rpx;
	color: #07C160;
}

.msg-action.danger {
	color: #d54941;
}

.msg-action.upload-btn {
	background: linear-gradient(135deg, #1890ff, #36cfc9);
	color: #fff;
	padding: 8rpx 20rpx;
	border-radius: 20rpx;
	font-size: 22rpx;
}

.msg-action.uploaded {
	color: #52c41a;
	font-size: 22rpx;
}

.references {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	margin-top: 16rpx;
	padding: 12rpx 16rpx;
	background-color: #f8f8f8;
	border-radius: 12rpx;
}

.ref-label {
	display: flex;
	align-items: center;
	gap: 8rpx;
	font-size: 24rpx;
	color: #666;
}

.ref-item {
	font-size: 24rpx;
	color: #07C160;
	margin-right: 16rpx;
	text-decoration: underline;
}

/* 输入中动画 */
.typing {
	padding: 24rpx 28rpx;
	background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
}

.typing-dots {
	display: flex;
	align-items: center;
	gap: 10rpx;
}

.dot {
	width: 16rpx;
	height: 16rpx;
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	border-radius: 50%;
	animation: typing 1.4s infinite;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
	0%, 60%, 100% { transform: translateY(0) scale(1); opacity: 0.5; }
	30% { transform: translateY(-10rpx) scale(1.2); opacity: 1; }
}

.bottom-placeholder {
	height: 20rpx;
}

/* 输入栏容器（固定） */
.input-container {
	position: fixed;
	bottom: 100rpx;
	left: 0;
	right: 0;
	background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
	border-top: none;
	box-shadow: 0 -8rpx 32rpx rgba(0, 0, 0, 0.08);
	z-index: 100;
}

/* 引用预览（输入框上方） */
.quote-preview {
	display: flex;
	align-items: stretch;
	padding: 16rpx 24rpx;
	margin: 16rpx 24rpx 0;
	background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%);
	border-radius: 12rpx;
}

.quote-preview-bar {
	width: 6rpx;
	background: linear-gradient(180deg, #07C160 0%, #06AD56 100%);
	border-radius: 3rpx;
	margin-right: 16rpx;
}

.quote-preview-content {
	flex: 1;
	min-width: 0;
}

.quote-preview-header {
	margin-bottom: 6rpx;
}

.quote-preview-role {
	font-size: 22rpx;
	color: #07C160;
	font-weight: 600;
}

.quote-preview-text {
	font-size: 24rpx;
	color: #666;
	line-height: 1.4;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
}

.quote-preview-close {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 48rpx;
	height: 48rpx;
	margin-left: 12rpx;
	color: #999;
}

/* 消息中的引用显示 */
.msg-quote {
	display: flex;
	align-items: stretch;
	padding: 12rpx 16rpx;
	margin-bottom: 12rpx;
	background: rgba(0, 0, 0, 0.05);
	border-radius: 8rpx;
	cursor: pointer;
}

.user-bubble .msg-quote {
	background: rgba(255, 255, 255, 0.3);
}

.msg-quote-bar {
	width: 4rpx;
	background: #07C160;
	border-radius: 2rpx;
	margin-right: 12rpx;
}

.user-bubble .msg-quote-bar {
	background: rgba(255, 255, 255, 0.8);
}

.msg-quote-content {
	flex: 1;
	min-width: 0;
}

.msg-quote-role {
	font-size: 20rpx;
	color: #07C160;
	font-weight: 600;
	display: block;
	margin-bottom: 4rpx;
}

.user-bubble .msg-quote-role {
	color: rgba(255, 255, 255, 0.9);
}

.msg-quote-text {
	font-size: 22rpx;
	color: #666;
	line-height: 1.3;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
}

.user-bubble .msg-quote-text {
	color: rgba(255, 255, 255, 0.85);
}

/* 引用按钮样式 */
.quote-btn {
	color: #07C160 !important;
}

/* 文件预览 */
.file-preview {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 20rpx 24rpx;
	margin: 16rpx 24rpx 0;
	background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
	border: 2rpx solid #c8e6c9;
	border-radius: 16rpx;
}

.file-preview-content {
	display: flex;
	align-items: center;
	gap: 16rpx;
	flex: 1;
	min-width: 0;
}

.preview-image {
	width: 80rpx;
	height: 80rpx;
	border-radius: 8rpx;
	object-fit: cover;
}

.preview-file {
	width: 80rpx;
	height: 80rpx;
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	border-radius: 8rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	color: #fff;
}

.preview-ext {
	font-size: 18rpx;
	font-weight: 600;
	margin-top: 4rpx;
}

.preview-name {
	font-size: 26rpx;
	color: #333;
	flex: 1;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.file-remove {
	width: 48rpx;
	height: 48rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	background: rgba(0, 0, 0, 0.1);
	border-radius: 50%;
	color: #666;
	flex-shrink: 0;
	transition: all 0.2s;
}

.file-remove:active {
	background: rgba(0, 0, 0, 0.2);
	transform: scale(0.9);
}

/* 输入栏 */
.input-bar {
	display: flex;
	align-items: center;
	padding: 20rpx 24rpx 24rpx;
}

.add-btn {
	width: 76rpx;
	height: 76rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	color: #fff;
	border-radius: 50%;
	margin-right: 16rpx;
	box-shadow: 0 4rpx 12rpx rgba(7, 193, 96, 0.3);
}

.input-wrapper {
	flex: 1;
	min-height: 80rpx;
	background: #ffffff;
	border: 2rpx solid #e8e8e8;
	border-radius: 40rpx;
	padding: 18rpx 28rpx;
	margin-right: 16rpx;
	display: flex;
	align-items: center;
	box-shadow: inset 0 2rpx 6rpx rgba(0, 0, 0, 0.03);
	transition: all 0.2s;
}

.input-wrapper:focus-within {
	border-color: #07C160;
	box-shadow: 0 0 0 4rpx rgba(7, 193, 96, 0.1);
}

.input-field {
	flex: 1;
	font-size: 30rpx;
	background-color: transparent;
}

.send-btn {
	width: 76rpx;
	height: 76rpx;
	background: #e8e8e8;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.2s;
}

.send-btn.active {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	box-shadow: 0 4rpx 12rpx rgba(7, 193, 96, 0.3);
	transform: scale(1.05);
}

.send-icon {
	font-size: 32rpx;
	color: #fff;
}

.safe-bottom {
	display: none;
}

/* 历史记录侧边栏 */
.history-mask {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background-color: rgba(0, 0, 0, 0.5);
	z-index: 100;
}

.history-sidebar {
	position: fixed;
	top: 0;
	left: -80%;
	width: 80%;
	height: 100%;
	background-color: #fff;
	z-index: 101;
	display: flex;
	flex-direction: column;
	transition: left 0.3s ease;
}

.history-sidebar.show {
	left: 0;
}

.sidebar-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 48rpx 32rpx 24rpx;
	border-bottom: 1rpx solid #eee;
}

.sidebar-title {
	font-size: 34rpx;
	font-weight: 600;
	color: #333;
}

.sidebar-close {
	font-size: 40rpx;
	color: #999;
}

.history-list {
	flex: 1;
	min-height: 0;
	overflow-y: auto;
	-webkit-overflow-scrolling: touch;
}

.history-item {
	padding: 24rpx 32rpx;
	border-bottom: 1rpx solid #f5f5f5;
}

.history-item.active {
	background-color: #e8f5e9;
}

.history-title {
	font-size: 30rpx;
	color: #333;
	font-weight: 500;
	display: block;
	margin-bottom: 8rpx;
}

.history-time {
	font-size: 24rpx;
	color: #999;
	display: block;
	margin-bottom: 8rpx;
}

.history-preview {
	font-size: 26rpx;
	color: #666;
	display: -webkit-box;
	-webkit-line-clamp: 1;
	-webkit-box-orient: vertical;
	overflow: hidden;
}

.history-empty {
	display: flex;
	justify-content: center;
	padding: 80rpx;
	color: #999;
	font-size: 28rpx;
}

.sidebar-footer {
	padding: 24rpx 32rpx;
	border-top: 1rpx solid #eee;
}

.new-chat-btn {
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 24rpx;
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	border-radius: 12rpx;
}

.new-chat-icon {
	font-size: 32rpx;
	color: #fff;
	margin-right: 8rpx;
}

.new-chat-text {
	font-size: 30rpx;
	color: #fff;
}
</style>

<!-- AI 内容格式化样式（不带 scoped，v-html 需要） -->
<style>
.ai-content .ai-h1 {
	font-size: 36rpx;
	font-weight: 700;
	color: #1a1a1a;
	margin: 24rpx 0 16rpx;
	padding-bottom: 12rpx;
	border-bottom: 2rpx solid #e8e8e8;
}

.ai-content .ai-h2 {
	font-size: 34rpx;
	font-weight: 600;
	color: #1a1a1a;
	margin: 20rpx 0 12rpx;
}

.ai-content .ai-h3 {
	font-size: 32rpx;
	font-weight: 600;
	color: #333;
	margin: 16rpx 0 10rpx;
}

.ai-content .ai-list-item {
	display: flex;
	align-items: flex-start;
	margin: 12rpx 0;
	padding-left: 8rpx;
}

.ai-content .list-num {
	color: #07C160;
	font-weight: 600;
	min-width: 40rpx;
	flex-shrink: 0;
}

.ai-content .list-dot {
	color: #07C160;
	font-weight: bold;
	margin-right: 12rpx;
	flex-shrink: 0;
}

.ai-content .code-block {
	background: #1e1e1e;
	color: #d4d4d4;
	padding: 20rpx 24rpx;
	border-radius: 12rpx;
	margin: 16rpx 0;
	overflow-x: auto;
	font-family: 'Monaco', 'Consolas', monospace;
	font-size: 26rpx;
	line-height: 1.6;
	white-space: pre-wrap;
	word-break: break-all;
}

.ai-content .inline-code {
	background: #f0f0f0;
	color: #e83e8c;
	padding: 4rpx 12rpx;
	border-radius: 6rpx;
	font-family: 'Monaco', 'Consolas', monospace;
	font-size: 28rpx;
}

.ai-content strong {
	font-weight: 600;
	color: #1a1a1a;
}

/* 多选操作栏 */
.select-action-bar {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 24rpx 32rpx;
	background: #fff;
	border-top: 1rpx solid #eee;
}

.select-info {
	display: flex;
	align-items: center;
}

.select-count {
	font-size: 28rpx;
	color: #07C160;
	font-weight: 500;
}

.select-actions {
	display: flex;
	gap: 24rpx;
}

.select-action-btn {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 16rpx 24rpx;
	border-radius: 16rpx;
	background: #f5f5f5;
	color: #333;
}

.select-action-btn text {
	font-size: 22rpx;
	margin-top: 8rpx;
}

.select-action-btn.cancel {
	background: #ffebeb;
	color: #ff4d4f;
}

/* 聊天记录卡片 */
.chat-record-card {
	background: #fff;
	border-radius: 16rpx;
	overflow: hidden;
	box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.08);
	min-width: 400rpx;
	max-width: 100%;
}

.record-header {
	display: flex;
	align-items: center;
	gap: 12rpx;
	padding: 20rpx 24rpx;
	background: #f8f8f8;
	border-bottom: 1rpx solid #eee;
}

.record-title {
	font-size: 28rpx;
	font-weight: 500;
	color: #333;
}

.record-preview {
	padding: 20rpx 24rpx;
}

.record-item {
	display: flex;
	font-size: 26rpx;
	line-height: 1.6;
	margin-bottom: 12rpx;
}

.record-item:last-child {
	margin-bottom: 0;
}

.record-name {
	color: #07C160;
	flex-shrink: 0;
}

.record-text {
	color: #666;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.record-more {
	font-size: 24rpx;
	color: #999;
	margin-top: 8rpx;
}

.record-footer {
	padding: 16rpx 24rpx;
	border-top: 1rpx solid #eee;
	background: #fafafa;
}

.record-label {
	font-size: 24rpx;
	color: #999;
}

/* 聊天记录详情弹窗 */
.record-detail-mask {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.5);
	z-index: 1000;
}

.record-detail-popup {
	position: fixed;
	left: 5%;
	right: 5%;
	top: 50%;
	transform: translateY(-50%) scale(0.9);
	background: #fff;
	border-radius: 24rpx;
	z-index: 1001;
	max-height: 70vh;
	display: flex;
	flex-direction: column;
	opacity: 0;
	pointer-events: none;
	transition: all 0.25s ease;
}

.record-detail-popup.show {
	opacity: 1;
	transform: translateY(-50%) scale(1);
	pointer-events: auto;
}

.popup-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 28rpx 32rpx;
	border-bottom: 1rpx solid #eee;
}

.popup-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #333;
}

.popup-close {
	width: 56rpx;
	height: 56rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 50%;
	background: #f5f5f5;
}

.popup-content {
	flex: 1;
	padding: 24rpx 32rpx;
	overflow-y: auto;
	max-height: 50vh;
}

.popup-msg {
	margin-bottom: 28rpx;
}

.popup-msg:last-child {
	margin-bottom: 0;
}

.popup-msg-row {
	display: flex;
	gap: 20rpx;
}

.popup-avatar {
	width: 72rpx;
	height: 72rpx;
	border-radius: 12rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	color: #fff;
	flex-shrink: 0;
}

.popup-msg-main {
	flex: 1;
	min-width: 0;
}

.popup-msg-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 8rpx;
}

.popup-name {
	font-size: 28rpx;
	font-weight: 500;
	color: #333;
}

.popup-time {
	font-size: 24rpx;
	color: #999;
}

.popup-msg-content {
	font-size: 28rpx;
	color: #333;
	line-height: 1.6;
	word-break: break-all;
}

.popup-actions {
	display: flex;
	gap: 24rpx;
	padding: 24rpx 32rpx;
	border-top: 1rpx solid #eee;
}

.popup-action-btn {
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 12rpx;
	padding: 24rpx;
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	color: #fff;
	border-radius: 16rpx;
	font-size: 28rpx;
}

.popup-action-btn:last-child {
	background: linear-gradient(135deg, #059669 0%, #047857 100%);
}
</style>
