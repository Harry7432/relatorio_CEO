import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

interface LayoutProps {
  children: (props: {
    activeTab: 'overview' | 'vendedores' | 'conversas';
  }) => React.ReactNode;
  lastUpdated?: string;
}

export const Layout: React.FC<LayoutProps> = ({ children, lastUpdated }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'vendedores' | 'conversas'>('overview');

  return (
    <div className="min-h-screen bg-background flex text-slate-100">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="flex-1 flex flex-col min-w-0 ml-16 sm:ml-56 transition-all duration-200">
        <Header lastUpdated={lastUpdated} />
        <main className="flex-1 p-4 sm:p-6 space-y-6 max-w-7xl w-full mx-auto">
          {children({ activeTab })}
        </main>
      </div>
    </div>
  );
};
