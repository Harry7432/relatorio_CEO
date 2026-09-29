import { useQuery } from '@tanstack/react-query';
import {
  fetchFilterOptions,
  fetchMetricSummary,
  fetchDashboardOverview,
  fetchConversations,
} from '../services/api';
import { ActiveFilters } from '../types/dashboard';

export function useFilterOptions() {
  return useQuery({
    queryKey: ['dashboard', 'filters'],
    queryFn: fetchFilterOptions,
    staleTime: 5 * 60 * 1000,
  });
}

export function useMetricSummary(filters: ActiveFilters) {
  return useQuery({
    queryKey: ['dashboard', 'metrics', filters],
    queryFn: () => fetchMetricSummary(filters),
    staleTime: 30 * 1000,
  });
}

export function useDashboardOverview(filters: ActiveFilters) {
  return useQuery({
    queryKey: ['dashboard', 'overview', filters],
    queryFn: () => fetchDashboardOverview(filters),
    staleTime: 30 * 1000,
  });
}

export function useConversations(filters: ActiveFilters, page: number, limit = 50) {
  return useQuery({
    queryKey: ['dashboard', 'conversations', filters, page, limit],
    queryFn: () => fetchConversations(filters, page, limit),
    staleTime: 30 * 1000,
  });
}
