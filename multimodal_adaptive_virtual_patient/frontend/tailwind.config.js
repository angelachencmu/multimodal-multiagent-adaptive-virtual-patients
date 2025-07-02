/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        purple: '#52489c',
        blue: '#4062bb',
        teal: '#59c3c3',
        lightGray: '#ebebeb',
        coral: '#f45b69',
      },
    },
  },
  plugins: [],
}
