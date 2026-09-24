"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { MarketingShell } from "@/components/AppShell";
import { Button } from "@/components/Button";
import { Reveal } from "@/components/Reveal";
import { AnimatedNumber } from "@/components/AnimatedNumber";
import { staggerContainer, staggerItem, fadeUp, easeSmooth } from "@/lib/motion";

const steps = [
  {
    title: "Capture",
    body: "Photograph a clear, well-lit leaf or canopy region showing visible symptoms.",
  },
  {
    title: "Analyze",
    body: "Our models assess image quality, locate foliage, and classify visual symptom patterns.",
  },
  {
    title: "Advise",
    body: "Review ranked predictions, confidence, severity cues, and sourced management notes.",
  },
];

const classes = ["Bacteria", "Fungi", "Healthy", "Pests", "Virus"];

const benchmarks = [
  { value: 99.48, suffix: "%", label: "Test accuracy", hint: "Full-dataset ResNet-18 benchmark" },
  { value: 5, suffix: "", label: "Symptom classes", hint: "Bacteria · Fungi · Healthy · Pests · Virus" },
  { value: 39997, suffix: "", label: "Benchmark images", hint: "Train / validation / test split" },
];

function ScanVisual() {
  return (
    <div className="relative aspect-[4/5] overflow-hidden rounded-sm bg-gradient-to-br from-moss via-emerald to-forest shadow-soft">
      <div
        className="absolute inset-0 opacity-40"
        style={{
          backgroundImage:
            "radial-gradient(circle at 30% 40%, rgba(243,246,242,0.25), transparent 45%), radial-gradient(circle at 70% 70%, rgba(143,173,156,0.35), transparent 40%)",
        }}
      />
      {/* Leaf silhouette */}
      <motion.svg
        viewBox="0 0 200 240"
        className="absolute left-1/2 top-1/2 h-[62%] w-[62%] -translate-x-1/2 -translate-y-1/2 opacity-90"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 0.9, scale: 1, y: [0, -8, 0] }}
        transition={{
          opacity: { duration: 0.8, ease: easeSmooth },
          scale: { duration: 0.8, ease: easeSmooth },
          y: { duration: 6, repeat: Infinity, ease: "easeInOut" },
        }}
      >
        <path
          d="M100 10c55 20 90 70 90 120 0 60-45 100-90 100S10 190 10 130C10 80 45 30 100 10Z"
          fill="rgba(232,240,234,0.14)"
          stroke="rgba(232,240,234,0.5)"
          strokeWidth="1.5"
        />
        <path
          d="M100 30v190M100 90c-18 6-32 20-38 40M100 90c18 6 32 20 38 40M100 140c-22 6-38 22-44 46M100 140c22 6 38 22 44 46"
          fill="none"
          stroke="rgba(232,240,234,0.45)"
          strokeWidth="1.25"
          strokeLinecap="round"
        />
      </motion.svg>

      {/* Scan line */}
      <motion.div
        className="absolute inset-x-6 h-px bg-gradient-to-r from-transparent via-cream/80 to-transparent"
        style={{ boxShadow: "0 0 12px 1px rgba(232,240,234,0.6)" }}
        initial={{ top: "18%" }}
        animate={{ top: ["18%", "82%", "18%"] }}
        transition={{ duration: 4.5, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Confidence chip */}
      <motion.div
        className="absolute right-6 top-6 rounded-md bg-forest/70 px-3 py-1.5 text-xs text-cream backdrop-blur-sm"
        initial={{ opacity: 0, x: 10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.6, duration: 0.5 }}
      >
        Fungi · 94.7% confidence
      </motion.div>

      <div className="absolute inset-x-0 bottom-0 p-8">
        <p className="text-xs uppercase tracking-[0.18em] text-cream/60">
          Field intelligence
        </p>
        <p className="mt-2 font-display text-2xl text-white">
          From canopy to confidence score in minutes.
        </p>
      </div>
    </div>
  );
}

