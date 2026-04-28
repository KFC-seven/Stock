<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from './stores/user'
import AppLayout from './components/AppLayout.vue'

const route = useRoute()
const user = useUserStore()
const isLoginPage = computed(() => route.path === '/login')
</script>

<template>
  <a-config-provider :theme="{ algorithm: theme.darkAlgorithm }" v-if="false">
  </a-config-provider>
  <AppLayout v-if="user.loggedIn && !isLoginPage" />
  <router-view v-else />
</template>

<script lang="ts">
import { theme } from 'ant-design-vue'
export default { name: 'App' }
</script>
