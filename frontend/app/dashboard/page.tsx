"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { Badge } from "@/components/Badge";
import { Button } from "@/components/Button";
import { EmptyState } from "@/components/EmptyState";
import { MetricStat } from "@/components/MetricStat";
import {
  api,
  ApiError,
  type AnalyticsOverview,
  type Diagnosis,
} from "@/lib/api";
import { formatConfidence, formatDate } from "@/lib/utils";
import { useRouter } from "next/navigation";

function statusTone(status: string) {
  const s = status.toUpperCase();
  if (s === "COMPLETED") return "success" as const;
  if (s === "FAILED") return "danger" as const;
  return "info" as const;
}

export default function DashboardPage() {
  const router = useRouter();
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [recent, setRecent] = useState<Diagnosis[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [ov, list] = await Promise.all([
          api.analyticsOverview(),
          api.listDiagnoses(),
        ]);
        if (cancelled) return;
        setOverview(ov);
        setRecent(list.slice(0, 6));
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : "Failed to load dashboard.");
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
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="eyebrow">Overview</p>
          <h1 className="mt-2 font-display text-4xl text-charcoal">Dashboard</h1>
          <p className="mt-2 max-w-xl text-sm text-charcoal/60">
            Track analysis volume, confidence trends, and your latest diagnoses.
          </p>
        </div>
        <Link href="/analyze">
          <Button>New analysis</Button>
        </Link>
      </div>

      {error && <p className="mt-6 text-sm text-danger">{error}</p>}

      {loading ? (
        <p className="mt-12 text-sm text-charcoal/45">Loading metrics…</p>
      ) : (
        <>
          <div className="mt-12 grid gap-8 border-y border-charcoal/10 py-10 sm:grid-cols-2 lg:grid-cols-3">
            <MetricStat
              label="Total diagnoses"
              value={overview?.total_diagnoses ?? 0}
            />
            <MetricStat
              label="Completed"
              value={overview?.completed_diagnoses ?? 0}
              hint={`${overview?.failed_diagnoses ?? 0} failed`}
            />
            <MetricStat
              label="Avg. confidence"
              value={formatConfidence(overview?.average_confidence)}
            />
            <MetricStat
              label="Healthy detections"
              value={overview?.healthy_detections ?? 0}
            />
            <MetricStat
              label="Diseased detections"
              value={overview?.diseased_detections ?? 0}
            />
          </div>

          <section className="mt-12">
            <div className="flex items-baseline justify-between gap-4">
              <h2 className="font-display text-2xl">Recent diagnoses</h2>
              <Link href="/history" className="text-sm text-emerald link-underline">
                View history
              </Link>
            </div>

            {recent.length === 0 ? (
              <EmptyState
                title="No diagnoses yet"
                description="Upload a leaf image to run your first visual symptom analysis."
                actionLabel="Analyze an image"
                onAction={() => router.push("/analyze")}
              />
            ) : (
              <ul className="mt-6 divide-y divide-charcoal/10">
                {recent.map((d) => {
                  const top = d.predictions?.[0];
                  return (
                    <li key={d.id}>
                      <Link
                        href={`/diagnosis/${d.id}`}
                        className="flex flex-wrap items-center justify-between gap-3 py-4 transition-colors hover:bg-white/60"
                      >
                        <div>
                          <p className="font-medium text-charcoal">
                            {top?.label || "Pending classification"}
                          </p>
                          <p className="mt-0.5 text-xs text-charcoal/45">
                            {formatDate(d.created_at)}
                          </p>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-sm text-charcoal/55">
                            {formatConfidence(d.overall_confidence ?? top?.probability)}
                          </span>
                          <Badge tone={statusTone(d.status)}>{d.status}</Badge>
                        </div>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            )}
          </section>
        </>
      )}
    </AppShell>
  );
}
