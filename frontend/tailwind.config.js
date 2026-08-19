/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        blueprint: {
          950: "#070B12",
          900: "#0B111C",
          800: "#111A29",
          700: "#182236",
          600: "#26344C",
        },
        cyan: {
          glow: "#4FD8FF",
          soft: "#8FE7FF",
        },
        amber: {
          flag: "#FFB454",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
      backgroundImage: {
        "blueprint-grid":
          "linear-gradient(rgba(79,216,255,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(79,216,255,0.06) 1px, transparent 1px)",
      },
      backgroundSize: {
        grid: "28px 28px",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(79,216,255,0.15), 0 0 24px rgba(79,216,255,0.08)",
      },
    },
  },
  plugins: [],
};
