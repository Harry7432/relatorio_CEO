import React from 'react';
import { Trophy, Award, Medal } from 'lucide-react';
import { SellerRankingItem } from '../../types/dashboard';
import { Badge } from '../common/Badge';
import { Skeleton } from '../common/Skeleton';

interface SellerLeaderboardProps {
  ranking?: SellerRankingItem[];
  totalVendedoresMensagens?: number;
  isLoading?: boolean;
}

export const SellerLeaderboard: React.FC<SellerLeaderboardProps> = ({
  ranking = [],
  totalVendedoresMensagens = 0,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div className="bg-surface border border-border rounded-xl p-5 space-y-4">
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-24 w-full" />
      </div>
    );
  }

  const getRankBadge = (posicao: number) => {
    if (posicao === 1) {
      return (
        <Badge variant="gold" className="gap-1">
          <Trophy className="w-3 h-3 text-amber-300" />
          1º Lugar
        </Badge>
      );
    }
    if (posicao === 2) {
      return (
        <Badge variant="silver" className="gap-1">
          <Award className="w-3 h-3 text-slate-300" />
          2º Lugar
        </Badge>
      );
    }
    if (posicao === 3) {
      return (
        <Badge variant="bronze" className="gap-1">
          <Medal className="w-3 h-3 text-amber-500" />
          3º Lugar
        </Badge>
      );
    }
    return <span className="text-xs font-mono text-slate-400">#{posicao}</span>;
  };

  return (
    <div className="bg-surface border border-brand-700 rounded-xl p-5 shadow-lg relative overflow-hidden">
      {/* Background Subtle Accent Glow */}
      <div className="absolute -top-12 -right-12 w-48 h-48 bg-brand-700/25 rounded-full blur-3xl pointer-events-none" />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <Trophy className="w-5 h-5 text-amber-400" />
            <h2 className="text-base font-bold text-slate-100 tracking-tight">
              Ranking de Atendimento dos Vendedores
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Destaque comercial de mensagens enviadas (direção TO_HUB com usuário identificado)
          </p>
        </div>
        <div className="text-right">
          <div className="text-xs font-mono text-slate-400">Total Enviado</div>
          <div className="text-lg font-bold font-mono text-brand-300">
            {totalVendedoresMensagens.toLocaleString('pt-BR')} msgs
          </div>
        </div>
      </div>

      {ranking.length === 0 ? (
        <div className="text-center py-6 text-xs text-slate-400 bg-slate-900/40 rounded-lg border border-border/40">
          Nenhuma mensagem de vendedor registrada no período e canal selecionados.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-border/80 text-slate-400 font-medium">
                <th className="pb-2.5 px-3">Posição</th>
                <th className="pb-2.5 px-3">Vendedor</th>
                <th className="pb-2.5 px-3 text-right">Mensagens Enviadas</th>
                <th className="pb-2.5 px-3 w-48 text-right">Participação %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40">
              {ranking.map((item) => (
                <tr
                  key={item.posicao}
                  className={`hover:bg-slate-800/40 transition-colors ${
                    item.posicao === 1 ? 'bg-amber-500/5 font-semibold' : ''
                  }`}
                >
                  <td className="py-3 px-3">{getRankBadge(item.posicao)}</td>
                  <td className="py-3 px-3 font-medium text-slate-200">
                    {item.vendedor}
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-slate-100">
                    {item.mensagens_enviadas.toLocaleString('pt-BR')}
                  </td>
                  <td className="py-3 px-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <span className="font-mono text-slate-300 w-12 text-right">
                        {item.participacao_percentual.toFixed(1).replace('.', ',')}%
                      </span>
                      <div className="w-24 bg-slate-700 rounded-full h-2 overflow-hidden border border-border/50">
                        <div
                          className={`h-full rounded-full ${
                            item.posicao === 1
                              ? 'bg-amber-400'
                              : item.posicao === 2
                              ? 'bg-slate-300'
                              : item.posicao === 3
                              ? 'bg-amber-600'
                              : 'bg-brand-500'
                          }`}
                          style={{
                            width:
                              item.participacao_percentual > 0
                                ? `max(4px, ${Math.min(100, item.participacao_percentual)}%)`
                                : '0px',
                          }}
                        />
                      </div>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
