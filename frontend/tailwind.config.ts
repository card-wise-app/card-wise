import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#F7F7F5",
        ink: "#17171C",
        lime: "#C1FF72",
        limeDark: "#9EDB4A",
        line: "#E5E5E2",
        muted: "#777777",
        card: "#FFFFFF",
      },
      fontFamily: {
        display: ["'Space Grotesk'", "system-ui", "sans-serif"],
        body: ["Inter", "system-ui", "sans-serif"],
      },
      borderRadius: {
        xl2: "20px",
        xl3: "24px",
      },
      boxShadow: {
        soft: "0 1px 0 rgba(23,23,28,0.06), 0 12px 32px rgba(23,23,28,0.06)",
      },
    },
  },
  plugins: [],
};
export default config;
