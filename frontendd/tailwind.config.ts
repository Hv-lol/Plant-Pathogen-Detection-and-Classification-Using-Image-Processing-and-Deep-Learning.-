import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: "var(--color-forest)",
        emerald: "var(--color-emerald)",
        leaf: "var(--color-leaf)",
        mist: "var(--color-mist)",
        charcoal: "var(--color-charcoal)",
        moss: "var(--color-moss)",
        sage: "var(--color-sage)",
        cream: "var(--color-cream)",
        danger: "var(--color-danger)",
        warning: "var(--color-warning)",
      },
      fontFamily: {
        sans: ["var(--font-manrope)", "system-ui", "sans-serif"],
        display: ["var(--font-source-serif)", "Georgia", "serif"],
      },
      boxShadow: {
        soft: "0 12px 40px -16px rgba(15, 31, 23, 0.35)",
        inset: "inset 0 1px 0 rgba(255,255,255,0.06)",
      },
      backgroundImage: {
        "forest-glow":
          "radial-gradient(ellipse 80% 60% at 70% 10%, rgba(61,139,110,0.28), transparent 55%), radial-gradient(ellipse 50% 40% at 10% 80%, rgba(31,111,84,0.22), transparent 50%)",
        "leaf-mesh":
          "linear-gradient(135deg, rgba(15,31,23,0.92), rgba(28,36,32,0.88)), url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%233d8b6e' fill-opacity='0.06'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
      },
      transitionTimingFunction: {
        smooth: "cubic-bezier(0.22, 1, 0.36, 1)",
      },
    },
  },
  plugins: [],
};

export default config;
