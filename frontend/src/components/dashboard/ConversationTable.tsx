import React, { useState } from 'react';
import { Download, FileSpreadsheet, FileText, ChevronLeft, ChevronRight } from 'lucide-react';
import { ActiveFilters, ConversationsResponse } from '../../types/dashboard';
import { getExportUrl } from '../../services/api';
import { Badge } from '../common/Badge';
import { TableSkeleton } from '../common/Skeleton';
import { EmptyState } from '../common/EmptyState';

interface ConversationTableProps {
  data?: ConversationsResponse;
  filters: ActiveFilters;
  page: number;
  onPageChange: (newPage: number) => void;
  isLoading?: boolean;
  onResetFilters?: () => void;
}

export const ConversationTable: React.FC<ConversationTableProps> = ({
  data,
  filters,
  page,
  onPageChange,
  isLoading,
  onResetFilters,
}) => {
  const [sortField, setSortField] = useState<string>('timestamp_mensagem');
  const [sortAsc, setSortAsc] = useState<boolean>(false);

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(true);
    }
  };

  const handleExport = (format: 'csv' | 'xlsx') => {
    const url = getExportUrl(filters, format);
    window.open(url, '_blank');
  };

  if (isLoading) {
    return (
      <div className="bg-surface border border-border rounded-xl p-5 space-y-4">
        <div className="h-6 w-48 bg-slate-800 rounded animate-pulse" />
        <TableSkeleton />
      </div>
    );
  }

  if (!data || data.items.length === 0) {
    return <EmptyState onResetFilters={onResetFilters} />;
  }

  // Sorting
  const sortedItems = [...data.items].sort((a: any, b: any) => {
    const valA = a[sortField] || '';
    const valB = b[sortField] || '';
    if (valA < valB) return sortAsc ? -1 : 1;
    if (valA > valB) return sortAsc ? 1 : -1;
    return 0;
  });

  return (
    <div className="bg-surface border border-border rounded-xl p-5 shadow-sm space-y-4">
      {/* Table Header & Export Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-border/60">
        <div>
          <h3 className="text-base font-bold text-slate-100 tracking-tight">
            Mensagens Encontradas
          </h3>
          <p className="text-xs text-slate-400">
            Exibindo {data.items.length} de {data.total.toLocaleString('pt-BR')} registros filtrados (Página {data.page} de {data.pages})
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => handleExport('csv')}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-border rounded-lg transition-colors"
          >
            <FileText className="w-3.5 h-3.5 text-brand-500" />
            Baixar CSV
          </button>
          <button
            onClick={() => handleExport('xlsx')}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-border rounded-lg transition-colors"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-status-success-text" />
            Baixar Excel
          </button>
        </div>
      </div>

      {/* Table Area */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-border/80 text-slate-400 font-medium select-none">
              <th
                onClick={() => handleSort('timestamp_mensagem')}
                className="py-2.5 px-3 cursor-pointer hover:text-slate-200"
              >
                Data e Hora {sortField === 'timestamp_mensagem' ? (sortAsc ? '↑' : '↓') : ''}
              </th>
              <th
                onClick={() => handleSort('vendedor_responsavel')}
                className="py-2.5 px-3 cursor-pointer hover:text-slate-200"
              >
                Vendedor
              </th>
              <th
                onClick={() => handleSort('contato_nome')}
                className="py-2.5 px-3 cursor-pointer hover:text-slate-200"
              >
                Cliente / Telefone
              </th>
              <th className="py-2.5 px-3">Canal</th>
              <th className="py-2.5 px-3">Status / Tipo / Direção</th>
              <th className="py-2.5 px-3">Mensagem</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40">
            {sortedItems.map((item, idx) => (
              <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-3 px-3 font-mono text-slate-300 whitespace-nowrap">
                  {item.timestamp_mensagem}
                </td>
                <td className="py-3 px-3 font-medium text-slate-200 max-w-[160px]">
                  <div className="truncate" title={item.vendedor_responsavel}>{item.vendedor_responsavel}</div>
                  <div className="text-[10px] text-slate-500 truncate">{item.origem_vendedor}</div>
                </td>
                <td className="py-3 px-3 max-w-[200px]">
                  <div className="font-medium text-slate-200 truncate" title={item.contato_nome}>{item.contato_nome}</div>
                  <div className="text-[10px] font-mono text-slate-400">{item.telefone_formatado}</div>
                </td>
                <td className="py-3 px-3 text-slate-300 max-w-[140px] truncate">
                  {item.canal}
                </td>
                <td className="py-3 px-3">
                  <div className="flex flex-wrap gap-1 max-w-[190px]">
                    <Badge variant={item.status_sessao === 'CLOSED' ? 'neutral' : 'success'}>
                      {item.status_sessao}
                    </Badge>
                    <Badge variant="neutral">{item.tipo_mensagem}</Badge>
                    <Badge variant={item.direcao === 'TO_HUB' ? 'success' : 'warning'}>
                      {item.direcao}
                    </Badge>
                  </div>
                </td>
                <td className="py-3 px-3 text-slate-300 max-w-[220px] truncate" title={item.texto}>
                  {item.texto || <span className="italic text-slate-500">(Sem texto)</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      <div className="flex items-center justify-between pt-3 border-t border-border/60 text-xs text-slate-400">
        <div>
          Página <span className="font-mono text-slate-200">{data.page}</span> de{' '}
          <span className="font-mono text-slate-200">{data.pages}</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1)}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300"
            title="Página Anterior"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            disabled={page >= data.pages}
            onClick={() => onPageChange(page + 1)}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300"
            title="Próxima Página"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
