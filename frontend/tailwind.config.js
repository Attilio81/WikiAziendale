/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#F7F3EE',
        surface: '#FFFFFF',
        nav: '#1B2840',
        accent: '#B5492C',
        'accent-light': '#F0E0DA',
        border: '#E2DDD8',
        muted: '#6B6B6B',
      },
      fontFamily: {
        display: ['Fraunces', 'Georgia', 'serif'],
        sans: ['DM Sans', 'system-ui', 'sans-serif'],
        mono: ['DM Mono', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '2px',
        sm: '2px',
        md: '2px',
        lg: '4px',
      },
    },
  },
  plugins: [],
}
