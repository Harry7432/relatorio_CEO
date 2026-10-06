import React from 'react';
import { MessageSquare, MessagesSquare, Users, UserCheck } from 'lucide-react';
import { MetricSummary } from '../../types/dashboard';
import { CardSkeleton } from '../common/Skeleton';

interface KpiGridProps {
  metrics?: MetricSummary;
  isLoading?: boolean;
}

export const KpiGrid: React.FC<KpiGridProps> = ({ metrics, isLoading }) => {
  if (isLoading || !metrics) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
    );
  }

  const kpis = [
    {
      title: 'Mensagens Filtradas',
      value: metrics.total_mensagens.toLocaleString('pt-BR'),
      subtitle: 'Total no período selecionado',
      icon: MessageSquare,
      color: 'text-brand-300 bg-brand-700/25 border-brand-700',
    },
    {
      title: 'Conversas / Sessões',
      value: metrics.total_sessoes.toLocaleString('pt-BR'),
      subtitle: 'Atendimentos únicos',
      icon: MessagesSquare,
      color: 'text-brand-500 bg-brand-500/10 border-brand-500/20',
    },
    {
      title: 'Contatos',
      value: metrics.total_contatos.toLocaleString('pt-BR'),
      subtitle: 'Clientes identificados',
      icon: Users,
      color: 'text-accent-teal bg-accent-teal/10 border-accent-teal/20',
    },
    {
      title: 'Contatos Identificados',
      value: `${metrics.percentual_contatos_identificados.toFixed(1).replace('.', ',')}%`,
      subtitle: 'Com vendedor atribuído',
      icon: UserCheck,
      color: 'text-status-success-text bg-emerald-500/10 border-emerald-500/20',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {kpis.map((kpi, idx) => {
        const Icon = kpi.icon;
        return (
          <div
            key={idx}
            className="bg-surface border border-border rounded-xl p-5 shadow-sm hover:border-slate-700 transition-all group"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-slate-400">
                {kpi.title}
              </span>
              <div
                className={`w-8 h-8 rounded-lg border flex items-center justify-center ${kpi.color}`}
              >
                <Icon className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl font-bold font-mono text-slate-100 tracking-tight mb-1">
              {kpi.value}
            </div>
            <div className="text-[11px] text-slate-500">{kpi.subtitle}</div>
          </div>
        );
      })}
    </div>
  );
};
