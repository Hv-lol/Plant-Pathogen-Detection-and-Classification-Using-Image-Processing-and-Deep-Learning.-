import clsx, { type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export const JOB_STAGES = [
  "queued",
  "checking_image_quality",
  "detecting_plant_leaf",
  "analyzing_symptoms",
  "running_disease_classifier",
  "generating_explanation",
  "estimating_severity",
  "preparing_diagnosis",
  "completed",
] as const;

export type JobStage =
  | (typeof JOB_STAGES)[number]
  | "failed"
  | "failed_quality";

export const STAGE_LABELS: Record<string, string> = {
  queued: "Queued",
  checking_image_quality: "Checking image quality",
  detecting_plant_leaf: "Detecting plant leaf",
  analyzing_symptoms: "Analyzing symptoms",
  running_disease_classifier: "Running disease classifier",
  generating_explanation: "Generating explanation",
  estimating_severity: "Estimating severity",
  preparing_diagnosis: "Preparing diagnosis",
  completed: "Completed",
  failed: "Failed",
  failed_quality: "Failed quality check",
};

export function formatConfidence(value?: number | null): string {
  if (value == null || Number.isNaN(value)) return "—";
  const pct = value <= 1 ? value * 100 : value;
  return `${pct.toFixed(1)}%`;
}

export function formatDate(value?: string | null): string {
  if (!value) return "—";
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

export function stageIndex(stage?: string | null): number {
  if (!stage) return 0;
  if (stage === "failed" || stage === "failed_quality") return -1;
  const idx = JOB_STAGES.indexOf(stage as (typeof JOB_STAGES)[number]);
  return idx >= 0 ? idx : 0;
}
