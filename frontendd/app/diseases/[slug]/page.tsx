"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { Badge } from "@/components/Badge";
import { api, ApiError, type Disease } from "@/lib/api";

function Section({ title, body }: { title: string; body?: string | null }) {
  if (!body) return null;
  return (
    <section className="border-t border-charcoal/10 pt-8">
      <h2 className="font-display text-2xl text-charcoal">{title}</h2>
      <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-charcoal/70">
        {body}
      </p>
    </section>
  );
}

export default function DiseaseDetailPage() {
  const params = useParams<{ slug: string }>();
  const slug = params.slug;
  const [disease, setDisease] = useState<Disease | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await api.getDisease(slug);
        if (!cancelled) setDisease(data);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : "Disease not found.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [slug]);

  return (
    <AppShell>
      <Link href="/diseases" className="text-sm text-emerald link-underline">
        ← Disease library
      </Link>

      {loading && <p className="mt-10 text-sm text-charcoal/45">Loading…</p>}
      {error && <p className="mt-10 text-sm text-danger">{error}</p>}

      {disease && (
        <article className="mt-8 max-w-3xl space-y-10 slide-up">
          <header>
            <div className="flex flex-wrap gap-2">
              {disease.pathogen_type && <Badge tone="info">{disease.pathogen_type}</Badge>}
            </div>
            <h1 className="mt-4 font-display text-4xl text-charcoal sm:text-5xl">
              {disease.name}
            </h1>
            {disease.pathogen_name && (
              <p className="mt-3 font-display text-lg italic text-charcoal/55">
                {disease.pathogen_name}
              </p>
            )}
            {disease.description && (
              <p className="mt-5 text-base leading-relaxed text-charcoal/70">
                {disease.description}
              </p>
            )}
          </header>

          <Section title="Symptoms" body={disease.symptoms} />
          <Section title="Cause" body={disease.cause} />
          <Section title="Prevention" body={disease.prevention} />
          <Section title="Management notes" body={disease.management_notes} />

          <aside className="rounded-md bg-cream/80 px-5 py-4 text-sm text-charcoal/65">
            Knowledge entries support education and awareness. Confirm critical
            decisions with qualified agronomists or laboratory testing—PlantGuard
            does not provide laboratory pathogen confirmation.
          </aside>
        </article>
      )}
    </AppShell>
  );
}
