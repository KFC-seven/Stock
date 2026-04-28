<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { holdingsApi, type HoldingItem, type HoldingCreate } from '../../api/holdings'
import { marketApi, type SearchResult } from '../../api/market'

const holdings = ref<HoldingItem[]>([])
const loading = ref(false)
const modalVisible = ref(false)
const editingId = ref<number | null>(null)
const formLoading = ref(false)

// Form model
const formModel = ref<HoldingCreate>({
  asset_type: 'stock',
  asset_code: '',
  asset_name: '',
  quantity: 0,
  cost_price: 0,
  buy_date: undefined,
  notes: '',
})

// Search
const searchKeyword = ref('')
const searchResults = ref<SearchResult[]>([])
const searchDropdownVisible = ref(false)
let searchTimer: ReturnType<typeof setTimeout> | null = null

const columns = [
  { title: '类型', dataIndex: 'asset_type', key: 'asset_type', width: 80 },
  { title: '代码', dataIndex: 'asset_code', key: 'asset_code', width: 110 },
  { title: '名称', dataIndex: 'asset_name', key: 'asset_name' },
  { title: '数量', dataIndex: 'quantity', key: 'quantity', width: 100, align: 'right' as const },
  { title: '成本价', dataIndex: 'cost_price', key: 'cost_price', width: 110, align: 'right' as const },
  { title: '现价', dataIndex: 'current_price', key: 'current_price', width: 110, align: 'right' as const },
  { title: '盈亏', dataIndex: 'profit', key: 'profit', width: 120, align: 'right' as const },
  { title: '操作', key: 'action', width: 160, fixed: 'right' as const },
]

const typeOptions = [
  { value: 'stock', label: '股票' },
  { value: 'fund', label: '基金' },
  { value: 'etf', label: 'ETF' },
  { value: 'bond', label: '债券' },
  { value: 'other', label: '其他' },
]

async function loadHoldings() {
  loading.value = true
  try {
    const res = await holdingsApi.list()
    holdings.value = res.data
  } catch (e: any) {
    message.error(e.response?.data?.detail || '加载持仓失败')
  } finally {
    loading.value = false
  }
}

function openAddModal() {
  editingId.value = null
  formModel.value = {
    asset_type: 'stock',
    asset_code: '',
    asset_name: '',
    quantity: 0,
    cost_price: 0,
    buy_date: undefined,
    notes: '',
  }
  searchKeyword.value = ''
  searchResults.value = []
  modalVisible.value = true
}

function openEditModal(record: HoldingItem) {
  editingId.value = record.id
  formModel.value = {
    asset_type: record.asset_type,
    asset_code: record.asset_code,
    asset_name: record.asset_name,
    quantity: record.quantity,
    cost_price: record.cost_price,
    buy_date: record.buy_date || undefined,
    notes: record.notes,
  }
  searchKeyword.value = record.asset_name
  modalVisible.value = true
}

function handleSearchInput(val: string) {
  searchKeyword.value = val
  if (searchTimer) clearTimeout(searchTimer)
  if (!val || val.trim().length < 1) {
    searchResults.value = []
    searchDropdownVisible.value = false
    return
  }
  searchTimer = setTimeout(async () => {
    try {
      const res = await marketApi.search(val.trim())
      searchResults.value = res.data
      searchDropdownVisible.value = searchResults.value.length > 0
    } catch {
      searchResults.value = []
    }
  }, 300)
}

function selectSearchResult(item: SearchResult) {
  formModel.value.asset_type = item.type
  formModel.value.asset_code = item.code
  formModel.value.asset_name = item.name
  searchKeyword.value = item.name
  searchDropdownVisible.value = false
}

async function handleSubmit() {
  formLoading.value = true
  try {
    if (editingId.value !== null) {
      await holdingsApi.update(editingId.value, formModel.value)
      message.success('更新成功')
    } else {
      await holdingsApi.create(formModel.value)
      message.success('添加成功')
    }
    modalVisible.value = false
    await loadHoldings()
  } catch (e: any) {
    message.error(e.response?.data?.detail || '保存失败')
  } finally {
    formLoading.value = false
  }
}

