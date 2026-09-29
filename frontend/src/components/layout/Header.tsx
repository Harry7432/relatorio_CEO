import React from 'react';
import { Database, Clock } from 'lucide-react';
import { Badge } from '../common/Badge';

interface HeaderProps {
  lastUpdated?: string;
}

export const Header: React.FC<HeaderProps> = ({ lastUpdated }) => {
  return (
    <header className="h-16 bg-surface border-b border-border px-6 flex items-center justify-between sticky top-0 z-20">
      <div>
        <h1 className="text-lg font-bold text-slate-100 tracking-tight">
          Relatório Comercial BotNext
        </h1>
        <p className="text-xs text-slate-400 hidden sm:block">
          Acompanhamento executivo de contatos, conversas e desempenho dos vendedores.
        </p>
      </div>

      <div className="flex items-center gap-3">
        <Badge variant="success" className="hidden sm:inline-flex gap-1.5">
          <Database className="w-3 h-3" />
          PostgreSQL Conectado
        </Badge>
        {lastUpdated && (
          <div className="flex items-center gap-1.5 text-[11px] text-slate-400 bg-slate-800/60 border border-border px-3 py-1 rounded-full font-mono">
            <Clock className="w-3 h-3 text-slate-400" />
            <span>Atualizado: {lastUpdated}</span>
          </div>
        )}
      </div>
    </header>
  );
};
