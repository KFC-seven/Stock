<script setup lang="ts">
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import { holdingsApi } from '../../api/holdings'

const ocrResult = ref('')
const recognizedRows = ref<Array<Record<string, string>>>([])
const recognizing = ref(false)
const importing = ref(false)
const fileList = ref<any[]>([])

function handleFileChange(info: any) {
  fileList.value = info.fileList.slice(-1)
}

async function handleRecognize() {
  if (fileList.value.length === 0) {
    message.warning('请先选择图片文件')
    return
  }
  recognizing.value = true
  ocrResult.value = ''
  recognizedRows.value = []
  try {
    // OCR API call placeholder — will be replaced when backend is ready
    // For now, simulate a delay and show a placeholder message
    await new Promise((resolve) => setTimeout(resolve, 1000))
    ocrResult.value = 'OCR识别功能待后端实现。\n\n上传图片后，系统将自动识别图片中的持仓信息，\n包括证券代码、名称、数量、价格等字段。'
    message.info('OCR识别服务尚未接入')
  } catch (e: any) {
    message.error(e.response?.data?.detail || '识别失败')
  } finally {
    recognizing.value = false
  }
}

async function handleImport() {
  if (recognizedRows.value.length === 0) {
    message.warning('没有可导入的数据，请先识别')
    return
  }
  importing.value = true
  try {
    let imported = 0
    for (const row of recognizedRows.value) {
      await holdingsApi.create({
        asset_type: row.type || 'stock',
        asset_code: row.code || '',
        asset_name: row.name || '',
        quantity: parseFloat(row.quantity) || 0,
        cost_price: parseFloat(row.cost_price) || 0,
      })
      imported++
    }
    message.success(`成功导入 ${imported} 条持仓记录`)
    ocrResult.value = ''
    recognizedRows.value = []
    fileList.value = []
  } catch (e: any) {
    message.error(e.response?.data?.detail || '导入失败')
  } finally {
    importing.value = false
  }
}

async function handleBeforeUpload(file: File) {
  // Validate file type
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    message.error('只能上传图片文件')
    return false
  }
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    message.error('图片大小不能超过 10MB')
    return false
  }
  // Return false to prevent auto-upload — we handle it manually
  return false
}
</script>

<template>
  <div>
    <div style="margin-bottom:16px;">
      <h2 style="color:#fff;margin:0;">导入持仓</h2>
    </div>

    <a-row :gutter="[16, 16]">
      <a-col :xs="24" :md="12">
        <a-card :bordered="false" title="上传截图" style="background:rgba(255,255,255,0.03);border-radius:12px;">
          <a-upload-dragger
            v-model:fileList="fileList"
            :before-upload="handleBeforeUpload"
            :multiple="false"
            :show-upload-list="true"
            @change="handleFileChange"
            accept="image/*"
            style="margin-bottom:16px;"
          >
            <p style="font-size:48px;color:rgba(255,255,255,0.25);margin-bottom:8px;">
              <InboxOutlined />
            </p>
            <p style="color:rgba(255,255,255,0.65);">点击或拖拽图片到此区域上传</p>
            <p style="color:rgba(255,255,255,0.35);font-size:12px;">支持 PNG、JPG 格式，单张不超过 10MB</p>
          </a-upload-dragger>

          <a-button
            type="primary"
            :loading="recognizing"
            :disabled="fileList.length === 0"
            block
            size="large"
            @click="handleRecognize"
          >
            <template #icon><ScanOutlined /></template>
            {{ recognizing ? '识别中...' : '开始识别' }}
          </a-button>
        </a-card>
      </a-col>

      <a-col :xs="24" :md="12">
        <a-card :bordered="false" title="识别结果" style="background:rgba(255,255,255,0.03);border-radius:12px;">
          <a-textarea
            v-model:value="ocrResult"
            :rows="10"
            placeholder="识别结果将在此显示..."
            :disabled="recognizing"
            style="margin-bottom:16px;font-family:monospace;"
          />

          <a-button
            type="primary"
            :loading="importing"
            :disabled="!ocrResult || recognizedRows.length === 0"
            block
            size="large"
            @click="handleImport"
          >
            <template #icon><ImportOutlined /></template>
            {{ importing ? '导入中...' : '导入到持仓' }}
          </a-button>

          <a-alert
            v-if="recognizedRows.length > 0"
            type="success"
            :message="`识别到 ${recognizedRows.length} 条记录`"
            show-icon
            style="margin-top:12px;"
          />
        </a-card>
      </a-col>
    </a-row>

    <!-- Instructions -->
    <a-card :bordered="false" style="background:rgba(255,255,255,0.03);border-radius:12px;margin-top:16px;">
      <a-collapse ghost expand-icon-position="right">
        <a-collapse-panel key="help" header="使用说明">
          <ol style="color:rgba(255,255,255,0.65);padding-left:20px;line-height:2;">
            <li>截取券商App或交易软件的持仓页面截图</li>
            <li>上传截图（支持 PNG / JPG 格式）</li>
            <li>点击"开始识别"进行 OCR 文字识别</li>
            <li>核对识别结果，然后点击"导入到持仓"</li>
          </ol>
        </a-collapse-panel>
      </a-collapse>
    </a-card>
  </div>
</template>

<script lang="ts">
import { InboxOutlined, ScanOutlined, ImportOutlined } from '@ant-design/icons-vue'
export default {
  components: { InboxOutlined, ScanOutlined, ImportOutlined },
}
</script>

<style scoped>
:deep(.ant-card-head-title) {
  color: rgba(255,255,255,0.85);
}
:deep(.ant-upload-drag) {
  background: rgba(255,255,255,0.02) !important;
  border-color: rgba(255,255,255,0.1) !important;
}
:deep(.ant-upload-drag:hover) {
  border-color: #1677ff !important;
}
</style>
