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
    meta: { title: 'SNPs - Search Activity Difference' }
  },
  {
    path: '/indels',
    name: 'IndelList',
    component: () => import('../views/IndelTableView.vue'),
    meta: { title: 'Indels - Search Activity Difference' }
  },
  {
    path: '/svs',
    name: 'SVList',
    component: () => import('../views/SVTableView.vue'),
    meta: { title: 'SVs - Search Activity Difference' }
  },
  {
    path: '/exp-snps',
    name: 'ExpSNPList',
    component: () => import('../views/ExpSNPTableView.vue'),
    meta: { title: 'SNPs - Search Expression Difference' }
  },
  {
    path: '/exp-indels',
    name: 'ExpIndelList',
    component: () => import('../views/ExpIndelTableView.vue'),
    meta: { title: 'Indels - Search Expression Difference' }
  },
  {
    path: '/exp-svs',
    name: 'ExpSVList',
    component: () => import('../views/ExpSVTableView.vue'),
    meta: { title: 'SVs - Search Expression Difference' }
  },
  {
    path: '/sv',
    name: 'SV',
    component: () => import('../views/SVView.vue'),
    meta: { title: 'Search Expression Difference' }
  },
  {
    path: '/prediction',
    name: 'Prediction',
    component: () => import('../views/PredictionView.vue'),
    meta: { title: 'Prediction' }
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
