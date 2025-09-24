import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#0B6EFE",
          foreground: "#ffffff"
        },
        muted: {
          DEFAULT: "#F4F4F5",
          foreground: "#71717A"
        }
      },
      borderRadius: {
        xl: "1.25rem"
      }
    }
  },
  plugins: []
};

export default config;
