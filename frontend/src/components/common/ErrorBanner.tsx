import React from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';

interface ErrorBannerProps {
  message?: string;
  onRetry?: () => void;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({
  message = 'Não foi possível carregar os dados do painel. Verifique a conexão com a API FastAPI e tente novamente.',
  onRetry,
}) => {
  return (
    <div className="bg-status-danger/10 border-l-4 border-status-danger border-y border-r border-status-danger/40 rounded-r-xl p-4 my-4 flex items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <AlertTriangle className="w-5 h-5 text-status-danger shrink-0" />
        <div>
          <h4 className="text-sm font-semibold text-status-danger-text">Falha na Requisição</h4>
          <p className="text-xs text-status-danger-text/80">{message}</p>
        </div>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-status-danger/20 text-status-danger-text hover:bg-status-danger/30 rounded-lg transition-colors shrink-0"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Tentar Novamente
        </button>
      )}
    </div>
  );
};
