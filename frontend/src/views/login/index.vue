<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { message } from 'ant-design-vue'

const router = useRouter()
const user = useUserStore()
const activeTab = ref('login')
const username = ref('')
const password = ref('')
const displayName = ref('')
const loading = ref(false)

async function handleSubmit() {
  loading.value = true
  try {
    if (activeTab.value === 'register') {
      await user.register({ username: username.value, password: password.value, display_name: displayName.value })
      message.success('注册成功')
    } else {
      await user.login({ username: username.value, password: password.value })
    }
    router.push('/dashboard')
  } catch (e: any) {
    message.error(e.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-wrapper">
    <div class="login-card">
      <h1 style="text-align:center;margin-bottom:32px;font-size:28px;letter-spacing:-0.5px;background:linear-gradient(135deg,#fff 0%,#8a94b0 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📊 投资管家</h1>
      <a-tabs v-model:activeKey="activeTab">
        <a-tab-pane key="login" tab="登录">
          <a-form @finish="handleSubmit" :model="{ username, password }">
            <a-form-item name="username" :rules="[{ required: true, message: '请输入用户名' }]">
              <a-input v-model:value="username" placeholder="用户名" size="large" />
            </a-form-item>
            <a-form-item name="password" :rules="[{ required: true, message: '请输入密码' }]">
              <a-input-password v-model:value="password" placeholder="密码" size="large" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" html-type="submit" :loading="loading" block size="large">登录</a-button>
            </a-form-item>
          </a-form>
        </a-tab-pane>
        <a-tab-pane key="register" tab="注册">
          <a-form @finish="handleSubmit" :model="{ r_user: username, r_name: displayName, r_pass: password }">
            <a-form-item name="r_user" :rules="[{ required: true, message: '请输入用户名' }]">
              <a-input v-model:value="username" placeholder="用户名" size="large" />
            </a-form-item>
            <a-form-item name="r_name" :rules="[{ required: true, message: '请输入显示名称' }]">
              <a-input v-model:value="displayName" placeholder="显示名称（如：张三）" size="large" />
            </a-form-item>
            <a-form-item name="r_pass" :rules="[{ required: true, message: '请输入密码' }]">
              <a-input-password v-model:value="password" placeholder="密码" size="large" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" html-type="submit" :loading="loading" block size="large">注册并登录</a-button>
            </a-form-item>
          </a-form>
        </a-tab-pane>
      </a-tabs>
    </div>
  </div>
</template>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0a0b0f 0%, #0f1219 30%, #13172a 60%, #0d1020 100%);
}
.login-card {
  width: 400px;
  padding: 40px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 20px;
  backdrop-filter: blur(40px);
}
</style>
