/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#5B5BF0',
        'primary-dark': '#4545D4',
        dark: '#080B1A',
        dark2: '#0C0F24',
        light: '#F4F5FA',
        muted: '#6B7280',
        border: '#E5E7EB',
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
