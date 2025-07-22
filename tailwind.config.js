
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js",
    "./static/**/*.html"
  ],
  theme: {
    extend: {
      colors: {
        'signature-grey': '#6B7280',
        'main-accent-pink': '#E0218A',
        'accessible-grey': '#4B5563',
        'container-bg': '#374151',
        'border-color': '#4b5563',
        'nav-bg': '#374151',
        'nav-border': '#4b5563'
      },
      fontFamily: {
        'playfair': ['Playfair Display', 'serif'],
        'alice': ['Alice', 'serif'],
        'times-new-roman': ['Times New Roman', 'serif'],
        'inter': ['Inter', 'sans-serif']
      }
    },
  },
  plugins: [],
}
