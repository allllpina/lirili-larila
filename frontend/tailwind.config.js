/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Ми даємо нашому кольору назву "alpine"
        alpine: {
          DEFAULT: '#1B5448', // Основний колір
          light: '#2C7A6A',   // Світліша версія (знадобиться для темної теми пізніше)
        }
      },
      fontFamily: {
        montserrat: ['Montserrat', 'sans-serif'],
      }
    },
  },
  plugins: [],
}