<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()

// News keywords
const keywords = ref<string[]>([])
const newKeyword = ref('')

function addKeyword() {
  const trimmed = newKeyword.value.trim()
  if (!trimmed) {
    message.warning('请输入关键词')
    return
  }
  if (keywords.value.includes(trimmed)) {
    message.warning('该关键词已存在')
    return
  }
  keywords.value.push(trimmed)
  newKeyword.value = ''
  saveKeywords()
  message.success('已添加关键词')
}

function removeKeyword(index: number) {
  keywords.value.splice(index, 1)
  saveKeywords()
  message.success('已删除关键词')
}

function saveKeywords() {
  localStorage.setItem('news_keywords', JSON.stringify(keywords.value))
}

function loadKeywords() {
  try {
    const saved = localStorage.getItem('news_keywords')
    if (saved) {
      keywords.value = JSON.parse(saved)
    }
  } catch {
    keywords.value = []
  }
}

onMounted(() => {
  loadKeywords()
})
</script>

<template>
  <div>
    <div style="margin-bottom:16px;">
      <h2 style="color:#fff;margin:0;">设置</h2>
    </div>

    <a-row :gutter="[16, 16]">
      <!-- User Info -->
      <a-col :xs="24" :md="12">
        <a-card :bordered="false" title="用户信息" style="background:rgba(255,255,255,0.03);border-radius:12px;">
          <a-descriptions :column="1" :label-style="{ color: 'rgba(255,255,255,0.45)' }" :content-style="{ color: 'rgba(255,255,255,0.85)' }">
            <a-descriptions-item label="用户ID">
              <a-tag color="blue">{{ userStore.userId }}</a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="显示名称">
              {{ userStore.displayName || '未设置' }}
            </a-descriptions-item>
            <a-descriptions-item label="登录状态">
              <a-tag color="green">已登录</a-tag>
            </a-descriptions-item>
          </a-descriptions>
        </a-card>
      </a-col>

      <!-- News keywords -->
      <a-col :xs="24" :md="12">
        <a-card :bordered="false" title="新闻关键词" style="background:rgba(255,255,255,0.03);border-radius:12px;">
          <div style="display:flex;gap:8px;margin-bottom:16px;">
            <a-input
              v-model:value="newKeyword"
              placeholder="输入关键词，如: 茅台"
              @press-enter="addKeyword"
              style="flex:1;"
            />
            <a-button type="primary" @click="addKeyword">
              <template #icon><PlusOutlined /></template>
              添加
            </a-button>
          </div>

          <div v-if="keywords.length === 0" style="color:rgba(255,255,255,0.35);text-align:center;padding:24px 0;">
            暂无关键词，添加后可接收相关新闻推送
          </div>

          <a-space wrap v-else>
            <a-tag
              v-for="(kw, index) in keywords"
              :key="index"
              closable
              @close="removeKeyword(index)"
              style="padding:4px 8px;font-size:14px;margin-bottom:8px;"
            >
              {{ kw }}
            </a-tag>
          </a-space>

          <a-divider style="border-color:rgba(255,255,255,0.06);" />
          <div style="color:rgba(255,255,255,0.35);font-size:12px;">
            设置关注的关键词，系统将推送相关财经新闻
          </div>
        </a-card>
      </a-col>

      <!-- About -->
      <a-col :span="24">
        <a-card :bordered="false" title="关于" style="background:rgba(255,255,255,0.03);border-radius:12px;">
          <a-descriptions :column="1" :label-style="{ color: 'rgba(255,255,255,0.45)' }" :content-style="{ color: 'rgba(255,255,255,0.85)' }">
            <a-descriptions-item label="应用名称">投资管家</a-descriptions-item>
            <a-descriptions-item label="版本">1.0.0</a-descriptions-item>
            <a-descriptions-item label="技术栈">Vue 3 + TypeScript + Ant Design Vue + ECharts</a-descriptions-item>
            <a-descriptions-item label="说明">
              个人投资组合管理工具，支持多用户、家庭看板、持仓管理、盈亏分析等功能。
            </a-descriptions-item>
          </a-descriptions>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script lang="ts">
import { PlusOutlined } from '@ant-design/icons-vue'
export default {
  components: { PlusOutlined },
}
</script>

<style scoped>
:deep(.ant-card-head-title) {
  color: rgba(255,255,255,0.85);
}
:deep(.ant-descriptions-item-label) {
  color: rgba(255,255,255,0.45) !important;
}
:deep(.ant-descriptions-item-content) {
  color: rgba(255,255,255,0.85) !important;
}
:deep(.ant-tag) {
  background: rgba(22,119,255,0.15);
  border-color: rgba(22,119,255,0.3);
  color: #fff;
}
</style>
