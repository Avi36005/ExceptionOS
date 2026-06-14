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
        // Purple-blackish sidebar palette
        sidebar: '#171430',
        'sidebar-2': '#0F0D24',
        'sidebar-accent': '#241F4A',
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 2px rgba(16,24,40,.04), 0 1px 3px rgba(16,24,40,.06)',
        'card-hover': '0 12px 32px rgba(16,24,40,.10)',
        sidebar: '0 0 0 1px rgba(255,255,255,.04)',
      },
    },
  },
  plugins: [],
}
