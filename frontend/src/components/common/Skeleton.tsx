import React from 'react';

interface SkeletonProps {
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = '' }) => {
  return (
    <div
      className={`animate-pulse bg-gradient-to-r from-surface-elevated via-slate-800 to-surface-elevated rounded-md ${className}`}
    />
  );
};

export const CardSkeleton: React.FC = () => {
  return (
    <div className="bg-surface border border-border rounded-xl p-5 shadow-sm space-y-3">
      <Skeleton className="h-4 w-28" />
      <Skeleton className="h-8 w-20" />
      <Skeleton className="h-3 w-36" />
    </div>
  );
};

export const TableSkeleton: React.FC = () => {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, idx) => (
        <div
          key={idx}
          className="h-11 bg-surface border border-border/50 rounded-lg animate-pulse"
        />
      ))}
    </div>
  );
};

export const ChartSkeleton: React.FC = () => {
  return (
    <div className="bg-surface border border-border rounded-xl p-5 h-80 flex flex-col justify-between">
      <Skeleton className="h-5 w-40" />
      <div className="h-48 w-full bg-slate-800/40 rounded-lg animate-pulse" />
    </div>
  );
};
