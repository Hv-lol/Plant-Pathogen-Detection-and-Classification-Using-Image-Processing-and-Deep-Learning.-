import Link from "next/link";
import { MarketingShell } from "@/components/AppShell";
import { Button } from "@/components/Button";

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

export default function HomePage() {
  return (
    <MarketingShell>
      <section className="relative overflow-hidden bg-leaf-mesh">
        <div className="pointer-events-none absolute inset-0 bg-forest-glow" />
        <div className="container-narrow section-pad relative grid min-h-[calc(100vh-4rem)] items-center gap-12 py-20 lg:grid-cols-[1.15fr_0.85fr]">
          <div className="slide-up max-w-xl">
            <p className="eyebrow text-leaf">PlantGuard AI</p>
            <h1 className="mt-5 font-display text-4xl leading-[1.08] tracking-tight text-white sm:text-5xl lg:text-6xl">
              Detect Plant Diseases with AI.
            </h1>
            <p className="mt-6 max-w-lg text-base leading-relaxed text-cream/75 sm:text-lg">
              Upload plant imagery for rapid visual classification into Bacteria,
              Fungi, Healthy, Pests, or Virus—with confidence scores and advisory
              guidance for growers and agronomists.
            </p>
            <div className="mt-9 flex flex-wrap gap-3">
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
            </div>
          </div>

          <div className="fade-in relative hidden lg:block">
            <div className="aspect-[4/5] overflow-hidden rounded-sm bg-gradient-to-br from-moss via-emerald to-forest shadow-soft">
              <div className="absolute inset-0 opacity-40"
                style={{
                  backgroundImage:
                    "radial-gradient(circle at 30% 40%, rgba(243,246,242,0.25), transparent 45%), radial-gradient(circle at 70% 70%, rgba(143,173,156,0.35), transparent 40%)",
                }}
              />
              <div className="absolute inset-x-0 bottom-0 p-8">
                <p className="text-xs uppercase tracking-[0.18em] text-cream/60">
                  Field intelligence
                </p>
                <p className="mt-2 font-display text-2xl text-white">
                  From canopy to confidence score in minutes.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="technology" className="bg-mist text-charcoal">
        <div className="container-narrow section-pad py-20 lg:py-28">
          <div className="max-w-2xl">
            <p className="eyebrow">How it works</p>
            <h2 className="mt-3 font-display text-3xl sm:text-4xl">
              A clear path from image to insight.
            </h2>
            <p className="mt-4 text-base leading-relaxed text-charcoal/65">
              PlantGuard orchestrates quality checks, leaf detection, symptom
              analysis, and explanation overlays—without claiming laboratory
              confirmation.
            </p>
          </div>

          <ol className="mt-14 grid gap-10 md:grid-cols-3 md:gap-12">
            {steps.map((step, i) => (
              <li key={step.title} className="slide-up border-t border-charcoal/10 pt-6">
                <span className="text-xs font-semibold text-emerald">
                  0{i + 1}
                </span>
                <h3 className="mt-3 font-display text-2xl">{step.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-charcoal/60">
                  {step.body}
                </p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="border-t border-charcoal/10 bg-cream text-charcoal">
        <div className="container-narrow section-pad py-14">
          <p className="eyebrow">Scientific note</p>
          <p className="mt-3 max-w-3xl text-base leading-relaxed text-charcoal/70">
            PlantGuard AI performs visual symptom classification and advisory
            assessment. Outputs are not laboratory-confirmed pathogen
            identification and should not replace agronomic expertise or
            diagnostic lab testing when stakes are high.
          </p>
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
