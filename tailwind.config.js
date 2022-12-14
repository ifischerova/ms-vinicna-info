/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["app/templates/*.{html,js}"],
  theme: {
    fontFamily: {
      'sans': ['Poppins', 'sans-serif'],
    },
    screens: {
      'sm': '600px',

      'md': '900px',

      'lg': '1200px',

      'xl': '1440px',
    },
    extend: {},
  },
  safelist: [
    'flash-success',
    'flash-close-success',
    'flash-error',
    'flash-close-error',
  ],
  darkMode: 'class',
  plugins: [],  
}
