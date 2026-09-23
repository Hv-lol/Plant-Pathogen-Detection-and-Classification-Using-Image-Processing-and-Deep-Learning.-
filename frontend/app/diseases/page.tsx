"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { EmptyState } from "@/components/EmptyState";
import { Input } from "@/components/Input";
import { api, ApiError, type Disease } from "@/lib/api";

export default function DiseasesPage() {
  const [q, setQ] = useState("");
  const [diseases, setDiseases] = useState<Disease[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const handle = window.setTimeout(async () => {
      setLoading(true);
      try {
        const rows = await api.listDiseases(q || undefined);
        if (!cancelled) setDiseases(rows);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : "Failed to load diseases.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, 200);
    return () => {
      cancelled = true;
      window.clearTimeout(handle);
    };
  }, [q]);

  return (
    <AppShell>
      <div className="max-w-2xl">
        <p className="eyebrow">Knowledge</p>
        <h1 className="mt-2 font-display text-4xl text-charcoal">Pathogen categories</h1>
        <p className="mt-3 text-sm text-charcoal/60">
          Reference for the five visual classes in this model: Bacteria, Fungi,
          Healthy, Pests, and Virus. Educational context only—not lab diagnostics.
        </p>
      </div>

      <div className="mt-8 max-w-md">
        <Input
          label="Search"
          placeholder="Search by name…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
      </div>

      {error && <p className="mt-6 text-sm text-danger">{error}</p>}

      {loading ? (
        <p className="mt-10 text-sm text-charcoal/45">Loading…</p>
      ) : diseases.length === 0 ? (
        <EmptyState
          title="No matches"
          description="Try a different search term or browse when the knowledge base is populated."
        />
      ) : (
        <ul className="mt-10 divide-y divide-charcoal/10">
          {diseases.map((d) => (
            <li key={d.id}>
              <Link
                href={`/diseases/${d.slug}`}
                className="group flex flex-col gap-1 py-5 transition-colors hover:bg-white/50 sm:flex-row sm:items-baseline sm:justify-between"
              >
                <div>
                  <h2 className="font-display text-xl text-charcoal group-hover:text-emerald">
                    {d.name}
                  </h2>
                  {d.pathogen_type && (
                    <p className="mt-1 text-xs uppercase tracking-wider text-charcoal/40">
                      {d.pathogen_type}
                      {d.pathogen_name ? ` · ${d.pathogen_name}` : ""}
                    </p>
                  )}
                </div>
                <p className="max-w-md text-sm text-charcoal/55 line-clamp-2">
                  {d.description || d.symptoms || "View details"}
                </p>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </AppShell>
  );
}
