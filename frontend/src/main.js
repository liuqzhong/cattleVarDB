/**
 * ============================================
 * Cattle SNP Effect Database - Frontend Entry Point
 * ============================================
 */

import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import en from 'element-plus/dist/locale/en.mjs'

import App from './App.vue'
import router from './router'
import './styles/main.css'

const app = createApp(App)

// Register Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus, { locale: en })
app.use(router)
app.mount('#app')
