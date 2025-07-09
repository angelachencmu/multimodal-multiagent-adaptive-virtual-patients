/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        purple: '#1f7a8c',
        blue: '#e1e5f2',
        teal: '#97C8D5',
        lightGray: '#ebebeb',
        coral: '#003459',
      },
    },
  },
  plugins: [],
}
