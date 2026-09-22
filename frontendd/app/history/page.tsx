"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { Badge } from "@/components/Badge";
import { EmptyState } from "@/components/EmptyState";
import { api, ApiError, type Diagnosis } from "@/lib/api";
import { formatConfidence, formatDate } from "@/lib/utils";

function statusTone(status: string) {
  const s = status.toUpperCase();
  if (s === "COMPLETED") return "success" as const;
  if (s === "FAILED") return "danger" as const;
  return "info" as const;
}

export default function HistoryPage() {
  const router = useRouter();
  const [rows, setRows] = useState<Diagnosis[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const list = await api.listDiagnoses();
        if (!cancelled) setRows(list);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : "Failed to load history.");
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
      <div>
        <p className="eyebrow">Archive</p>
        <h1 className="mt-2 font-display text-4xl text-charcoal">Diagnosis history</h1>
        <p className="mt-3 max-w-xl text-sm text-charcoal/60">
          Every analysis you run is listed here with status, top prediction, and
          confidence.
        </p>
      </div>

      {error && <p className="mt-6 text-sm text-danger">{error}</p>}

      {loading ? (
        <p className="mt-10 text-sm text-charcoal/45">Loading…</p>
      ) : rows.length === 0 ? (
        <EmptyState
          title="No history yet"
          description="Run an analysis to build your diagnosis archive."
          actionLabel="Analyze an image"
          onAction={() => router.push("/analyze")}
        />
      ) : (
        <div className="mt-10 overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead>
              <tr className="border-b border-charcoal/15 text-xs uppercase tracking-[0.12em] text-charcoal/45">
                <th className="pb-3 font-semibold">Date</th>
                <th className="pb-3 font-semibold">Top prediction</th>
                <th className="pb-3 font-semibold">Confidence</th>
                <th className="pb-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((d) => {
                const top = d.predictions?.[0];
                return (
                  <tr
                    key={d.id}
                    className="border-b border-charcoal/8 transition-colors hover:bg-white/60"
                  >
                    <td className="py-4 text-charcoal/60">{formatDate(d.created_at)}</td>
                    <td className="py-4">
                      <Link
                        href={`/diagnosis/${d.id}`}
                        className="font-medium text-charcoal hover:text-emerald"
                      >
                        {top?.label || "Pending"}
                      </Link>
                    </td>
                    <td className="py-4 text-charcoal/65">
                      {formatConfidence(d.overall_confidence ?? top?.probability)}
                    </td>
                    <td className="py-4">
                      <Badge tone={statusTone(d.status)}>{d.status}</Badge>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </AppShell>
  );
}
