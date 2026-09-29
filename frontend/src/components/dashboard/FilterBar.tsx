import React from 'react';
import { Filter, RefreshCw, Search } from 'lucide-react';
import { ActiveFilters, FilterOptions } from '../../types/dashboard';

interface FilterBarProps {
  options?: FilterOptions;
  filters: ActiveFilters;
  onFilterChange: (newFilters: ActiveFilters) => void;
  onResetFilters: () => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  options,
  filters,
  onFilterChange,
  onResetFilters,
}) => {
  const handleChange = (field: keyof ActiveFilters, value: any) => {
    onFilterChange({
      ...filters,
      [field]: value,
    });
  };

  const handleMultiSelect = (
    field: keyof ActiveFilters,
    e: React.ChangeEvent<HTMLSelectElement>
  ) => {
    const selectedOptions = Array.from(
      e.target.selectedOptions,
      (option) => option.value
    );
    handleChange(field, selectedOptions.length > 0 ? selectedOptions : undefined);
  };

  return (
    <div className="bg-surface border border-border rounded-xl p-4 shadow-sm space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-border/60">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-linear-indigo" />
          <h3 className="text-sm font-semibold text-slate-200">
            Filtros do Relatório
          </h3>
        </div>
        <button
          onClick={onResetFilters}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-slate-200 bg-slate-800/80 hover:bg-slate-800 rounded-lg transition-colors border border-border/50"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Limpar Filtros
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
        {/* Período de Datas */}
        <div>
          <label className="block text-slate-400 font-medium mb-1">
            Data Inicial
          </label>
          <input
            type="date"
            min={options?.data_minima}
            max={options?.data_maxima}
            value={filters.data_inicial || ''}
            onChange={(e) => handleChange('data_inicial', e.target.value || undefined)}
            className="w-full bg-slate-900 border border-border rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-linear-indigo"
          />
        </div>

        <div>
          <label className="block text-slate-400 font-medium mb-1">
            Data Final
          </label>
          <input
            type="date"
            min={options?.data_minima}
            max={options?.data_maxima}
            value={filters.data_final || ''}
            onChange={(e) => handleChange('data_final', e.target.value || undefined)}
            className="w-full bg-slate-900 border border-border rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-linear-indigo"
          />
        </div>

        {/* Vendedor Responsável */}
        <div>
          <label className="block text-slate-400 font-medium mb-1">
            Vendedor Responsável
          </label>
          <select
            multiple
            value={filters.vendedores || []}
            onChange={(e) => handleMultiSelect('vendedores', e)}
            className="w-full bg-slate-900 border border-border rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-linear-indigo h-16"
          >
            {options?.vendedores.map((v) => (
              <option key={v} value={v}>
                {v}
              </option>
            ))}
          </select>
          <span className="text-[10px] text-slate-500 block mt-0.5">Segure Ctrl para selecionar múltiplos</span>
        </div>

        {/* Canal Comercial */}
        <div>
          <label className="block text-slate-400 font-medium mb-1">
            Canal Comercial
          </label>
          <select
            multiple
            value={filters.canais || []}
            onChange={(e) => handleMultiSelect('canais', e)}
            className="w-full bg-slate-900 border border-border rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-linear-indigo h-16"
          >
            {options?.canais.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        {/* Status da Sessão */}
        <div>
          <label className="block text-slate-400 font-medium mb-1">
            Status da Sessão
          </label>
          <select
            multiple
            value={filters.status_sessao || []}
            onChange={(e) => handleMultiSelect('status_sessao', e)}
            className="w-full bg-slate-900 border border-border rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-linear-indigo h-16"
          >
            {options?.status_sessao.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        {/* Tipo de Mensagem */}
        <div>
          <label className="block text-slate-400 font-medium mb-1">
            Tipo de Mensagem
          </label>
          <select
            multiple
            value={filters.tipos_mensagem || []}
            onChange={(e) => handleMultiSelect('tipos_mensagem', e)}
            className="w-full bg-slate-900 border border-border rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-linear-indigo h-16"
          >
            {options?.tipos_mensagem.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>

        {/* Direção da Mensagem */}
        <div>
          <label className="block text-slate-400 font-medium mb-1">
            Direção da Mensagem
          </label>
          <select
            multiple
            value={filters.direcoes || []}
            onChange={(e) => handleMultiSelect('direcoes', e)}
            className="w-full bg-slate-900 border border-border rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-linear-indigo h-16"
          >
            {options?.direcoes.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </div>

        {/* Origem do Vendedor */}
        <div>
          <label className="block text-slate-400 font-medium mb-1">
            Origem do Vendedor
          </label>
          <select
            multiple
            value={filters.origens_vendedor || []}
            onChange={(e) => handleMultiSelect('origens_vendedor', e)}
            className="w-full bg-slate-900 border border-border rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-linear-indigo h-16"
          >
            {options?.origens_vendedor.map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Busca rápida */}
      <div className="pt-2 border-t border-border/40 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Pesquisar cliente ou telefone..."
            value={filters.search_cliente || ''}
            onChange={(e) => handleChange('search_cliente', e.target.value || undefined)}
            className="w-full bg-slate-900 border border-border rounded-lg pl-9 pr-3 py-2 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-linear-indigo"
          />
        </div>

        <div className="relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Pesquisar no texto da mensagem..."
            value={filters.search_mensagem || ''}
            onChange={(e) => handleChange('search_mensagem', e.target.value || undefined)}
            className="w-full bg-slate-900 border border-border rounded-lg pl-9 pr-3 py-2 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-linear-indigo"
          />
        </div>
      </div>
    </div>
  );
};
