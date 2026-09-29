/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#0B0E14',
        surface: {
          DEFAULT: '#131822',
          elevated: '#1C2333',
        },
        border: {
          DEFAULT: '#2A3447',
          focus: '#6366F1',
        },
        linear: {
          indigo: '#6366F1',
          indigoHover: '#4F46E5',
          gold: '#F59E0B',
          silver: '#94A3B8',
          bronze: '#D97706',
        },
        status: {
          success: '#10B981',
          warning: '#F59E0B',
          danger: '#EF4444',
          neutral: '#64748B',
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
