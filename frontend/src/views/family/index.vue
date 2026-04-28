<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { message } from 'ant-design-vue'
import * as echarts from 'echarts'
import { holdingsApi } from '../../api/holdings'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()

interface FamilyMember {
  user_id: number
  username: string
  display_name: string
  total_cost: number
  total_value: number
  total_profit: number
  total_profit_pct: number
  holdings: Array<{
    asset_type: string
    asset_code: string
    asset_name: string
    quantity: number
    cost_price: number
    current_price: number
    cost: number
    value: number
    profit: number
    profit_pct: number
  }>
}

interface FamilyData {
  members: FamilyMember[]
  total_cost: number
  total_value: number
  total_profit: number
  total_profit_pct: number
  distribution: Record<string, { value: number; cost: number; profit: number }>
}

const familyData = ref<FamilyData | null>(null)
const loading = ref(false)
let pieChart: echarts.ECharts | null = null

async function loadFamilyData() {
  loading.value = true
  try {
    const res = await holdingsApi.family()
    familyData.value = res.data as unknown as FamilyData
    await nextTick()
    renderPieChart()
  } catch (e: any) {
    message.error(e.response?.data?.detail || '加载家庭数据失败')
  } finally {
    loading.value = false
  }
}

function renderPieChart() {
  const el = document.getElementById('familyPie')
  if (!el || !familyData.value) return
  if (pieChart) pieChart.dispose()
  pieChart = echarts.init(el)

  const dist = familyData.value.distribution
  const pieData = Object.entries(dist).map(([key, val]) => ({
    name: key,
    value: Math.round(val.value * 100) / 100,
  }))

  pieChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
    series: [{
      type: 'pie',
      radius: ['30%', '60%'],
      center: ['50%', '50%'],
      roseType: 'area',
      itemStyle: { borderRadius: 4 },
      data: pieData.length ? pieData : [{ name: '暂无数据', value: 1 }],
      label: { color: 'rgba(255,255,255,0.85)', fontSize: 12 },
    }],
  })
}

