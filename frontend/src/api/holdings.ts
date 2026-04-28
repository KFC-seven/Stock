import api from './index'

export interface HoldingItem {
  id: number
  user_id: number
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
  buy_date: string | null
  notes: string
}

export interface HoldingCreate {
  asset_type: string
  asset_code: string
  asset_name?: string
  quantity: number
  cost_price: number
  buy_date?: string
  notes?: string
}

export interface PortfolioSummary {
  items: HoldingItem[]
  total_cost: number
  total_value: number
  total_profit: number
  total_profit_pct: number
}

export const holdingsApi = {
  list: () => api.get<HoldingItem[]>('/holdings'),
  create: (data: HoldingCreate) => api.post<HoldingItem>('/holdings', data),
  update: (id: number, data: Partial<HoldingCreate>) => api.put<HoldingItem>(`/holdings/${id}`, data),
  delete: (id: number) => api.delete(`/holdings/${id}`),
  summary: () => api.get<{ portfolio: PortfolioSummary; distribution: Record<string, { value: number; cost: number; profit: number }> }>('/portfolio/summary'),
  family: () => api.get('/portfolio/family'),
  refreshPrices: () => api.post('/portfolio/refresh-prices'),
}
