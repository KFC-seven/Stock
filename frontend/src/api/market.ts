import api from './index'

export interface SearchResult {
  code: string
  name: string
  type: string
  type_label: string
}

export const marketApi = {
  search: (q: string) => api.get<SearchResult[]>('/market/search', { params: { q } }),
  price: (asset_code: string, asset_type: string) =>
    api.get<{ asset_code: string; asset_type: string; price: number | null }>('/market/price', {
      params: { asset_code, asset_type },
    }),
}
