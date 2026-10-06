import React from 'react';
import { Database, Clock, Sun, Moon } from 'lucide-react';
import { Badge } from '../common/Badge';
import { useTheme } from '../../theme/ThemeProvider';

interface HeaderProps {
  lastUpdated?: string;
}

export const Header: React.FC<HeaderProps> = ({ lastUpdated }) => {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <header className="h-16 bg-surface border-b border-border px-6 flex items-center justify-between sticky top-0 z-20">
      <div>
        <h1 className="text-lg font-bold text-slate-100 tracking-tight">
          Falavinha Next Relatório BotNext
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
        <button
          type="button"
          onClick={toggleTheme}
          aria-label={isDark ? 'Ativar tema claro' : 'Ativar tema escuro'}
          title="Tema claro/escuro"
          className="p-1.5 rounded-lg border border-border bg-slate-800/60 text-slate-300 hover:text-slate-100 hover:bg-slate-800 transition-colors"
        >
          {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>
      </div>
    </header>
  );
};
