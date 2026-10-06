import { useMemo } from 'react';
import { useTheme } from './ThemeProvider';

export interface ChartPalette {
  series1: string;
  series2: string;
  series3: string;
  donut: string[];
  status: Record<string, string>;
  grid: string;
  axis: string;
  tooltipBg: string;
  tooltipBorder: string;
  tooltipText: string;
}

const readVar = (style: CSSStyleDeclaration, name: string) =>
  `rgb(${style.getPropertyValue(name).trim().replace(/\s+/g, ', ')})`;

const readChartPalette = (): ChartPalette => {
  const style = getComputedStyle(document.documentElement);
  const v = (name: string) => readVar(style, name);

  return {
    series1: v('--chart-series-1'),
    series2: v('--chart-series-2'),
    series3: v('--chart-series-3'),
    donut: [1, 2, 3, 4, 5, 6].map((n) => v(`--chart-donut-${n}`)),
    status: {
      COMPLETED: v('--chart-status-completed'),
      IN_PROGRESS: v('--chart-status-in-progress'),
      HIDDEN: v('--chart-status-hidden'),
      PENDING: v('--chart-status-pending'),
    },
    grid: v('--chart-grid'),
    axis: v('--chart-axis'),
    tooltipBg: v('--chart-tooltip-bg'),
    tooltipBorder: v('--chart-tooltip-border'),
    tooltipText: v('--chart-tooltip-text'),
  };
};

export const useChartPalette = (): ChartPalette => {
  const { theme } = useTheme();
  return useMemo(() => readChartPalette(), [theme]);
};
