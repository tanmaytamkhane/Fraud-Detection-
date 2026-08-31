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
        background: '#050608',
        card: '#0b0d13',
        'card-hover': '#10141e',
        border: '#1a1f2c',
        'border-light': '#252b3d',
        accent: {
          cyan: '#00e5ff',
          red: '#ff334b',
          green: '#00e676',
          yellow: '#f59e0b',
          purple: '#b388ff',
          orange: '#ff9100',
        }
      },
            fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Roboto Mono', 'monospace'],
        display: ['Inter', '"Plus Jakarta Sans"', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'glow-cyan': '0 0 25px -5px rgba(0, 229, 255, 0.3)',
        'glow-red': '0 0 25px -5px rgba(255, 51, 75, 0.3)',
        'glow-green': '0 0 25px -5px rgba(0, 230, 118, 0.3)',
      }
    },
  },
  plugins: [],
}