export default function HomePage() {
  return (
    <MarketingShell>
      <section className="relative overflow-hidden bg-leaf-mesh">
        <div className="pointer-events-none absolute inset-0 bg-forest-glow" />
        <div className="container-narrow section-pad relative grid min-h-[calc(100vh-4rem)] items-center gap-12 py-20 lg:grid-cols-[1.15fr_0.85fr]">
          <motion.div
            className="max-w-xl"
            initial="hidden"
            animate="show"
            variants={staggerContainer}
          >
            <motion.p variants={staggerItem} className="eyebrow text-leaf">
              PlantGuard AI
            </motion.p>
            <motion.h1
              variants={staggerItem}
              className="mt-5 font-display text-4xl leading-[1.08] tracking-tight text-white sm:text-5xl lg:text-6xl"
            >
              Detect Plant Diseases with AI.
            </motion.h1>
            <motion.p
              variants={staggerItem}
              className="mt-6 max-w-lg text-base leading-relaxed text-cream/75 sm:text-lg"
            >
              Upload plant imagery for rapid visual classification into Bacteria,
              Fungi, Healthy, Pests, or Virus—with confidence scores and advisory
              guidance for growers and agronomists.
            </motion.p>
            <motion.div variants={staggerItem} className="mt-9 flex flex-wrap gap-3">
              <Link href="/analyze">
                <Button size="lg">Analyze</Button>
              </Link>
              <a href="#technology">
                <Button
                  size="lg"
                  variant="outline"
                  className="border-cream/30 text-cream hover:border-leaf hover:text-white"
                >
                  Explore Technology
                </Button>
              </a>
            </motion.div>
            <motion.div
              variants={staggerItem}
              className="mt-10 flex flex-wrap gap-x-8 gap-y-4 border-t border-white/10 pt-6"
            >
              {benchmarks.map((b) => (
                <div key={b.label}>
                  <p className="font-display text-2xl text-white">
                    <AnimatedNumber
                      value={b.value}
                      format={(n) =>
                        b.label === "Test accuracy"
                          ? `${(b.value).toFixed(2)}%`
                          : n.toLocaleString()
                      }
                    />
                  </p>
                  <p className="mt-0.5 text-xs text-cream/55">{b.label}</p>
                </div>
              ))}
            </motion.div>
          </motion.div>

          <motion.div
            className="relative hidden lg:block"
            initial={{ opacity: 0, scale: 0.94 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, ease: easeSmooth, delay: 0.2 }}
          >
            <ScanVisual />
          </motion.div>
        </div>
      </section>

      <section id="technology" className="bg-mist text-charcoal">
        <div className="container-narrow section-pad py-20 lg:py-28">
          <Reveal className="max-w-2xl">
            <p className="eyebrow">How it works</p>
            <h2 className="mt-3 font-display text-3xl sm:text-4xl">
              A clear path from image to insight.
            </h2>
            <p className="mt-4 text-base leading-relaxed text-charcoal/65">
              PlantGuard orchestrates quality checks, leaf detection, symptom
              analysis, and explanation overlays—without claiming laboratory
              confirmation.
            </p>
          </Reveal>

          <motion.ol
            className="mt-14 grid gap-10 md:grid-cols-3 md:gap-12"
            initial="hidden"
            whileInView="show"
            viewport={{ once: true, margin: "-80px" }}
            variants={staggerContainer}
          >
            {steps.map((step, i) => (
              <motion.li
                key={step.title}
                variants={staggerItem}
                whileHover={{ y: -4 }}
                transition={{ duration: 0.25, ease: easeSmooth }}
                className="border-t border-charcoal/10 pt-6"
              >
                <span className="text-xs font-semibold text-emerald">
                  0{i + 1}
                </span>
                <h3 className="mt-3 font-display text-2xl">{step.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-charcoal/60">
                  {step.body}
                </p>
              </motion.li>
            ))}
          </motion.ol>
        </div>
      </section>

      <section className="border-t border-charcoal/10 bg-forest text-cream">
        <div className="container-narrow section-pad py-20">
          <Reveal className="max-w-2xl">
            <p className="eyebrow text-leaf">Symptom classes</p>
            <h2 className="mt-3 font-display text-3xl sm:text-4xl">
              Five visual categories, ranked by confidence.
            </h2>
          </Reveal>
          <motion.div
            className="mt-10 flex flex-wrap gap-3"
            initial="hidden"
            whileInView="show"
            viewport={{ once: true, margin: "-80px" }}
            variants={staggerContainer}
          >
            {classes.map((c) => (
              <motion.span
                key={c}
                variants={staggerItem}
                whileHover={{ y: -2, borderColor: "rgba(61,139,110,0.8)" }}
                className="rounded-full border border-white/15 bg-white/5 px-5 py-2.5 text-sm text-cream/85 transition-colors"
              >
                {c}
              </motion.span>
            ))}
          </motion.div>
        </div>
      </section>

      <section className="border-t border-charcoal/10 bg-cream text-charcoal">
        <div className="container-narrow section-pad py-14">
          <Reveal variants={fadeUp}>
            <p className="eyebrow">Scientific note</p>
            <p className="mt-3 max-w-3xl text-base leading-relaxed text-charcoal/70">
              PlantGuard AI performs visual symptom classification and advisory
              assessment. Outputs are not laboratory-confirmed pathogen
              identification and should not replace agronomic expertise or
              diagnostic lab testing when stakes are high.
            </p>
          </Reveal>
        </div>
      </section>

      <footer className="border-t border-white/10 bg-forest py-10 text-cream/55">
        <div className="container-narrow section-pad flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <p className="font-display text-lg text-cream">PlantGuard AI</p>
          <div className="flex gap-6 text-sm">
            <Link href="/help" className="hover:text-cream">
              Help
            </Link>
            <Link href="/diseases" className="hover:text-cream">
              Disease library
            </Link>
            <Link href="/register" className="hover:text-cream">
              Create account
            </Link>
          </div>
        </div>
      </footer>
    </MarketingShell>
  );
}
