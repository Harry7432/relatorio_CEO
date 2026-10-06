import React, { useState } from 'react';
import { LayoutDashboard, Users, MessageSquare, ChevronLeft, ChevronRight, BarChart3 } from 'lucide-react';
import { useTheme } from '../../theme/ThemeProvider';

interface SidebarProps {
  activeTab: 'overview' | 'vendedores' | 'conversas';
  setActiveTab: (tab: 'overview' | 'vendedores' | 'conversas') => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const [collapsed, setCollapsed] = useState(false);
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const menuItems = [
    {
      id: 'overview' as const,
      label: 'Visão Geral',
      icon: LayoutDashboard,
    },
    {
      id: 'vendedores' as const,
      label: 'Vendedores',
      icon: Users,
    },
    {
      id: 'conversas' as const,
      label: 'Conversas',
      icon: MessageSquare,
    },
  ];

  return (
    <aside
      className={`fixed left-0 top-0 bottom-0 z-30 bg-sidebar border-r border-border transition-all duration-200 flex flex-col justify-between ${
        collapsed ? 'w-16' : 'w-56'
      }`}
    >
      <div>
        {/* Logo / Brand Header */}
        <div className="min-h-[4rem] flex items-center justify-between gap-2 px-3 py-3 border-b border-border">
          {collapsed ? (
            <img
              src={isDark ? '/brand/icon-x-white.png' : '/brand/icon-x-teal.png'}
              alt="Falavinha Next"
              className="w-8 h-8 mx-auto object-contain"
            />
          ) : (
            <div className="flex flex-col gap-2 min-w-0 flex-1">
              {isDark ? (
                <div className="rounded-lg bg-slate-50 p-3">
                  <img
                    src="/brand/logo-falavinha-next.svg"
                    alt="Falavinha Next"
                    className="w-full h-auto"
                  />
                </div>
              ) : (
                <img
                  src="/brand/logo-falavinha-next.svg"
                  alt="Falavinha Next"
                  className="w-full h-auto"
                />
              )}
              <span className="text-[11px] font-semibold tracking-tight text-slate-300 truncate">
                Falavinha Next Relatório BotNext
              </span>
            </div>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="text-slate-400 hover:text-slate-100 p-1 rounded-md hover:bg-slate-800 transition-colors shrink-0"
            title={collapsed ? 'Expandir Sidebar' : 'Recolher Sidebar'}
          >
            {collapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronLeft className="w-4 h-4" />
            )}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="p-2 space-y-1 mt-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? isDark
                      ? 'bg-brand-700/25 text-brand-300 border border-brand-700'
                      : 'bg-brand-700 text-white border border-brand-700'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                }`}
                title={collapsed ? item.label : undefined}
              >
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? (isDark ? 'text-brand-300' : 'text-white') : ''}`} />
                {!collapsed && <span>{item.label}</span>}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      <div className="p-3 border-t border-border">
        {!collapsed ? (
          <div className="text-[11px] text-slate-500 font-mono">
            v1.0.0 • Falavinha Next
          </div>
        ) : (
          <div className="w-2 h-2 rounded-full bg-status-success mx-auto" title="Sistema Operacional" />
        )}
      </div>
    </aside>
  );
};
