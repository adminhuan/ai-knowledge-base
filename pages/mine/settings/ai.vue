<template>
	<view class="ai-page">
		<!-- 标题 -->
		<view class="page-header">
			<text class="page-title">AI 配置</text>
			<text class="page-desc">分别配置各个 AI 服务</text>
		</view>

		<!-- Tab 切换 -->
		<view class="tabs">
			<view 
				class="tab" 
				:class="{ active: activeTab === 'chat' }" 
				@click="activeTab = 'chat'"
			>
				<text class="tab-icon">💬</text>
				<text class="tab-text">聊天</text>
			</view>
			<view 
				class="tab" 
				:class="{ active: activeTab === 'vision' }" 
				@click="activeTab = 'vision'"
			>
				<text class="tab-icon">👁️</text>
				<text class="tab-text">图片</text>
			</view>
			<view 
				class="tab" 
				:class="{ active: activeTab === 'file' }" 
				@click="activeTab = 'file'"
			>
				<text class="tab-icon">📄</text>
				<text class="tab-text">文件</text>
			</view>
			<view 
				class="tab" 
				:class="{ active: activeTab === 'embedding' }" 
				@click="activeTab = 'embedding'"
			>
				<text class="tab-icon">🔍</text>
				<text class="tab-text">向量</text>
			</view>
			<view 
				class="tab" 
				:class="{ active: activeTab === 'search' }" 
				@click="activeTab = 'search'"
			>
				<text class="tab-icon">🌐</text>
				<text class="tab-text">搜索</text>
			</view>
		</view>

		<!-- 聊天AI配置 -->
		<view class="config-section" v-show="activeTab === 'chat'">
			<view class="section-header">
				<text class="section-title">聊天 AI</text>
				<text class="section-desc">用于普通对话和知识库问答</text>
			</view>
			
			<view class="card">
				<view class="field">
					<text class="label">服务商</text>
					<view class="picker" @click="showPicker('chat')">
						<text class="picker-text">{{ getProviderName(config.chat.provider) }}</text>
						<text class="picker-arrow">›</text>
					</view>
				</view>
				
				<view class="field">
					<text class="label">API Base URL</text>
					<input class="input" v-model="config.chat.baseUrl" placeholder="https://api.example.com/v1" />
				</view>
				
				<view class="field">
					<text class="label">API Key</text>
					<view class="input-group">
						<input 
							class="input flex-1" 
							:type="showKeys.chat ? 'text' : 'password'" 
							v-model="config.chat.apiKey" 
							placeholder="sk-xxxxxxxx" 
						/>
						<view class="toggle-btn" @click="showKeys.chat = !showKeys.chat">
							<text>{{ showKeys.chat ? '隐藏' : '显示' }}</text>
						</view>
					</view>
				</view>
				
				<view class="field">
					<text class="label">模型名称</text>
					<input class="input" v-model="config.chat.model" placeholder="glm-4-flash" />
					<text class="hint">推荐: glm-4.5-flash(免费), qwen-turbo, deepseek-chat</text>
				</view>
			</view>
		</view>

		<!-- 联网搜索AI配置 -->
		<view class="config-section" v-show="activeTab === 'search'">
			<view class="section-header">
				<text class="section-title">联网搜索 AI</text>
				<text class="section-desc">用于实时网络搜索功能</text>
			</view>
			
			<view class="card">
				<view class="field">
					<text class="label">服务商</text>
					<view class="picker" @click="showPicker('search')">
						<text class="picker-text">{{ getProviderName(config.search.provider) }}</text>
						<text class="picker-arrow">›</text>
					</view>
				</view>
				
				<view class="field">
					<text class="label">API Base URL</text>
					<input class="input" v-model="config.search.baseUrl" placeholder="https://dashscope.aliyuncs.com/compatible-mode/v1" />
				</view>
				
				<view class="field">
					<text class="label">API Key</text>
					<view class="input-group">
						<input 
							class="input flex-1" 
							:type="showKeys.search ? 'text' : 'password'" 
							v-model="config.search.apiKey" 
							placeholder="sk-xxxxxxxx" 
						/>
						<view class="toggle-btn" @click="showKeys.search = !showKeys.search">
							<text>{{ showKeys.search ? '隐藏' : '显示' }}</text>
						</view>
					</view>
				</view>
				
				<view class="field">
					<text class="label">模型名称</text>
					<input class="input" v-model="config.search.model" placeholder="qwen-turbo" />
					<text class="hint">推荐: qwen-turbo(免费联网), qwen-plus</text>
				</view>
			</view>
		</view>

		<!-- Embedding配置 -->
		<view class="config-section" v-show="activeTab === 'embedding'">
			<view class="section-header">
				<text class="section-title">向量 Embedding</text>
				<text class="section-desc">用于知识库语义搜索</text>
			</view>
			
			<view class="card">
				<view class="field">
					<text class="label">服务商</text>
					<view class="picker" @click="showPicker('embedding')">
						<text class="picker-text">{{ getProviderName(config.embedding.provider) }}</text>
						<text class="picker-arrow">›</text>
					</view>
				</view>
				
				<view class="field">
					<text class="label">API Base URL</text>
					<input class="input" v-model="config.embedding.baseUrl" placeholder="https://open.bigmodel.cn/api/paas/v4" />
				</view>
				
				<view class="field">
					<text class="label">API Key</text>
					<view class="input-group">
						<input 
							class="input flex-1" 
							:type="showKeys.embedding ? 'text' : 'password'" 
							v-model="config.embedding.apiKey" 
							placeholder="xxxxxxxx.xxxxxxxx" 
						/>
						<view class="toggle-btn" @click="showKeys.embedding = !showKeys.embedding">
							<text>{{ showKeys.embedding ? '隐藏' : '显示' }}</text>
						</view>
					</view>
				</view>
				
				<view class="field">
					<text class="label">模型名称</text>
					<input class="input" v-model="config.embedding.model" placeholder="embedding-2" />
					<text class="hint">推荐: embedding-2(智谱), text-embedding-v3(通义)</text>
				</view>
				
				<view class="field">
					<text class="label">向量维度</text>
					<input class="input" type="number" v-model="config.embedding.dimension" placeholder="1024" />
					<text class="hint">embedding-2: 1024, text-embedding-v3: 1024</text>
				</view>
			</view>
		</view>

		<!-- 视觉/图片识别AI配置 -->
		<view class="config-section" v-show="activeTab === 'vision'">
			<view class="section-header">
				<text class="section-title">图片识别 AI</text>
				<text class="section-desc">用于识别图片内容（GLM视觉模型轮换）</text>
			</view>
			
			<view class="card">
				<view class="field">
					<text class="label">服务商</text>
					<view class="picker" @click="showPicker('vision')">
						<text class="picker-text">{{ getProviderName(config.vision.provider) }}</text>
						<text class="picker-arrow">›</text>
					</view>
				</view>
				
				<view class="field">
					<text class="label">API Base URL</text>
					<input class="input" v-model="config.vision.baseUrl" placeholder="https://open.bigmodel.cn/api/paas/v4" />
				</view>
				
				<view class="field">
					<text class="label">API Key</text>
					<view class="input-group">
						<input 
							class="input flex-1" 
							:type="showKeys.vision ? 'text' : 'password'" 
							v-model="config.vision.apiKey" 
							placeholder="xxxxxxxx.xxxxxxxx" 
						/>
						<view class="toggle-btn" @click="showKeys.vision = !showKeys.vision">
							<text>{{ showKeys.vision ? '隐藏' : '显示' }}</text>
						</view>
					</view>
				</view>
				
				<view class="field">
					<text class="label">模型列表（逗号分隔，轮换使用）</text>
					<input class="input" v-model="config.vision.models" placeholder="glm-4v-flash,glm-4.1v-thinking-flash" />
					<text class="hint">免费: glm-4v-flash, glm-4.1v-thinking-flash</text>
				</view>
			</view>
		</view>

		<!-- 文件解析AI配置 -->
		<view class="config-section" v-show="activeTab === 'file'">
			<view class="section-header">
				<text class="section-title">文件解析 AI</text>
				<text class="section-desc">用于解析 PDF/Word/Excel/图片</text>
			</view>
			
			<view class="card">
				<view class="field">
					<text class="label">服务商</text>
					<view class="picker" @click="showPicker('file')">
						<text class="picker-text">{{ getProviderName(config.file.provider) }}</text>
						<text class="picker-arrow">›</text>
					</view>
				</view>
				
				<view class="field">
					<text class="label">API Base URL</text>
					<input class="input" v-model="config.file.baseUrl" placeholder="https://api.moonshot.cn/v1" />
				</view>
				
				<view class="field">
					<text class="label">API Key</text>
					<view class="input-group">
						<input 
							class="input flex-1" 
							:type="showKeys.file ? 'text' : 'password'" 
							v-model="config.file.apiKey" 
							placeholder="sk-xxxxxxxx" 
						/>
						<view class="toggle-btn" @click="showKeys.file = !showKeys.file">
							<text>{{ showKeys.file ? '隐藏' : '显示' }}</text>
						</view>
					</view>
				</view>
				
				<view class="field">
					<text class="label">模型名称</text>
					<input class="input" v-model="config.file.model" placeholder="moonshot-v1-auto" />
					<text class="hint">推荐: moonshot-v1-auto(Kimi免费), qwen-vl-max</text>
				</view>
			</view>
		</view>

		<!-- 通用设置 -->
		<view class="card" style="margin-top: 24rpx;">
			<view class="card-header">
				<text class="card-title">通用设置</text>
			</view>
			
			<view class="field">
				<text class="label">系统提示词</text>
				<textarea 
					class="textarea"
					v-model="config.systemPrompt"
					placeholder="你是一个知识库助手..."
					:maxlength="500"
				/>
			</view>
			
			<view class="switch-item">
				<view class="switch-info">
					<text class="switch-label">智能知识库检索</text>
					<text class="switch-desc">说"查找/搜索"时自动检索知识库</text>
				</view>
				<switch :checked="config.enableRAG" @change="config.enableRAG = $event.detail.value" color="#07C160" />
			</view>
		</view>

		<!-- 操作按钮 -->
		<view class="btn-group">
			<view class="btn primary" @click="saveConfig">保存全部配置</view>
			<view class="btn" @click="testCurrent">测试当前服务</view>
			<view class="btn danger" @click="resetConfig">恢复默认</view>
		</view>

		<!-- 服务商选择弹窗 -->
		<view class="modal-mask" v-if="pickerVisible" @click="pickerVisible = false">
			<view class="modal" @click.stop>
				<view class="modal-header">
					<text class="modal-title">选择服务商</text>
				</view>
				<view class="provider-list">
					<view 
						class="provider-item" 
						:class="{ active: isProviderSelected(item) }"
						v-for="item in currentProviders" 
						:key="item.id"
						@click="selectProvider(item)"
					>
						<view class="provider-info">
							<text class="provider-name">{{ item.name }}</text>
							<text class="provider-desc">{{ item.desc }}</text>
						</view>
						<text class="check-icon" v-if="isProviderSelected(item)">✓</text>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { saveAIConfig, getAIConfig } from '@/api/user'

