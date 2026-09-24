"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { AppShell } from "@/components/AppShell";
import { EmptyState } from "@/components/EmptyState";
import { SkeletonCard } from "@/components/Skeleton";
import { useToast } from "@/components/Toast";
import { api, ApiError, type Crop } from "@/lib/api";
import { fadeUp, staggerContainer, staggerItem, easeSmooth } from "@/lib/motion";

const exampleCrops = [
  "Tomato", "Potato", "Pepper", "Maize", "Wheat", "Rice",
  "Cotton", "Soybean", "Grape", "Citrus", "Apple", "Cucumber",
];

export default function CropsPage() {
  const toast = useToast();
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
          const message = err instanceof ApiError ? err.message : "Failed to load crops.";
          setError(message);
          toast.push({ title: "Couldn't load crops", description: message, tone: "error" });
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
      <motion.div initial="hidden" animate="show" variants={fadeUp} className="max-w-2xl">
        <p className="eyebrow">Knowledge</p>
        <h1 className="mt-2 font-display text-4xl text-charcoal">Crops</h1>
        <p className="mt-3 text-sm text-charcoal/60">
          This release classifies pathogen categories across general field-crop
          imagery (not crop-specific disease names).
        </p>
      </motion.div>

      {!loading && error && <p className="mt-6 text-sm text-danger">{error}</p>}

      {loading ? (
        <div className="mt-12 grid gap-x-10 gap-y-8 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : crops.length === 0 ? (
        <EmptyState
          title="No crops listed"
          description="Crop entries will appear here once the knowledge base is seeded."
        />
      ) : (
        <motion.ul
          className="mt-12 grid gap-x-10 gap-y-8 sm:grid-cols-2 lg:grid-cols-3"
          initial="hidden"
          animate="show"
          variants={staggerContainer}
        >
          {crops.map((c) => (
            <motion.li
              key={c.id}
              variants={staggerItem}
              whileHover={{ y: -3 }}
              transition={{ duration: 0.2, ease: easeSmooth }}
              className="border-t border-charcoal/10 pt-5"
            >
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
            </motion.li>
          ))}
        </motion.ul>
      )}

      <motion.div
        className="mt-16 border-t border-charcoal/10 pt-8"
        initial="hidden"
        whileInView="show"
        viewport={{ once: true, margin: "-80px" }}
        variants={staggerContainer}
      >
        <motion.p variants={staggerItem} className="eyebrow">
          Field coverage
        </motion.p>
        <motion.h2 variants={staggerItem} className="mt-2 font-display text-2xl text-charcoal">
          Crops commonly represented in the training imagery
        </motion.h2>
        <motion.p variants={staggerItem} className="mt-3 max-w-2xl text-sm leading-relaxed text-charcoal/60">
          The model isn&apos;t tuned per crop, so it doesn&apos;t give crop-specific
          disease names—but it has seen foliage from a broad mix of field and
          horticultural crops, including these:
        </motion.p>
        <motion.div variants={staggerItem} className="mt-6 flex flex-wrap gap-2.5">
          {exampleCrops.map((crop) => (
            <span
              key={crop}
              className="rounded-full border border-charcoal/10 bg-white/60 px-4 py-1.5 text-sm text-charcoal/70"
            >
              {crop}
            </span>
          ))}
        </motion.div>
      </motion.div>
    </AppShell>
  );
}
