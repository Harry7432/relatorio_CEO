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
import { useChartPalette } from '../../theme/chartPalette';

interface ChartsGridProps {
  overview?: DashboardOverview;
  isLoading?: boolean;
}

export const ChartsGrid: React.FC<ChartsGridProps> = ({ overview, isLoading }) => {
  const palette = useChartPalette();

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

  const tooltipStyle = {
    backgroundColor: palette.tooltipBg,
    borderColor: palette.tooltipBorder,
    borderRadius: '8px',
    color: palette.tooltipText,
    fontSize: '12px',
  };

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
              <CartesianGrid strokeDasharray="3 3" stroke={palette.grid} />
              <XAxis dataKey="data" stroke={palette.axis} fontSize={11} />
              <YAxis stroke={palette.axis} fontSize={11} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line
                type="monotone"
                dataKey="mensagens"
                name="Mensagens"
                stroke={palette.series1}
                strokeWidth={3}
                dot={{ fill: palette.series1, r: 4 }}
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
              <CartesianGrid strokeDasharray="3 3" stroke={palette.grid} />
              <XAxis dataKey="tipo" stroke={palette.axis} fontSize={11} />
              <YAxis stroke={palette.axis} fontSize={11} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="quantidade" name="Quantidade" fill={palette.series2} radius={[4, 4, 0, 0]} />
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
                {sessoes_por_status.map((item, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={palette.status[item.status] ?? palette.donut[index % palette.donut.length]}
                  />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
              <Legend
                verticalAlign="bottom"
                height={36}
                formatter={(value) => {
                  const total = sessoes_por_status.reduce((acc, s) => acc + s.conversas, 0);
                  const item = sessoes_por_status.find((s) => s.status === value);
                  const pct = total && item ? ((item.conversas / total) * 100).toFixed(1).replace('.', ',') : '0';
                  return (
                    <span className="text-xs text-slate-300">
                      {value} <span className="font-mono text-slate-100">{pct}%</span>
                    </span>
                  );
                }}
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
              <CartesianGrid strokeDasharray="3 3" stroke={palette.grid} />
              <XAxis dataKey="canal" stroke={palette.axis} fontSize={10} interval={0} />
              <YAxis stroke={palette.axis} fontSize={11} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="mensagens" name="Mensagens" fill={palette.series1} radius={[4, 4, 0, 0]} />
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
              <CartesianGrid strokeDasharray="3 3" stroke={palette.grid} />
              <XAxis type="number" stroke={palette.axis} fontSize={11} />
              <YAxis
                type="category"
                dataKey="vendedor"
                stroke={palette.axis}
                fontSize={11}
                width={120}
              />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="contatos" name="Contatos" fill={palette.series3} radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