const STORAGE_KEY = 'ai_config_v2'

const providers = {
	chat: [
		{ id: 'zhipu', name: '智谱 AI', desc: 'GLM-4-Flash-250414 免费', baseUrl: 'https://open.bigmodel.cn/api/paas/v4', model: 'glm-4-flash-250414' },
		{ id: 'qwen', name: '通义千问', desc: 'qwen-turbo 超便宜', baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1', model: 'qwen-turbo' },
		{ id: 'deepseek', name: 'DeepSeek', desc: '性价比高', baseUrl: 'https://api.deepseek.com/v1', model: 'deepseek-chat' },
		{ id: 'openai', name: 'OpenAI', desc: 'GPT-4o', baseUrl: 'https://api.openai.com/v1', model: 'gpt-4o-mini' },
		{ id: 'custom', name: '自定义', desc: '自定义URL和模型', baseUrl: '', model: '' }
	],
	vision: [
		{ id: 'zhipu', name: '智谱 AI', desc: 'GLM-4V 视觉模型（免费轮换）', baseUrl: 'https://open.bigmodel.cn/api/paas/v4', models: 'glm-4v-flash,glm-4.1v-thinking-flash' },
		{ id: 'qwen', name: '通义千问', desc: 'qwen-vl-plus 视觉', baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1', models: 'qwen-vl-plus' },
		{ id: 'custom', name: '自定义', desc: '自定义URL和模型', baseUrl: '', models: '' }
	],
	file: [
		{ id: 'qwen', name: '通义千问', desc: 'qwen-doc-turbo 文档解析', baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1', model: 'qwen-doc-turbo' },
		{ id: 'kimi', name: 'Kimi (月之暗面)', desc: '文件解析限时免费', baseUrl: 'https://api.moonshot.cn/v1', model: 'moonshot-v1-auto' },
		{ id: 'custom', name: '自定义', desc: '自定义URL和模型', baseUrl: '', model: '' }
	],
	embedding: [
		{ id: 'zhipu', name: '智谱 AI', desc: 'embedding-2', baseUrl: 'https://open.bigmodel.cn/api/paas/v4', model: 'embedding-2', dimension: 1024 },
		{ id: 'qwen', name: '通义千问', desc: 'text-embedding-v3', baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1', model: 'text-embedding-v3', dimension: 1024 },
		{ id: 'openai', name: 'OpenAI', desc: 'text-embedding-3-small', baseUrl: 'https://api.openai.com/v1', model: 'text-embedding-3-small', dimension: 1536 },
		{ id: 'custom', name: '自定义', desc: '自定义URL和模型', baseUrl: '', model: '', dimension: 1024 }
	],
	search: [
		{ id: 'qwen', name: '通义千问', desc: '联网搜索限时免费', baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1', model: 'qwen-turbo' },
		{ id: 'zhipu', name: '智谱 AI', desc: '联网搜索', baseUrl: 'https://open.bigmodel.cn/api/paas/v4', model: 'glm-4-flash-250414' },
		{ id: 'custom', name: '自定义', desc: '自定义URL和模型', baseUrl: '', model: '' }
	]
}

const defaultConfig = {
	chat: {
		provider: 'zhipu',
		baseUrl: 'https://open.bigmodel.cn/api/paas/v4',
		apiKey: '',
		model: 'glm-4-flash-250414'
	},
	vision: {
		provider: 'zhipu',
		baseUrl: 'https://open.bigmodel.cn/api/paas/v4',
		apiKey: '',
		models: 'glm-4v-flash,glm-4.1v-thinking-flash'
	},
	file: {
		provider: 'qwen',
		baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
		apiKey: '',
		model: 'qwen-doc-turbo'
	},
	embedding: {
		provider: 'zhipu',
		baseUrl: 'https://open.bigmodel.cn/api/paas/v4',
		apiKey: '',
		model: 'embedding-2',
		dimension: 1024
	},
	search: {
		provider: 'qwen',
		baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
		apiKey: '',
		model: 'qwen-turbo'
	},
	systemPrompt: '你是一个智能知识库助手，帮助用户管理、检索和整理知识。回答问题时尽量简洁准确。',
	enableRAG: true
}

const activeTab = ref('chat')
const config = ref(JSON.parse(JSON.stringify(defaultConfig)))
const showKeys = ref({ chat: false, vision: false, file: false, embedding: false, search: false })
const pickerVisible = ref(false)
const pickerType = ref('chat')

const currentProviders = computed(() => providers[pickerType.value] || [])

onMounted(() => {
	loadConfig()
})

onShow(() => {
	loadConfig()
})

const loadConfig = async () => {
	try {
		const saved = uni.getStorageSync(STORAGE_KEY)
		if (saved) {
			const data = typeof saved === 'string' ? JSON.parse(saved) : saved
			config.value = mergeConfig(defaultConfig, data)
		}
		
		const res = await getAIConfig()
		if (res?.data) {
			config.value = mergeConfig(config.value, mapServerConfig(res.data))
			uni.setStorageSync(STORAGE_KEY, JSON.stringify(config.value))
		}
	} catch (e) {
		console.log('加载配置失败', e)
	}
}

const mergeConfig = (base, update) => {
	const result = JSON.parse(JSON.stringify(base))
	for (const key in update) {
		if (typeof update[key] === 'object' && !Array.isArray(update[key]) && update[key] !== null) {
			result[key] = { ...result[key], ...update[key] }
		} else if (update[key] !== undefined && update[key] !== '') {
			result[key] = update[key]
		}
	}
	return result
}

const mapServerConfig = (data) => {
	return {
		chat: {
			provider: data.chat_provider || defaultConfig.chat.provider,
			baseUrl: data.chat_base_url || defaultConfig.chat.baseUrl,
			apiKey: data.chat_api_key || '',
			model: data.chat_model || defaultConfig.chat.model
		},
		vision: {
			provider: data.vision_provider || defaultConfig.vision.provider,
			baseUrl: data.vision_base_url || defaultConfig.vision.baseUrl,
			apiKey: data.vision_api_key || '',
			models: data.vision_models || defaultConfig.vision.models
		},
		file: {
			provider: data.file_provider || defaultConfig.file.provider,
			baseUrl: data.file_base_url || defaultConfig.file.baseUrl,
			apiKey: data.file_api_key || '',
			model: data.file_model || defaultConfig.file.model
		},
		embedding: {
			provider: data.embedding_provider || defaultConfig.embedding.provider,
			baseUrl: data.embedding_base_url || defaultConfig.embedding.baseUrl,
			apiKey: data.embedding_api_key || '',
			model: data.embedding_model || defaultConfig.embedding.model,
			dimension: data.embedding_dimension || defaultConfig.embedding.dimension
		},
		search: {
			provider: data.search_provider || defaultConfig.search.provider,
			baseUrl: data.search_base_url || defaultConfig.search.baseUrl,
			apiKey: data.search_api_key || '',
			model: data.search_model || defaultConfig.search.model
		},
		systemPrompt: data.system_prompt || defaultConfig.systemPrompt,
		enableRAG: data.enable_rag !== undefined ? data.enable_rag : defaultConfig.enableRAG
	}
}

const getProviderName = (id) => {
	for (const type in providers) {
		const found = providers[type].find(p => p.id === id)
		if (found) return found.name
	}
	return '自定义'
}

const showPicker = (type) => {
	pickerType.value = type
	pickerVisible.value = true
}

const isProviderSelected = (item) => {
	return config.value[pickerType.value]?.provider === item.id
}

const selectProvider = (item) => {
	const type = pickerType.value
	config.value[type].provider = item.id
	if (item.id !== 'custom') {
		config.value[type].baseUrl = item.baseUrl
		if (item.model !== undefined) {
			config.value[type].model = item.model
		}
		if (item.models !== undefined) {
			config.value[type].models = item.models
		}
		if (item.dimension !== undefined) {
			config.value[type].dimension = item.dimension
		}
	}
	pickerVisible.value = false
}

const saveConfig = async () => {
	uni.setStorageSync(STORAGE_KEY, JSON.stringify(config.value))
	
	try {
		await saveAIConfig({
			chat_provider: config.value.chat.provider,
			chat_base_url: config.value.chat.baseUrl,
			chat_api_key: config.value.chat.apiKey,
			chat_model: config.value.chat.model,
			vision_provider: config.value.vision.provider,
			vision_base_url: config.value.vision.baseUrl,
			vision_api_key: config.value.vision.apiKey,
			vision_models: config.value.vision.models,
			file_provider: config.value.file.provider,
			file_base_url: config.value.file.baseUrl,
			file_api_key: config.value.file.apiKey,
			file_model: config.value.file.model,
			embedding_provider: config.value.embedding.provider,
			embedding_base_url: config.value.embedding.baseUrl,
			embedding_api_key: config.value.embedding.apiKey,
			embedding_model: config.value.embedding.model,
			embedding_dimension: config.value.embedding.dimension,
			search_provider: config.value.search.provider,
			search_base_url: config.value.search.baseUrl,
			search_api_key: config.value.search.apiKey,
			search_model: config.value.search.model,
			system_prompt: config.value.systemPrompt,
			enable_rag: config.value.enableRAG
		})
		uni.showToast({ title: '配置已保存', icon: 'success' })
	} catch (e) {
		console.log('保存失败', e)
		uni.showToast({ title: '本地已保存，云端同步失败', icon: 'none' })
	}
}

const testCurrent = async () => {
	const type = activeTab.value
	const cfg = config.value[type]
	
	if (!cfg.apiKey) {
		uni.showToast({ title: '请先填写 API Key', icon: 'none' })
		return
	}
	
	uni.showLoading({ title: '测试中...' })
	
	try {
		let testData = {}
		
		if (type === 'embedding') {
			testData = {
				model: cfg.model,
				input: '测试'
			}
			const res = await uni.request({
				url: `${cfg.baseUrl}/embeddings`,
				method: 'POST',
				header: {
					'Authorization': `Bearer ${cfg.apiKey}`,
					'Content-Type': 'application/json'
				},
				data: testData,
				timeout: 15000
			})
			uni.hideLoading()
			if (res.statusCode === 200 && res.data.data) {
				uni.showToast({ title: '连接成功', icon: 'success' })
			} else {
				uni.showToast({ title: res.data.error?.message || '连接失败', icon: 'none' })
			}
		} else {
			testData = {
				model: cfg.model,
				messages: [{ role: 'user', content: 'Hi' }],
				max_tokens: 10
			}
			const res = await uni.request({
				url: `${cfg.baseUrl}/chat/completions`,
				method: 'POST',
				header: {
					'Authorization': `Bearer ${cfg.apiKey}`,
					'Content-Type': 'application/json'
				},
				data: testData,
				timeout: 15000
			})
			uni.hideLoading()
			if (res.statusCode === 200 && res.data.choices) {
				uni.showToast({ title: '连接成功', icon: 'success' })
			} else {
				uni.showToast({ title: res.data.error?.message || '连接失败', icon: 'none' })
			}
		}
	} catch (e) {
		uni.hideLoading()
		uni.showToast({ title: '连接失败: ' + (e.errMsg || '网络错误'), icon: 'none' })
	}
}

const resetConfig = () => {
	uni.showModal({
		title: '确认重置',
		content: '将恢复为默认配置，是否继续？',
		success: (res) => {
			if (res.confirm) {
				config.value = JSON.parse(JSON.stringify(defaultConfig))
				uni.setStorageSync(STORAGE_KEY, JSON.stringify(config.value))
				uni.showToast({ title: '已重置', icon: 'none' })
			}
		}
	})
}
</script>

<style scoped>
.ai-page {
	min-height: 100vh;
	background-color: #f5f5f5;
	padding: 32rpx;
	padding-bottom: 120rpx;
}

.page-header {
	margin-bottom: 24rpx;
}

.page-title {
	font-size: 44rpx;
	font-weight: 700;
	color: #333;
	display: block;
}

.page-desc {
	font-size: 26rpx;
	color: #999;
	margin-top: 8rpx;
	display: block;
}

/* Tabs */
.tabs {
	display: flex;
	background: #fff;
	border-radius: 16rpx;
	padding: 8rpx;
	margin-bottom: 24rpx;
	box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.05);
}

.tab {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 20rpx 8rpx;
	border-radius: 12rpx;
	transition: all 0.3s;
}

.tab.active {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
}

.tab-icon {
	font-size: 36rpx;
	margin-bottom: 8rpx;
}

.tab-text {
	font-size: 24rpx;
	color: #666;
}

.tab.active .tab-text {
	color: #fff;
	font-weight: 500;
}

/* Section */
.config-section {
	margin-bottom: 24rpx;
}

.section-header {
	margin-bottom: 16rpx;
	padding: 0 8rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #333;
	display: block;
}

.section-desc {
	font-size: 24rpx;
	color: #999;
	margin-top: 4rpx;
	display: block;
}

/* Card */
.card {
	background: #fff;
	border-radius: 20rpx;
	padding: 32rpx;
	box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.05);
}

.card-header {
	margin-bottom: 24rpx;
	padding-bottom: 16rpx;
	border-bottom: 1rpx solid #f0f0f0;
}

.card-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #333;
}

/* Field */
.field {
	margin-bottom: 28rpx;
}

.field:last-child {
	margin-bottom: 0;
}

.label {
	font-size: 28rpx;
	color: #333;
	margin-bottom: 12rpx;
	display: block;
	font-weight: 500;
}

.input {
	width: 100%;
	height: 88rpx;
	background: #f8f8f8;
	border-radius: 12rpx;
	padding: 0 24rpx;
	font-size: 28rpx;
	color: #333;
	box-sizing: border-box;
}

.input-group {
	display: flex;
	align-items: center;
	gap: 16rpx;
}

.flex-1 {
	flex: 1;
}

.toggle-btn {
	padding: 16rpx 24rpx;
	background: #f0f0f0;
	border-radius: 8rpx;
}

.toggle-btn text {
	font-size: 24rpx;
	color: #666;
}

.picker {
	display: flex;
	align-items: center;
	justify-content: space-between;
	height: 88rpx;
	background: #f8f8f8;
	border-radius: 12rpx;
	padding: 0 24rpx;
}

.picker-text {
	font-size: 28rpx;
	color: #333;
}

.picker-arrow {
	font-size: 32rpx;
	color: #999;
}

.hint {
	font-size: 24rpx;
	color: #999;
	margin-top: 8rpx;
	display: block;
}

.textarea {
	width: 100%;
	height: 160rpx;
	background: #f8f8f8;
	border-radius: 12rpx;
	padding: 20rpx 24rpx;
	font-size: 28rpx;
	color: #333;
	box-sizing: border-box;
}

/* Switch */
.switch-item {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 20rpx 0;
	border-top: 1rpx solid #f5f5f5;
	margin-top: 16rpx;
}

.switch-info {
	flex: 1;
}

.switch-label {
	font-size: 28rpx;
	color: #333;
	display: block;
}

.switch-desc {
	font-size: 24rpx;
	color: #999;
	margin-top: 4rpx;
	display: block;
}

/* Buttons */
.btn-group {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
	margin-top: 32rpx;
}

.btn {
	height: 96rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 16rpx;
	font-size: 32rpx;
	font-weight: 500;
}

.btn.primary {
	background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
	color: #fff;
}

.btn:not(.primary):not(.danger) {
	background: #fff;
	color: #333;
	border: 2rpx solid #ddd;
}

.btn.danger {
	background: #fff;
	color: #ff4d4f;
	border: 2rpx solid #ffccc7;
}

/* Modal */
.modal-mask {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0,0,0,0.5);
	display: flex;
	align-items: flex-end;
	z-index: 1000;
}

.modal {
	width: 100%;
	background: #fff;
	border-radius: 32rpx 32rpx 0 0;
	padding-bottom: env(safe-area-inset-bottom);
}

.modal-header {
	padding: 32rpx;
	text-align: center;
	border-bottom: 1rpx solid #f0f0f0;
}

.modal-title {
	font-size: 34rpx;
	font-weight: 600;
	color: #333;
}

.provider-list {
	max-height: 60vh;
	overflow-y: auto;
}

.provider-item {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 32rpx;
	border-bottom: 1rpx solid #f5f5f5;
}

.provider-item.active {
	background: #f0fff4;
}

.provider-info {
	flex: 1;
}

.provider-name {
	font-size: 32rpx;
	color: #333;
	font-weight: 500;
	display: block;
}

.provider-desc {
	font-size: 26rpx;
	color: #999;
	margin-top: 8rpx;
	display: block;
}

.check-icon {
	font-size: 36rpx;
	color: #07C160;
	font-weight: bold;
}
</style>
