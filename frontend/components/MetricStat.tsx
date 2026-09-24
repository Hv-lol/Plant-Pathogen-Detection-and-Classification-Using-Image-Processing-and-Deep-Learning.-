"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { AnimatedNumber } from "./AnimatedNumber";
import { staggerItem } from "@/lib/motion";

export function MetricStat({
  label,
  value,
  hint,
  className,
}: {
  label: string;
  value: string | number;
  hint?: string;
  className?: string;
}) {
  return (
    <motion.div variants={staggerItem} className={cn("py-2", className)}>
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-charcoal/45">
        {label}
      </p>
      <p className="mt-2 font-display text-3xl tracking-tight text-charcoal sm:text-4xl">
        {typeof value === "number" ? <AnimatedNumber value={value} /> : value}
      </p>
      {hint && <p className="mt-1 text-sm text-charcoal/50">{hint}</p>}
    </motion.div>
  );
}
