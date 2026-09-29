import React, { useState, useEffect } from 'react';
import { Layout } from './components/layout/Layout';
import { KpiGrid } from './components/dashboard/KpiGrid';
import { SellerLeaderboard } from './components/dashboard/SellerLeaderboard';
import { ChartsGrid } from './components/dashboard/ChartsGrid';
import { FilterBar } from './components/dashboard/FilterBar';
import { ConversationTable } from './components/dashboard/ConversationTable';
import { ErrorBanner } from './components/common/ErrorBanner';
import { ActiveFilters } from './types/dashboard';
import {
  useFilterOptions,
  useMetricSummary,
  useDashboardOverview,
  useConversations,
} from './hooks/useDashboardData';

export const App: React.FC = () => {
  const [filters, setFilters] = useState<ActiveFilters>({});
  const [page, setPage] = useState<number>(1);

  // Load filter options
  const {
    data: options,
    isError: isErrorOptions,
    refetch: refetchOptions,
  } = useFilterOptions();

  // Set initial date range when options load
  useEffect(() => {
    if (options && !filters.data_inicial && !filters.data_final) {
      setFilters((prev) => ({
        ...prev,
        data_inicial: options.data_minima,
        data_final: options.data_maxima,
      }));
    }
  }, [options]);

  // Reset page when filters change
  const handleFilterChange = (newFilters: ActiveFilters) => {
    setFilters(newFilters);
    setPage(1);
  };

  const handleResetFilters = () => {
    if (options) {
      setFilters({
        data_inicial: options.data_minima,
        data_final: options.data_maxima,
      });
    } else {
      setFilters({});
    }
    setPage(1);
  };

  // Queries
  const {
    data: metrics,
    isLoading: isLoadingMetrics,
    isError: isErrorMetrics,
    refetch: refetchMetrics,
  } = useMetricSummary(filters);

  const {
    data: overview,
    isLoading: isLoadingOverview,
    isError: isErrorOverview,
    refetch: refetchOverview,
  } = useDashboardOverview(filters);

  const {
    data: conversations,
    isLoading: isLoadingConversations,
    isError: isErrorConversations,
    refetch: refetchConversations,
  } = useConversations(filters, page);

  const isAnyError = isErrorOptions || isErrorMetrics || isErrorOverview || isErrorConversations;

  const handleRetryAll = () => {
    refetchOptions();
    refetchMetrics();
    refetchOverview();
    refetchConversations();
  };

  const formattedLastUpdated = new Date().toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <Layout lastUpdated={formattedLastUpdated}>
      {({ activeTab }) => (
        <div className="space-y-6">
          {/* Error Banner if API fails */}
          {isAnyError && (
            <ErrorBanner
              message="Erro ao conectar à API FastAPI. Verifique se o backend está em execução na porta 8000."
              onRetry={handleRetryAll}
            />
          )}

          {/* Filter Bar visible across tabs */}
          <FilterBar
            options={options}
            filters={filters}
            onFilterChange={handleFilterChange}
            onResetFilters={handleResetFilters}
          />

          {/* Tab 1: Visão Geral */}
          {activeTab === 'overview' && (
            <>
              <KpiGrid metrics={metrics} isLoading={isLoadingMetrics} />
              <SellerLeaderboard
                ranking={metrics?.ranking}
                totalVendedoresMensagens={metrics?.vendedores_total_mensagens_enviadas}
                isLoading={isLoadingMetrics}
              />
              <ChartsGrid overview={overview} isLoading={isLoadingOverview} />
            </>
          )}

          {/* Tab 2: Vendedores */}
          {activeTab === 'vendedores' && (
            <>
              <SellerLeaderboard
                ranking={metrics?.ranking}
                totalVendedoresMensagens={metrics?.vendedores_total_mensagens_enviadas}
                isLoading={isLoadingMetrics}
              />
              <ChartsGrid overview={overview} isLoading={isLoadingOverview} />
            </>
          )}

          {/* Tab 3: Conversas */}
          {activeTab === 'conversas' && (
            <ConversationTable
              data={conversations}
              filters={filters}
              page={page}
              onPageChange={setPage}
              isLoading={isLoadingConversations}
              onResetFilters={handleResetFilters}
            />
          )}
        </div>
      )}
    </Layout>
  );
};
