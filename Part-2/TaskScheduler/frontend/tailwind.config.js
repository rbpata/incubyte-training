/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Minimal color palette
        'glass-light': 'rgba(255, 255, 255, 0.6)',
        'glass-medium': 'rgba(255, 255, 255, 0.5)',
        'glass-dark': 'rgba(255, 255, 255, 0.4)',
      },
      backdropBlur: {
        'glass': '12px',
        'glass-sm': '8px',
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
        'glass-md': '0 4px 18px 0 rgba(31, 38, 135, 0.1)',
        'glass-lg': '0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      },
      borderColor: {
        'glass': 'rgba(255, 255, 255, 0.8)',
        'glass-light': 'rgba(0, 0, 0, 0.04)',
      },
      animation: {
        'shimmer': 'shimmer 3s ease-in-out infinite',
        'slide-in': 'slideIn 0.3s ease',
        'fade-in': 'fadeIn 0.2s ease',
      },
      keyframes: {
        shimmer: {
          '0%, 100%': { left: '-100%' },
          '50%': { left: '100%' },
        },
        slideIn: {
          'from': {
            opacity: '0',
            transform: 'translateY(-10px)',
          },
          'to': {
            opacity: '1',
            transform: 'translateY(0)',
          },
        },
        fadeIn: {
          'from': { opacity: '0' },
          'to': { opacity: '1' },
        },
      },
      spacing: {
        'glass': '1.5rem',
        'glass-lg': '2.5rem',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
