/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        accent: {
          lime: '#84cc16', // Verde Lima más suave y legible
          electric: '#ff6b35', // Naranja Eléctrico
        },
      },
    },
  },
  plugins: [],
}
