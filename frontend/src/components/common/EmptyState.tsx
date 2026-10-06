import React from 'react';
import { SearchX, RefreshCw } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  description?: string;
  onResetFilters?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'Nenhum registro encontrado',
  description = 'Nenhum dado corresponde aos filtros selecionados. Tente ajustar o período de datas ou limpar a pesquisa.',
  onResetFilters,
}) => {
  return (
    <div className="bg-surface border border-border border-dashed rounded-xl p-8 text-center flex flex-col items-center justify-center my-4">
      <div className="w-12 h-12 rounded-full bg-slate-800/80 flex items-center justify-center mb-4 text-slate-400">
        <SearchX className="w-6 h-6" />
      </div>
      <h3 className="text-base font-semibold text-slate-200 mb-1">{title}</h3>
      <p className="text-sm text-slate-400 max-w-md mb-6">{description}</p>
      {onResetFilters && (
        <button
          onClick={onResetFilters}
          className="inline-flex items-center gap-2 px-4 py-2 text-xs font-medium bg-brand-700 text-white rounded-lg hover:ring-1 hover:ring-brand-300 transition-colors shadow-sm"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Limpar Filtros
        </button>
      )}
    </div>
  );
};
