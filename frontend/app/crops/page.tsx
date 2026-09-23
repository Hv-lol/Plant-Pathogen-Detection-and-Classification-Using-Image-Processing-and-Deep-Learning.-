"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { EmptyState } from "@/components/EmptyState";
import { api, ApiError, type Crop } from "@/lib/api";

export default function CropsPage() {
  const [crops, setCrops] = useState<Crop[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const rows = await api.listCrops();
        if (!cancelled) setCrops(rows);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : "Failed to load crops.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <AppShell>
      <div className="max-w-2xl">
        <p className="eyebrow">Knowledge</p>
        <h1 className="mt-2 font-display text-4xl text-charcoal">Crops</h1>
        <p className="mt-3 text-sm text-charcoal/60">
          This release classifies pathogen categories across general field-crop
          imagery (not crop-specific disease names).
        </p>
      </div>

      {error && <p className="mt-6 text-sm text-danger">{error}</p>}

      {loading ? (
        <p className="mt-10 text-sm text-charcoal/45">Loading…</p>
      ) : crops.length === 0 ? (
        <EmptyState
          title="No crops listed"
          description="Crop entries will appear here once the knowledge base is seeded."
        />
      ) : (
        <ul className="mt-12 grid gap-x-10 gap-y-8 sm:grid-cols-2 lg:grid-cols-3">
          {crops.map((c) => (
            <li key={c.id} className="border-t border-charcoal/10 pt-5">
              <h2 className="font-display text-2xl text-charcoal">{c.name}</h2>
              {c.scientific_name && (
                <p className="mt-1 text-sm italic text-charcoal/50">
                  {c.scientific_name}
                </p>
              )}
              {c.description && (
                <p className="mt-3 text-sm leading-relaxed text-charcoal/60">
                  {c.description}
                </p>
              )}
            </li>
          ))}
        </ul>
      )}
    </AppShell>
  );
}
