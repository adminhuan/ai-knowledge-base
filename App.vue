<!-- HBuilder X 版本要求: 3.6.11+ -->
<template>
  <view></view>
</template>

<script lang="ts">
  // #ifdef APP-ANDROID || APP-HARMONY
  let firstBackTime = 0
  // #endif
  export default {
    onLaunch: function () {
      console.log('App Launch')
      // 隐藏系统 tabBar
      uni.hideTabBar({ animation: false, fail: () => {} })
      // 检查登录状态
      const token = uni.getStorageSync('token')
      if (!token) {
        uni.reLaunch({ url: '/pages/login/index' })
      }
    },
    onShow: function () {
      console.log('App Show')
      uni.hideTabBar({ animation: false, fail: () => {} })
      // 同步全局背景（H5 场景 body 也跟随）
      if (typeof window !== 'undefined') {
        import('@/utils/theme').then(mod => {
          mod.applyGlobalBackground && mod.applyGlobalBackground()
        })
      }
    },
    onHide: function () {
      console.log('App Hide')
    },
    // #ifdef UNI-APP-X && APP-ANDROID || APP-HARMONY
    onLastPageBackPress: function () {
      console.log('App LastPageBackPress')
      if (firstBackTime == 0) {
        uni.showToast({
          title: '再按一次退出应用',
          position: 'bottom',
        })
        firstBackTime = Date.now()
        setTimeout(() => {
          firstBackTime = 0
        }, 2000)
      } else if (Date.now() - firstBackTime < 2000) {
        firstBackTime = Date.now()
        uni.exit()
      }
    },
    // #endif
    onExit() {
      console.log('App Exit')
    },
  }
</script>

<style>
  /*每个页面公共css */
  /* uni.css - 通用组件、模板样式库，可以当作一套ui库应用 */
  /* #ifdef APP-VUE */
  @import './common/uni.css';
  /* #endif */

  :root {
    --brand: #07C160;
    --brand-strong: #06AD56;
    --brand-ink: #0f172a;
    --brand-muted: #66768b;
    --card: #ffffff;
    --card-strong: #f5f7fa;
    --border: #e5e7eb;
    --shadow-soft: 0 16rpx 40rpx rgba(7, 193, 96, 0.12);
    --shadow-plain: 0 8rpx 20rpx rgba(0, 0, 0, 0.08);
  }

  page {
    background: transparent;
    color: var(--brand-ink);
    font-family: 'PingFang SC', 'HarmonyOS Sans', 'SF Pro Display', sans-serif;
    min-height: 100vh;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    touch-action: pan-y;
  }
</style>
