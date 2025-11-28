<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    v-html="paths[name] || paths.placeholder"
    :class="cls"
  />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: {
    type: String,
    default: 'placeholder'
  },
  size: {
    type: [Number, String],
    default: 24
  },
  class: {
    type: String,
    default: ''
  }
})

const paths = {
  placeholder:
    '<rect x="3" y="3" width="18" height="18" rx="4" stroke="currentColor" stroke-width="1.6" fill="none"/>',
  plus:
    '<path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
  menu:
    '<path d="M5 7h14M5 12h14M5 17h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
  refresh:
    '<path d="M5 11a7 7 0 0 1 12-3M19 13a7 7 0 0 1-12 3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M5 7v4h4M19 17v-4h-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
  user:
    '<circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="1.8"/><path d="M5 19c0-3.3 3.1-6 7-6s7 2.7 7 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
  robot:
    '<rect x="5" y="6" width="14" height="12" rx="3" stroke="currentColor" stroke-width="1.6"/><circle cx="10" cy="11" r="1.4" fill="currentColor"/><circle cx="14" cy="11" r="1.4" fill="currentColor"/><path d="M9 15h6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><path d="M12 4v2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
  book:
    '<path d="M6 5.5A2.5 2.5 0 0 1 8.5 3H19v16H8.5A2.5 2.5 0 0 0 6 21.5V5.5Z" stroke="currentColor" stroke-width="1.6" fill="none"/><path d="M6 5.5A2.5 2.5 0 0 1 8.5 3H19" stroke="currentColor" stroke-width="1.6"/><path d="M9 7.5h6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
  clipboard:
    '<rect x="6" y="6" width="12" height="14" rx="2" stroke="currentColor" stroke-width="1.6" fill="none"/><path d="M9 6V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v1" stroke="currentColor" stroke-width="1.6"/><path d="M9 11h6M9 14h4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
  search:
    '<circle cx="11" cy="11" r="6" stroke="currentColor" stroke-width="1.8"/><path d="M16.5 16.5 20 20" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
  note:
    '<rect x="5" y="4" width="14" height="16" rx="2" stroke="currentColor" stroke-width="1.6" fill="none"/><path d="M8 9h8M8 12h6M8 15h4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
  send:
    '<path d="M4.5 12 19 4.5 15.2 12 19 19.5 4.5 12Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" fill="none"/>',
  close:
    '<path d="m6 6 12 12M18 6 6 18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
  tag:
    '<path d="M4 12V6a2 2 0 0 1 2-2h6l8 8-8 8-6-6a2 2 0 0 1-.59-1.41Z" stroke="currentColor" stroke-width="1.6" fill="none"/><circle cx="9" cy="9" r="1.5" fill="currentColor"/>',
  sparkle:
    '<path d="M12 4 13.5 9.5 19 11 13.5 12.5 12 18 10.5 12.5 5 11 10.5 9.5 12 4Z" stroke="currentColor" stroke-width="1.4" fill="none" stroke-linejoin="round"/>',
  share:
    '<path d="M15 8.5V6a3 3 0 1 1 3 3h-2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/><path d="M7 12h7a3 3 0 0 1 3 3v2a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3v-2a3 3 0 0 1 3-3Z" stroke="currentColor" stroke-width="1.6" fill="none"/><path d="M12 12V9" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
  brain:
    '<rect x="5" y="5" width="14" height="14" rx="3" stroke="currentColor" stroke-width="1.6" fill="none"/><path d="M9 8h6M9 12h6M9 16h3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><path d="M8 5v14M16 5v14" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>',
  lightning:
    '<path d="M13 3 7 13h5l-1 8 6-10h-5l1-8Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" fill="none"/>',
  wrench:
    '<path d="M13.5 4a4 4 0 0 0-4.9 4.9l-5.6 5.6a1.5 1.5 0 1 0 2.1 2.1l5.6-5.6A4 4 0 0 0 15 10.5l2 2 2.5-2.5-2-2a4 4 0 0 0-4-4Z" stroke="currentColor" stroke-width="1.6" fill="none" stroke-linejoin="round"/>',
  lock:
    '<rect x="6" y="10" width="12" height="10" rx="2" stroke="currentColor" stroke-width="1.6" fill="none"/><path d="M9 10V7a3 3 0 0 1 6 0v3" stroke="currentColor" stroke-width="1.6"/><circle cx="12" cy="14.5" r="1.2" fill="currentColor"/>',
  folder:
    '<path d="M4 7a2 2 0 0 1 2-2h4l2 2h6a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7Z" stroke="currentColor" stroke-width="1.6" fill="none"/>',
  settings:
    '<circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.6" fill="none"/><path d="M19 12a7.002 7.002 0 0 0-.27-1.93l1.8-1.39-1.8-3.11-2.1.66A7.02 7.02 0 0 0 12 5a7.02 7.02 0 0 0-3.63.23l-2.1-.66-1.8 3.11 1.8 1.39A7.002 7.002 0 0 0 5 12c0 .66.09 1.3.27 1.93l-1.8 1.39 1.8 3.11 2.1-.66A7.02 7.02 0 0 0 12 19c1.22 0 2.38-.31 3.4-.86l2.1.66 1.8-3.11-1.8-1.39c.18-.63.27-1.27.27-1.93Z" stroke="currentColor" stroke-width="1.2" fill="none"/>',
  chart:
    '<path d="M5 5v14h14" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><rect x="7" y="11" width="3" height="6" rx="1" fill="currentColor"/><rect x="12" y="9" width="3" height="8" rx="1" fill="currentColor"/><rect x="17" y="7" width="3" height="10" rx="1" fill="currentColor"/>',
  target:
    '<circle cx="12" cy="12" r="7" stroke="currentColor" stroke-width="1.6" fill="none"/><circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.6"/><circle cx="12" cy="12" r="1.2" fill="currentColor"/>',
  laptop:
    '<rect x="5" y="6" width="14" height="9" rx="1.5" stroke="currentColor" stroke-width="1.6" fill="none"/><path d="M4 17h16" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
  globe:
    '<circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="1.6" fill="none"/><path d="M4 12h16M12 4c2 2 3 5 3 8s-1 6-3 8c-2-2-3-5-3-8s1-6 3-8Z" stroke="currentColor" stroke-width="1.4" fill="none"/>',
  phone:
    '<path d="M10 4h4a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2Z" stroke="currentColor" stroke-width="1.6" fill="none"/><circle cx="12" cy="18" r="1.2" fill="currentColor"/>',
  palette:
    '<path d="M12 4a8 8 0 1 0 0 16h1.5a1.5 1.5 0 0 0 0-3H12a2 2 0 0 1-2-2 3 3 0 0 1 3-3h2.5A4.5 4.5 0 0 0 12 4Z" stroke="currentColor" stroke-width="1.6" fill="none"/><circle cx="9" cy="9" r="1" fill="currentColor"/><circle cx="7" cy="13" r="1" fill="currentColor"/><circle cx="15" cy="9" r="1" fill="currentColor"/><circle cx="14" cy="14" r="1" fill="currentColor"/>',
  doc:
    '<path d="M7 4h7l4 4v10a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2Z" stroke="currentColor" stroke-width="1.6" fill="none"/><path d="M14 4v4h4" stroke="currentColor" stroke-width="1.6"/><path d="M9 13h6M9 16h6M9 10h3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
  image:
    '<rect x="4" y="5" width="16" height="14" rx="2" stroke="currentColor" stroke-width="1.6" fill="none"/><circle cx="9" cy="10" r="2" stroke="currentColor" stroke-width="1.4"/><path d="M4 16l4-4 3 3 5-5 4 4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>',
  file:
    '<path d="M7 4h7l4 4v10a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2Z" stroke="currentColor" stroke-width="1.6" fill="none"/><path d="M14 4v4h4" stroke="currentColor" stroke-width="1.6"/>',
  chat:
    '<path d="M4 6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-3l-3 3-3-3H6a2 2 0 0 1-2-2V6Z" stroke="currentColor" stroke-width="1.6" fill="none"/><path d="M8 9h8M8 12h5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
  download:
    '<path d="M12 4v12M12 16l-4-4M12 16l4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M5 18h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
  cloud:
    '<path d="M18 15a4 4 0 0 0-4-4 6 6 0 0 0-12 2 4 4 0 0 0 0 8h16a4 4 0 0 0 0-8Z" stroke="currentColor" stroke-width="1.6" fill="none"/>',
  trash:
    '<path d="M6 7h12M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><path d="M7 7v10a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V7" stroke="currentColor" stroke-width="1.6"/><path d="M10 10v5M14 10v5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>'
}

const cls = computed(() => props.class || '')
</script>
