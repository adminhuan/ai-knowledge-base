const STORAGE_KEY = 'user_background_setting'
const DEFAULT_BG = { type: 'color', value: '#ffffff' }

export const getBackgroundSetting = () => {
  try {
    const val = uni.getStorageSync(STORAGE_KEY)
    if (val) {
      return typeof val === 'string' ? JSON.parse(val) : val
    }
  } catch (e) {}
  return DEFAULT_BG
}

export const setBackgroundSetting = (setting) => {
  const data = {
    ...DEFAULT_BG,
    ...setting,
  }
  const val = data.value || ''
  if (!data.type) {
    data.type = isImage(val) ? 'image' : 'color'
  }
  uni.setStorageSync(STORAGE_KEY, JSON.stringify(data))
  return data
}

export const getBackgroundStyle = () => {
  const setting = getBackgroundSetting()
  const val = setting.value || DEFAULT_BG.value
  if (setting.type === 'image' || isImage(val)) {
    return {
      backgroundImage: `url(${val})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
      backgroundColor: '#ffffff',
    }
  }
  // 默认颜色 / 渐变
  return {
    background: val,
  }
}

export const applyGlobalBackground = () => {
  const style = getBackgroundStyle()
  if (typeof document !== 'undefined') {
    const el = document.body || document.documentElement
    if (style.backgroundImage) {
      el.style.backgroundImage = style.backgroundImage
      el.style.backgroundSize = style.backgroundSize
      el.style.backgroundRepeat = style.backgroundRepeat
      el.style.backgroundPosition = style.backgroundPosition
      el.style.backgroundColor = style.backgroundColor || '#ffffff'
    } else {
      el.style.background = style.background || '#ffffff'
      el.style.backgroundImage = ''
    }
  }
  return style
}

export default {
  getBackgroundSetting,
  setBackgroundSetting,
  getBackgroundStyle,
  applyGlobalBackground,
}

function isImage(val) {
  if (!val) return false
  return /^https?:\/\//.test(val)
    || val.startsWith('data:')
    || val.startsWith('file:')
    || val.startsWith('/')
    || val.startsWith('blob:')
    || val.includes('tmp/')
    || val.includes('temp/')
}
