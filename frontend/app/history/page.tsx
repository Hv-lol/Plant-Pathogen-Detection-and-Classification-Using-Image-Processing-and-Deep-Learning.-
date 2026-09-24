"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { AppShell } from "@/components/AppShell";
import { Badge } from "@/components/Badge";
import { EmptyState } from "@/components/EmptyState";
import { Skeleton } from "@/components/Skeleton";
import { useToast } from "@/components/Toast";
import { api, ApiError, type Diagnosis } from "@/lib/api";
import { formatConfidence, formatDate } from "@/lib/utils";
import { fadeUp, staggerContainer, staggerItem } from "@/lib/motion";

function statusTone(status: string) {
  const s = status.toUpperCase();
  if (s === "COMPLETED") return "success" as const;
  if (s === "FAILED") return "danger" as const;
  return "info" as const;
}

export default function HistoryPage() {
  const router = useRouter();
  const toast = useToast();
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
          const message = err instanceof ApiError ? err.message : "Failed to load history.";
          setError(message);
          toast.push({ title: "Couldn't load history", description: message, tone: "error" });
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <AppShell>
      <motion.div initial="hidden" animate="show" variants={fadeUp}>
        <p className="eyebrow">Archive</p>
        <h1 className="mt-2 font-display text-4xl text-charcoal">Diagnosis history</h1>
        <p className="mt-3 max-w-xl text-sm text-charcoal/60">
          Every analysis you run is listed here with status, top prediction, and
          confidence.
        </p>
      </motion.div>

      {!loading && error && <p className="mt-6 text-sm text-danger">{error}</p>}

      {loading ? (
        <div className="mt-10 space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex items-center justify-between gap-4 border-b border-charcoal/8 py-4">
              <Skeleton className="h-4 w-28" />
              <Skeleton className="h-4 w-40" />
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-6 w-20 rounded-full" />
            </div>
          ))}
        </div>
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
            <motion.tbody initial="hidden" animate="show" variants={staggerContainer}>
              {rows.map((d) => {
                const top = d.predictions?.[0];
                return (
                  <motion.tr
                    key={d.id}
                    variants={staggerItem}
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
                  </motion.tr>
                );
              })}
            </motion.tbody>
          </table>
        </div>
      )}
    </AppShell>
  );
}
