<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { message } from 'ant-design-vue'
import * as echarts from 'echarts'
import { holdingsApi, type HoldingItem } from '../../api/holdings'

const holdings = ref<HoldingItem[]>([])
const totalCost = ref(0)
const totalValue = ref(0)
const totalProfit = ref(0)
const profitPct = ref(0)
const distribution = ref<Record<string, { value: number; cost: number; profit: number }>>({})
const loading = ref(false)
const refreshing = ref(false)

let pieChart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null

async function loadData() {
  loading.value = true
  try {
    const [listRes, summaryRes] = await Promise.all([
      holdingsApi.list(),
      holdingsApi.summary(),
    ])
    holdings.value = listRes.data
    const portfolio = summaryRes.data.portfolio
    totalCost.value = portfolio.total_cost
    totalValue.value = portfolio.total_value
    totalProfit.value = portfolio.total_profit
    profitPct.value = portfolio.total_profit_pct
    distribution.value = summaryRes.data.distribution

    await nextTick()
    renderCharts()
  } catch (e: any) {
    message.error(e.response?.data?.detail || '加载数据失败')
  } finally {
    loading.value = false
  }
}

async function handleRefreshPrices() {
  refreshing.value = true
  try {
    const res = await holdingsApi.refreshPrices()
    const count = res.data?.results?.updated ?? res.data?.results ?? 0
    message.success(`价格刷新完成，共更新 ${count} 条`)
    await loadData()
  } catch (e: any) {
    message.error(e.response?.data?.detail || '刷新价格失败')
  } finally {
    refreshing.value = false
  }
}

function renderCharts() {
  // Pie chart - asset distribution
  const pieEl = document.getElementById('distributionPie')
  if (pieEl) {
    if (pieChart) pieChart.dispose()
    pieChart = echarts.init(pieEl)
    const pieData = Object.entries(distribution.value).map(([key, val]) => ({
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

  // Bar chart - individual holding profits
  const barEl = document.getElementById('profitBar')
  if (barEl) {
    if (barChart) barChart.dispose()
    barChart = echarts.init(barEl)
    const names = holdings.value.map(h => h.asset_name)
    const profits = holdings.value.map(h => Math.round(h.profit * 100) / 100)
    barChart.setOption({
      tooltip: { trigger: 'axis', formatter: '{b}: ¥{c}' },
      grid: { left: 60, right: 20, top: 40, bottom: 40 },
      xAxis: {
        type: 'category',
        data: names,
        axisLabel: { color: 'rgba(255,255,255,0.65)', rotate: 30, fontSize: 10 },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: 'rgba(255,255,255,0.65)' },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } },
      },
      series: [{
        type: 'bar',
        data: profits,
        itemStyle: {
          color: (params: any) => (params.value >= 0 ? '#3fb68b' : '#ff4d4f'),
          borderRadius: [4, 4, 0, 0],
        },
      }],
    })
  }
}

function formatMoney(val: number): string {
  return '¥' + val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

onMounted(() => {
  loadData()
})

onUnmounted(() => {
  pieChart?.dispose()
  barChart?.dispose()
})
</script>

<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
      <h2 style="color:#fff;margin:0;">投资看板</h2>
      <a-button type="primary" :loading="refreshing" @click="handleRefreshPrices">
        <template #icon><ReloadOutlined /></template>
        刷新价格
      </a-button>
    </div>

    <!-- Metric cards -->
    <a-row :gutter="[16, 16]" style="margin-bottom:16px;">
      <a-col :xs="12" :sm="6">
        <a-card :bordered="false" style="background:rgba(255,255,255,0.03);border-radius:12px;">
          <a-statistic title="总市值" :value="totalValue" :precision="2" prefix="¥" :value-style="{ color: '#1677ff' }" />
        </a-card>
      </a-col>
      <a-col :xs="12" :sm="6">
        <a-card :bordered="false" style="background:rgba(255,255,255,0.03);border-radius:12px;">
          <a-statistic title="总成本" :value="totalCost" :precision="2" prefix="¥" />
        </a-card>
      </a-col>
      <a-col :xs="12" :sm="6">
        <a-card :bordered="false" style="background:rgba(255,255,255,0.03);border-radius:12px;">
          <a-statistic
            title="总盈亏"
            :value="totalProfit"
            :precision="2"
            prefix="¥"
            :value-style="{ color: totalProfit >= 0 ? '#3fb68b' : '#ff4d4f' }"
          />
        </a-card>
      </a-col>
      <a-col :xs="12" :sm="6">
        <a-card :bordered="false" style="background:rgba(255,255,255,0.03);border-radius:12px;">
          <a-statistic
            title="收益率"
            :value="profitPct"
            :precision="2"
            suffix="%"
            :value-style="{ color: profitPct >= 0 ? '#3fb68b' : '#ff4d4f' }"
          />
        </a-card>
      </a-col>
    </a-row>

    <!-- Charts -->
    <a-row :gutter="[16, 16]" style="margin-bottom:16px;">
      <a-col :xs="24" :md="12">
        <a-card :bordered="false" title="资产分布" style="background:rgba(255,255,255,0.03);border-radius:12px;">
          <div id="distributionPie" style="width:100%;height:320px;"></div>
        </a-card>
      </a-col>
      <a-col :xs="24" :md="12">
        <a-card :bordered="false" title="持仓盈亏" style="background:rgba(255,255,255,0.03);border-radius:12px;">
          <div id="profitBar" style="width:100%;height:320px;"></div>
        </a-card>
      </a-col>
    </a-row>

    <!-- Holdings table -->
    <a-card :bordered="false" title="持仓明细" style="background:rgba(255,255,255,0.03);border-radius:12px;">
      <a-table
        :dataSource="holdings"
        :columns="columns"
        :loading="loading"
        rowKey="id"
        :pagination="{ pageSize: 10, showSizeChanger: true, showTotal: (t: number) => `共 ${t} 条` }"
        :locale="{ emptyText: '暂无持仓数据' }"
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
  </div>
</template>

<script lang="ts">
import { ReloadOutlined } from '@ant-design/icons-vue'
export default {
  components: { ReloadOutlined },
  computed: {
    columns() {
      return [
        { title: '类型', dataIndex: 'asset_type', key: 'asset_type', width: 80 },
        { title: '代码', dataIndex: 'asset_code', key: 'asset_code', width: 100 },
        { title: '名称', dataIndex: 'asset_name', key: 'asset_name' },
        { title: '数量', dataIndex: 'quantity', key: 'quantity', width: 100, align: 'right' },
        { title: '成本价', dataIndex: 'cost_price', key: 'cost_price', width: 110, align: 'right' },
        { title: '现价', dataIndex: 'current_price', key: 'current_price', width: 110, align: 'right' },
        { title: '市值', dataIndex: 'value', key: 'value', width: 120, align: 'right' },
        { title: '盈亏', dataIndex: 'profit', key: 'profit', width: 120, align: 'right' },
        { title: '收益率', dataIndex: 'profit_pct', key: 'profit_pct', width: 100, align: 'right' },
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
