/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          500: '#3981e6',
          600: '#2563eb', 
          700: '#0447d7',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
  // Important: Disable preflight to avoid conflicts with Ant Design
  corePlugins: {
    preflight: false,
  },
}