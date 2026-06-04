import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0b1020",
        panel: "#121a2e",
        panel2: "#1a2540",
        accent: "#5b8cff",
      },
    },
  },
  plugins: [],
};
export default config;
