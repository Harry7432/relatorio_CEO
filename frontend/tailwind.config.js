/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        brand: {
          900: 'rgb(var(--brand-900) / <alpha-value>)',
          700: 'rgb(var(--brand-700) / <alpha-value>)',
          600: 'rgb(var(--brand-600) / <alpha-value>)',
          500: 'rgb(var(--brand-500) / <alpha-value>)',
          300: 'rgb(var(--brand-300) / <alpha-value>)',
        },
        accent: {
          teal: 'rgb(var(--accent-teal) / <alpha-value>)',
        },
        background: 'rgb(var(--bg) / <alpha-value>)',
        sidebar: 'rgb(var(--sidebar) / <alpha-value>)',
        surface: {
          DEFAULT: 'rgb(var(--surface) / <alpha-value>)',
          elevated: 'rgb(var(--surface-2) / <alpha-value>)',
        },
        border: {
          DEFAULT: 'rgb(var(--border) / <alpha-value>)',
          focus: 'rgb(var(--brand-300) / <alpha-value>)',
        },
        slate: {
          50: 'rgb(var(--slate-50) / <alpha-value>)',
          100: 'rgb(var(--slate-100) / <alpha-value>)',
          200: 'rgb(var(--slate-200) / <alpha-value>)',
          300: 'rgb(var(--slate-300) / <alpha-value>)',
          400: 'rgb(var(--slate-400) / <alpha-value>)',
          500: 'rgb(var(--slate-500) / <alpha-value>)',
          600: 'rgb(var(--slate-600) / <alpha-value>)',
          700: 'rgb(var(--slate-700) / <alpha-value>)',
          800: 'rgb(var(--slate-800) / <alpha-value>)',
          900: 'rgb(var(--slate-900) / <alpha-value>)',
          950: 'rgb(var(--slate-950) / <alpha-value>)',
        },
        medal: {
          gold: '#F59E0B',
          silver: '#B4CFD0',
          bronze: '#D97706',
        },
        status: {
          success: 'rgb(var(--status-success) / <alpha-value>)',
          'success-text': 'rgb(var(--status-success-text) / <alpha-value>)',
          warning: 'rgb(var(--status-warning) / <alpha-value>)',
          'warning-text': 'rgb(var(--status-warning-text) / <alpha-value>)',
          danger: 'rgb(var(--status-danger) / <alpha-value>)',
          'danger-text': 'rgb(var(--status-danger-text) / <alpha-value>)',
          neutral: 'rgb(var(--status-neutral) / <alpha-value>)',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
