import axios from 'axios';
import {
  ActiveFilters,
  ConversationsResponse,
  DashboardOverview,
  FilterOptions,
  MetricSummary,
} from '../types/dashboard';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/dashboard`,
  headers: {
    'Content-Type': 'application/json',
  },
});

function filterToParams(filters: ActiveFilters): Record<string, any> {
  const params: Record<string, any> = {};

  if (filters.data_inicial) params.data_inicial = filters.data_inicial;
  if (filters.data_final) params.data_final = filters.data_final;
  if (filters.vendedores && filters.vendedores.length > 0)
    params.vendedores = filters.vendedores;
  if (filters.canais && filters.canais.length > 0)
    params.canais = filters.canais;
  if (filters.status_sessao && filters.status_sessao.length > 0)
    params.status_sessao = filters.status_sessao;
  if (filters.tipos_mensagem && filters.tipos_mensagem.length > 0)
    params.tipos_mensagem = filters.tipos_mensagem;
  if (filters.direcoes && filters.direcoes.length > 0)
    params.direcoes = filters.direcoes;
  if (filters.origens_vendedor && filters.origens_vendedor.length > 0)
    params.origens_vendedor = filters.origens_vendedor;
  if (filters.search_cliente) params.search_cliente = filters.search_cliente;
  if (filters.search_mensagem) params.search_mensagem = filters.search_mensagem;

  return params;
}

export async function fetchFilterOptions(): Promise<FilterOptions> {
  const response = await apiClient.get<FilterOptions>('/filters');
  return response.data;
}

export async function fetchMetricSummary(
  filters: ActiveFilters
): Promise<MetricSummary> {
  const response = await apiClient.get<MetricSummary>('/metrics', {
    params: filterToParams(filters),
  });
  return response.data;
}

export async function fetchDashboardOverview(
  filters: ActiveFilters
): Promise<DashboardOverview> {
  const response = await apiClient.get<DashboardOverview>('/overview', {
    params: filterToParams(filters),
  });
  return response.data;
}

export async function fetchConversations(
  filters: ActiveFilters,
  page = 1,
  limit = 50
): Promise<ConversationsResponse> {
  const response = await apiClient.get<ConversationsResponse>('/conversations', {
    params: {
      ...filterToParams(filters),
      page,
      limit,
    },
  });
  return response.data;
}

export function getExportUrl(filters: ActiveFilters, format: 'csv' | 'xlsx'): string {
  const searchParams = new URLSearchParams();
  searchParams.append('format', format);

  const paramsObj = filterToParams(filters);
  Object.keys(paramsObj).forEach((key) => {
    const val = paramsObj[key];
    if (Array.isArray(val)) {
      val.forEach((item) => searchParams.append(key, item));
    } else if (val !== undefined && val !== null) {
      searchParams.append(key, String(val));
    }
  });

  return `${apiClient.defaults.baseURL}/export?${searchParams.toString()}`;
}