function formatMoney(val: number): string {
  return '¥' + val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function isCurrentUser(userId: number): boolean {
  return userStore.userId === userId
}

onMounted(() => {
  loadFamilyData()
})

onUnmounted(() => {
  pieChart?.dispose()
})
</script>

<template>
  <div>
    <div style="margin-bottom:16px;">
      <h2 style="color:#fff;margin:0;">家庭看板</h2>
    </div>

    <a-card v-if="!familyData && !loading" :bordered="false" style="background:rgba(255,255,255,0.03);border-radius:12px;">
      <a-empty description="暂无家庭数据" />
    </a-card>

    <template v-if="familyData">
      <!-- Family total metrics -->
      <a-row :gutter="[16, 16]" style="margin-bottom:16px;">
        <a-col :xs="12" :sm="6">
          <a-card :bordered="false" style="background:rgba(255,255,255,0.03);border-radius:12px;">
            <a-statistic title="家庭总市值" :value="familyData.total_value" :precision="2" prefix="¥" :value-style="{ color: '#1677ff' }" />
          </a-card>
        </a-col>
        <a-col :xs="12" :sm="6">
          <a-card :bordered="false" style="background:rgba(255,255,255,0.03);border-radius:12px;">
            <a-statistic title="家庭总成本" :value="familyData.total_cost" :precision="2" prefix="¥" />
          </a-card>
        </a-col>
        <a-col :xs="12" :sm="6">
          <a-card :bordered="false" style="background:rgba(255,255,255,0.03);border-radius:12px;">
            <a-statistic
              title="家庭总盈亏"
              :value="familyData.total_profit"
              :precision="2"
              prefix="¥"
              :value-style="{ color: familyData.total_profit >= 0 ? '#3fb68b' : '#ff4d4f' }"
            />
          </a-card>
        </a-col>
        <a-col :xs="12" :sm="6">
          <a-card :bordered="false" style="background:rgba(255,255,255,0.03);border-radius:12px;">
            <a-statistic
              title="家庭收益率"
              :value="familyData.total_profit_pct"
              :precision="2"
              suffix="%"
              :value-style="{ color: familyData.total_profit_pct >= 0 ? '#3fb68b' : '#ff4d4f' }"
            />
          </a-card>
        </a-col>
      </a-row>

      <!-- Pie chart -->
      <a-row :gutter="[16, 16]" style="margin-bottom:16px;">
        <a-col :span="24">
          <a-card :bordered="false" title="家庭资产分布" style="background:rgba(255,255,255,0.03);border-radius:12px;">
            <div id="familyPie" style="width:100%;height:360px;"></div>
          </a-card>
        </a-col>
      </a-row>

      <!-- Per-user breakdown -->
      <a-row :gutter="[16, 16]">
        <a-col :span="24" v-for="member in familyData.members" :key="member.user_id">
          <a-card
            :bordered="false"
            :title="`${member.display_name}${isCurrentUser(member.user_id) ? ' (我)' : ''}`"
            style="background:rgba(255,255,255,0.03);border-radius:12px;margin-bottom:16px;"
          >
            <a-row :gutter="[16, 16]" style="margin-bottom:16px;">
              <a-col :xs="12" :sm="6">
                <a-statistic title="市值" :value="member.total_value" :precision="2" prefix="¥" />
              </a-col>
              <a-col :xs="12" :sm="6">
                <a-statistic title="成本" :value="member.total_cost" :precision="2" prefix="¥" />
              </a-col>
              <a-col :xs="12" :sm="6">
                <a-statistic
                  title="盈亏"
                  :value="member.total_profit"
                  :precision="2"
                  prefix="¥"
                  :value-style="{ color: member.total_profit >= 0 ? '#3fb68b' : '#ff4d4f' }"
                />
              </a-col>
              <a-col :xs="12" :sm="6">
                <a-statistic
                  title="收益率"
                  :value="member.total_profit_pct"
                  :precision="2"
                  suffix="%"
                  :value-style="{ color: member.total_profit_pct >= 0 ? '#3fb68b' : '#ff4d4f' }"
                />
              </a-col>
            </a-row>

            <a-table
              :dataSource="member.holdings"
              :columns="memberColumns"
              rowKey="asset_code"
              :pagination="false"
              :locale="{ emptyText: '暂无持仓' }"
              size="small"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'profit'">
                  <span :style="{ color: record.profit >= 0 ? '#3fb68b' : '#ff4d4f' }">
                    {{ formatMoney(record.profit) }}
                  </span>
                </template>
                <template v-else-if="column.key === 'profit_pct'">
                  <span :style="{ color: record.profit_pct >= 0 ? '#3fb68b' : '#ff4d4f' }">
                    {{ record.profit_pct.toFixed(2) }}%
                  </span>
                </template>
                <template v-else-if="column.key === 'value'">
                  {{ formatMoney(record.value) }}
                </template>
                <template v-else-if="['cost_price', 'current_price'].includes(column.key)">
                  {{ formatMoney(record[column.key]) }}
                </template>
              </template>
            </a-table>
          </a-card>
        </a-col>
      </a-row>
    </template>
  </div>
</template>

<script lang="ts">
export default {
  computed: {
    memberColumns() {
      return [
        { title: '类型', dataIndex: 'asset_type', key: 'asset_type', width: 70 },
        { title: '代码', dataIndex: 'asset_code', key: 'asset_code', width: 90 },
        { title: '名称', dataIndex: 'asset_name', key: 'asset_name' },
        { title: '数量', dataIndex: 'quantity', key: 'quantity', width: 80, align: 'right' as const },
        { title: '成本价', dataIndex: 'cost_price', key: 'cost_price', width: 100, align: 'right' as const },
        { title: '现价', dataIndex: 'current_price', key: 'current_price', width: 100, align: 'right' as const },
        { title: '市值', dataIndex: 'value', key: 'value', width: 110, align: 'right' as const },
        { title: '盈亏', dataIndex: 'profit', key: 'profit', width: 110, align: 'right' as const },
        { title: '收益率', dataIndex: 'profit_pct', key: 'profit_pct', width: 90, align: 'right' as const },
      ]
    },
  },
}
</script>

<style scoped>
:deep(.ant-card-head-title) {
  color: rgba(255,255,255,0.85);
}
:deep(.ant-statistic-title) {
  color: rgba(255,255,255,0.45);
}
:deep(.ant-table) {
  background: transparent;
}
</style>
