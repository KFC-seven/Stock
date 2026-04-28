import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/login/index.vue'), meta: { public: true } },
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: () => import('../views/dashboard/index.vue') },
  { path: '/holdings', name: 'Holdings', component: () => import('../views/holdings/index.vue') },
  { path: '/family', name: 'Family', component: () => import('../views/family/index.vue') },
  { path: '/ocr', name: 'OCR', component: () => import('../views/ocr/index.vue') },
  { path: '/settings', name: 'Settings', component: () => import('../views/settings/index.vue') },
]

const router = createRouter({ history: createWebHashHistory(), routes })

router.beforeEach((to) => {
  if (to.meta.public) return true
  const store = useUserStore()
  if (!store.loggedIn) return '/login'
  return true
})

export default router
