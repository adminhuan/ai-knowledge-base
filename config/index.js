/**
 * 应用配置
 */

// 环境：development | production
const ENV = 'production'

const config = {
	development: {
		API_BASE_URL: 'http://localhost:8080',
		WS_URL: 'ws://localhost:8080'
	},
	production: {
		API_BASE_URL: 'https://z.arshop.top',
		WS_URL: 'wss://z.arshop.top'
	}
}

export const API_BASE_URL = config[ENV].API_BASE_URL
export const WS_URL = config[ENV].WS_URL

// AI 配置
export const AI_CONFIG = {
	model: 'deepseek-chat', // 可选: gpt-3.5-turbo, qwen-turbo, glm-4 等
	maxTokens: 2000,
	temperature: 0.7
}

// 知识库配置
export const KNOWLEDGE_CONFIG = {
	maxContentLength: 10000,
	embeddingDimension: 1536  // OpenAI ada-002 维度
}

export default {
	ENV,
	...config[ENV],
	AI_CONFIG,
	KNOWLEDGE_CONFIG
}
