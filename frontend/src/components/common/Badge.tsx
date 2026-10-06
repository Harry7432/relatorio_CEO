import React from 'react';

interface BadgeProps {
  variant?: 'success' | 'warning' | 'danger' | 'neutral' | 'gold' | 'silver' | 'bronze';
  children: React.ReactNode;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = 'neutral',
  children,
  className = '',
}) => {
  const styles = {
    success: 'bg-emerald-500/10 text-status-success-text border-emerald-500/20',
    warning: 'bg-amber-500/10 text-status-warning-text border-amber-500/20',
    danger: 'bg-rose-500/10 text-status-danger-text border-rose-500/20',
    neutral: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
    gold: 'bg-amber-500/20 text-status-warning-text border-amber-500/40 font-bold',
    silver: 'bg-slate-400/20 text-slate-200 border-slate-400/40 font-bold',
    bronze: 'bg-amber-700/20 text-status-warning-text border-amber-700/40 font-bold',
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium border ${styles[variant]} ${className}`}
    >
      {children}
    </span>
  );
};
