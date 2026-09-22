import { cn } from "@/lib/utils";

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
    <div className={cn("slide-up py-2", className)}>
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-charcoal/45">
        {label}
      </p>
      <p className="mt-2 font-display text-3xl tracking-tight text-charcoal sm:text-4xl">
        {value}
      </p>
      {hint && <p className="mt-1 text-sm text-charcoal/50">{hint}</p>}
    </div>
  );
}
