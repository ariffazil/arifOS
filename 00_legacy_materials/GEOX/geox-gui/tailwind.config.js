/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Constitutional floor colors
        'floor-green': '#22c55e',
        'floor-amber': '#f59e0b',
        'floor-red': '#ef4444',
        'floor-grey': '#94a3b8',
      },
      fontFamily: {
        mono: ['Menlo', 'Monaco', 'Courier New', 'monospace'],
      },
    },
  },
  plugins: [],
}
