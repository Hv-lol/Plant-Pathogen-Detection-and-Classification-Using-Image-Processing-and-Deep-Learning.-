import { AppShell } from "@/components/AppShell";

const sections = [
  {
    title: "Limitations",
    body: [
      "PlantGuard AI maps photographs to five visual categories: Bacteria, Fungi, Healthy, Pests, and Virus. It does not culture pathogens, run PCR, or confirm species in a laboratory.",
      "Results can be affected by lighting, focus, occlusion, mixed symptoms, and images outside the training distribution.",
      "Always treat outputs as decision-support—not as definitive species-level diagnosis for high-stakes or regulatory decisions.",
    ],
  },
  {
    title: "Understanding confidence",
    body: [
      "Confidence reflects how strongly the model favors a visual class given the submitted image—not the biological certainty that a pathogen is present.",
      "High confidence on a misframed or low-quality image can still be wrong. Low confidence often means ambiguous symptoms or unfamiliar conditions.",
      "Review ranked alternatives and the attention heatmap together before acting on a single label.",
    ],
  },
  {
    title: "Image tips",
    body: [
      "Photograph a single leaf or clear lesion area when possible; fill the frame without extreme zoom noise.",
      "Use diffuse natural light; avoid harsh shadows, flash glare, and heavy motion blur.",
      "Include both symptomatic and adjacent healthy tissue when helpful, and keep backgrounds simple.",
      "Prefer JPEG, PNG, or WebP. Very dark, tiny, or heavily compressed images may fail quality checks.",
    ],
  },
];

export default function HelpPage() {
  return (
    <AppShell>
      <div className="max-w-2xl">
        <p className="eyebrow">Support</p>
        <h1 className="mt-2 font-display text-4xl text-charcoal">Help & guidance</h1>
        <p className="mt-3 text-sm leading-relaxed text-charcoal/60">
          How to interpret PlantGuard results responsibly and capture imagery
          that gives the models their best chance.
        </p>
      </div>

      <div className="mt-14 max-w-3xl space-y-14">
        {sections.map((section) => (
          <section key={section.title} className="border-t border-charcoal/10 pt-8">
            <h2 className="font-display text-2xl text-charcoal">{section.title}</h2>
            <ul className="mt-5 space-y-4">
              {section.body.map((item) => (
                <li
                  key={item}
                  className="text-sm leading-relaxed text-charcoal/70 pl-4 border-l-2 border-leaf/40"
                >
                  {item}
                </li>
              ))}
            </ul>
          </section>
        ))}

        <aside className="rounded-md bg-cream/80 px-5 py-4 text-sm leading-relaxed text-charcoal/70">
          <strong className="font-medium text-charcoal">Scientific disclaimer: </strong>
          Visual symptom classification is not laboratory-confirmed pathogen
          identification. Consult qualified agronomic or plant pathology experts
          when disease confirmation is required.
        </aside>
      </div>
    </AppShell>
  );
}
