/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Ableton-inspired dark theme
        'ableton': {
          'bg': '#1a1a1a',
          'surface': '#2a2a2a',
          'surface-light': '#333333',
          'border': '#3a3a3a',
          'text': '#e0e0e0',
          'text-dim': '#999999',
          'accent': '#ff7e3e',
          'blue': '#0066ff',
          'green': '#00cc00',
          'red': '#ff3333',
          'yellow': '#ffcc00',
        },
        // Emotion interface colors
        'emotion': {
          'grief': '#4a5568',
          'joy': '#fbbf24',
          'anger': '#ef4444',
          'fear': '#8b5cf6',
          'love': '#ec4899',
          'hope': '#34d399',
          'melancholy': '#6366f1',
          'rage': '#dc2626',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'SF Mono', 'Courier New', 'monospace'],
      },
      animation: {
        'flip': 'flip 0.6s ease-in-out',
        'flip-back': 'flip-back 0.6s ease-in-out',
        'vu-meter': 'vu-meter 0.1s ease-out',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'spin-slow': 'spin 3s linear infinite',
      },
      keyframes: {
        flip: {
          '0%': { transform: 'rotateY(0deg)' },
          '50%': { transform: 'rotateY(90deg)' },
          '100%': { transform: 'rotateY(180deg)' },
        },
        'flip-back': {
          '0%': { transform: 'rotateY(180deg)' },
          '50%': { transform: 'rotateY(90deg)' },
          '100%': { transform: 'rotateY(0deg)' },
        },
        'vu-meter': {
          '0%': { transform: 'scaleY(0)' },
          '100%': { transform: 'scaleY(1)' },
        },
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 5px currentColor' },
          '50%': { boxShadow: '0 0 20px currentColor' },
        },
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '112': '28rem',
        '128': '32rem',
      },
      borderRadius: {
        'sm': '2px',
      },
      transitionDuration: {
        '400': '400ms',
      },
    },
  },
  plugins: [],
}
