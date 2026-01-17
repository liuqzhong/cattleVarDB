/**
 * ============================================
 * Vue Router Configuration
 * ============================================
 */

import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue'),
    meta: { title: 'Cattle SNP Effect Database' }
  },
  {
    path: '/snps',
    name: 'SNPList',
    component: () => import('../views/SNPTableView.vue'),
    meta: { title: 'SNP Database' }
  },
  {
    path: '/sv',
    name: 'SV',
    component: () => import('../views/SVView.vue'),
    meta: { title: 'Structural Variants' }
  },
  {
    path: '/download',
    name: 'Download',
    component: () => import('../views/DownloadView.vue'),
    meta: { title: 'Download Center' }
  },
  {
    path: '/help',
    name: 'Help',
    component: () => import('../views/HelpView.vue'),
    meta: { title: 'Help & Documentation' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Set page title
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'Cattle SNP Effect Database'
  next()
})

export default router
