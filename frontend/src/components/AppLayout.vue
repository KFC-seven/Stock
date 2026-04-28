<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const user = useUserStore()

const menuItems = [
  { key: '/dashboard', icon: '📊', label: '投资看板' },
  { key: '/holdings', icon: '📈', label: '持仓管理' },
  { key: '/family', icon: '👨‍👩‍👧‍👦', label: '家庭看板' },
  { key: '/ocr', icon: '📷', label: '导入持仓' },
  { key: '/settings', icon: '⚙️', label: '设置' },
]

function navigate(path: string) {
  router.push(path)
}

function handleLogout() {
  user.logout()
  router.push('/login')
}
</script>

<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider theme="dark" width="220" collapsible>
      <div class="logo">
        <span>📊 投资管家</span>
      </div>
      <a-menu theme="dark" mode="inline" :selected-keys="[router.currentRoute.value.path]">
        <a-menu-item v-for="item in menuItems" :key="item.key" @click="navigate(item.key)">
          <span>{{ item.icon }} {{ item.label }}</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header style="background: #141414; padding: 0 24px; display: flex; align-items: center; justify-content: flex-end; gap: 16px;">
        <span style="color: rgba(255,255,255,0.65);">👋 {{ user.displayName }}</span>
        <a-button size="small" @click="handleLogout">退出</a-button>
      </a-layout-header>
      <a-layout-content style="margin: 16px; padding: 24px; background: #141414; border-radius: 12px; min-height: 360px;">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<style scoped>
.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
</style>
