<template>
	<view class="custom-tabbar">
		<view 
			class="tab-item" 
			:class="{ active: current === index }"
			v-for="(item, index) in tabs" 
			:key="index"
			@click="switchTab(index)"
		>
			<Icon :name="item.icon" size="20" class="tab-icon" />
			<text class="tab-text">{{ item.text }}</text>
		</view>
	</view>
</template>

<script setup>
import { ref, watch } from 'vue'
import Icon from '@/components/Icon.vue'

const props = defineProps({
	currentTab: {
		type: Number,
		default: 0
	}
})

const current = ref(props.currentTab)

watch(() => props.currentTab, (val) => {
	current.value = val
})

const tabs = [
	{ icon: 'robot', text: '工作台', path: '/pages/chat/index' },
	{ icon: 'book', text: '知识库', path: '/pages/knowledge/index' },
	{ icon: 'cloud', text: '云端', path: '/pages/monitor/index' },
	{ icon: 'chart', text: '报表', path: '/pages/stats/index' },
	{ icon: 'settings', text: '管理', path: '/pages/mine/index' }
]

const switchTab = (index) => {
	if (current.value === index) return
	current.value = index
	const path = tabs[index].path
	// 统一使用 reLaunch 避免 switchTab 限制
	uni.reLaunch({ url: path })
}
</script>

<style scoped>
.custom-tabbar {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	height: 100rpx;
	background: #fff;
	display: flex;
	align-items: center;
	justify-content: space-around;
	box-shadow: 0 -2rpx 20rpx rgba(0, 0, 0, 0.08);
	padding-bottom: env(safe-area-inset-bottom);
	z-index: 999;
}

.tab-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 8rpx 0;
}

.tab-icon {
	margin-bottom: 4rpx;
	color: #86909C;
}

.tab-text {
	font-size: 22rpx;
	color: #999;
}

.tab-item.active .tab-icon {
	color: #07C160;
}

.tab-item.active .tab-text {
	color: #07C160;
	font-weight: 500;
}
</style>
