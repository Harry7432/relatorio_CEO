import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { DashboardOverview } from '../../types/dashboard';
import { ChartSkeleton } from '../common/Skeleton';

interface ChartsGridProps {
  overview?: DashboardOverview;
  isLoading?: boolean;
}

const DONUT_COLORS = ['#10B981', '#F59E0B', '#EF4444', '#6366F1', '#0EA5E9', '#8B5CF6'];

export const ChartsGrid: React.FC<ChartsGridProps> = ({ overview, isLoading }) => {
  if (isLoading || !overview) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <ChartSkeleton key={i} />
        ))}
      </div>
    );
  }

  const {
    mensagens_por_dia = [],
    mensagens_por_tipo = [],
    sessoes_por_status = [],
    mensagens_por_canal = [],
    contatos_por_vendedor = [],
  } = overview;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* 1. Evolução Diária */}
      <div className="bg-surface border border-border rounded-xl p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-200 mb-4">
          Evolução Diária das Mensagens
        </h3>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={mensagens_por_dia}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2A3447" />
              <XAxis dataKey="data" stroke="#64748B" fontSize={11} />
              <YAxis stroke="#64748B" fontSize={11} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#131822',
                  borderColor: '#2A3447',
                  borderRadius: '8px',
                  color: '#F8FAFC',
                  fontSize: '12px',
                }}
              />
              <Line
                type="monotone"
                dataKey="mensagens"
                name="Mensagens"
                stroke="#6366F1"
                strokeWidth={3}
                dot={{ fill: '#6366F1', r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 2. Mensagens por Tipo */}
      <div className="bg-surface border border-border rounded-xl p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-200 mb-4">
          Mensagens por Tipo
        </h3>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={mensagens_por_tipo}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2A3447" />
              <XAxis dataKey="tipo" stroke="#64748B" fontSize={11} />
              <YAxis stroke="#64748B" fontSize={11} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#131822',
                  borderColor: '#2A3447',
                  borderRadius: '8px',
                  color: '#F8FAFC',
                  fontSize: '12px',
                }}
              />
              <Bar dataKey="quantidade" name="Quantidade" fill="#0EA5E9" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 3. Conversas por Status (Donut) */}
      <div className="bg-surface border border-border rounded-xl p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-200 mb-4">
          Conversas por Status
        </h3>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={sessoes_por_status}
                dataKey="conversas"
                nameKey="status"
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={85}
                paddingAngle={4}
              >
                {sessoes_por_status.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={DONUT_COLORS[index % DONUT_COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#131822',
                  borderColor: '#2A3447',
                  borderRadius: '8px',
                  color: '#F8FAFC',
                  fontSize: '12px',
                }}
              />
              <Legend
                verticalAlign="bottom"
                height={36}
                formatter={(value) => (
                  <span className="text-xs text-slate-300">{value}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 4. Mensagens por Canal Commercial */}
      <div className="bg-surface border border-border rounded-xl p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-200 mb-4">
          Mensagens por Canal Comercial
        </h3>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={mensagens_por_canal}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2A3447" />
              <XAxis dataKey="canal" stroke="#64748B" fontSize={10} interval={0} />
              <YAxis stroke="#64748B" fontSize={11} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#131822',
                  borderColor: '#2A3447',
                  borderRadius: '8px',
                  color: '#F8FAFC',
                  fontSize: '12px',
                }}
              />
              <Bar dataKey="mensagens" name="Mensagens" fill="#10B981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 5. Contatos por Vendedor Responsável (Horizontal Bar) */}
      <div className="bg-surface border border-border rounded-xl p-5 shadow-sm lg:col-span-2">
        <h3 className="text-sm font-semibold text-slate-200 mb-4">
          Contatos por Vendedor Responsável
        </h3>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              layout="vertical"
              data={contatos_por_vendedor}
              margin={{ left: 40 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#2A3447" />
              <XAxis type="number" stroke="#64748B" fontSize={11} />
              <YAxis
                type="category"
                dataKey="vendedor"
                stroke="#64748B"
                fontSize={11}
                width={120}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#131822',
                  borderColor: '#2A3447',
                  borderRadius: '8px',
                  color: '#F8FAFC',
                  fontSize: '12px',
                }}
              />
              <Bar dataKey="contatos" name="Contatos" fill="#8B5CF6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