function confirmDelete(record: HoldingItem) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除 ${record.asset_name} (${record.asset_code}) 吗？`,
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: async () => {
      try {
        await holdingsApi.delete(record.id)
        message.success('删除成功')
        await loadHoldings()
      } catch (e: any) {
        message.error(e.response?.data?.detail || '删除失败')
      }
    },
  })
}

function formatMoney(val: number): string {
  return '¥' + val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

onMounted(() => {
  loadHoldings()
})
</script>

<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
      <h2 style="color:#fff;margin:0;">持仓管理</h2>
      <a-button type="primary" @click="openAddModal">
        <template #icon><PlusOutlined /></template>
        添加持仓
      </a-button>
    </div>

    <a-card :bordered="false" style="background:rgba(255,255,255,0.03);border-radius:12px;">
      <a-table
        :dataSource="holdings"
        :columns="columns"
        :loading="loading"
        rowKey="id"
        :pagination="{ pageSize: 10, showSizeChanger: true, showTotal: (t: number) => `共 ${t} 条` }"
        :locale="{ emptyText: '暂无持仓数据' }"
        :scroll="{ x: 800 }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'profit'">
            <span :style="{ color: record.profit >= 0 ? '#3fb68b' : '#ff4d4f' }">
              {{ formatMoney(record.profit) }}
            </span>
          </template>
          <template v-else-if="column.key === 'cost_price'">
            {{ formatMoney(record.cost_price) }}
          </template>
          <template v-else-if="column.key === 'current_price'">
            {{ formatMoney(record.current_price) }}
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="openEditModal(record)">编辑</a-button>
              <a-button type="link" danger size="small" @click="confirmDelete(record)">删除</a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- Add / Edit Modal -->
    <a-modal
      v-model:visible="modalVisible"
      :title="editingId ? '编辑持仓' : '添加持仓'"
      :confirm-loading="formLoading"
      :destroy-on-close="true"
      @ok="handleSubmit"
      ok-text="保存"
      cancel-text="取消"
    >
      <a-form layout="vertical" :model="formModel">
        <!-- Asset search -->
        <a-form-item label="搜索证券">
          <a-auto-complete
            v-model:value="searchKeyword"
            :options="searchResults.map(r => ({ value: `${r.name} (${r.code})`, label: `${r.type_label} ${r.name} (${r.code})` }))"
            style="width:100%"
            placeholder="输入代码或名称搜索"
            @search="handleSearchInput"
            @select="(val: any) => {
              const idx = searchResults.findIndex(r => `${r.name} (${r.code})` === val)
              if (idx >= 0) selectSearchResult(searchResults[idx])
            }"
          />
        </a-form-item>

        <a-form-item label="类型" name="asset_type" :rules="[{ required: true, message: '请选择类型' }]">
          <a-select v-model:value="formModel.asset_type" :options="typeOptions" style="width:100%" />
        </a-form-item>

        <a-form-item label="代码" name="asset_code" :rules="[{ required: true, message: '请输入代码' }]">
          <a-input v-model:value="formModel.asset_code" placeholder="如: 600000" />
        </a-form-item>

        <a-form-item label="名称" name="asset_name">
          <a-input v-model:value="formModel.asset_name" placeholder="证券名称" />
        </a-form-item>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="数量" name="quantity" :rules="[{ required: true, message: '请输入数量' }]">
              <a-input-number v-model:value="formModel.quantity" :min="0" :precision="0" style="width:100%" placeholder="持仓数量" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="成本价" name="cost_price" :rules="[{ required: true, message: '请输入成本价' }]">
              <a-input-number v-model:value="formModel.cost_price" :min="0" :precision="4" style="width:100%" placeholder="买入均价" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="买入日期" name="buy_date">
          <a-date-picker v-model:value="formModel.buy_date" style="width:100%" placeholder="选择日期" />
        </a-form-item>

        <a-form-item label="备注" name="notes">
          <a-textarea v-model:value="formModel.notes" :rows="2" placeholder="可选备注" />
        </a-form-item>
      </a-form>
    </a-modal>
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
:deep(.ant-table) {
  background: transparent;
}
</style>
