"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { AppShell } from "@/components/AppShell";
import { Badge } from "@/components/Badge";
import { Button } from "@/components/Button";
import { FileUploader } from "@/components/FileUploader";
import { Select } from "@/components/Select";
import { useToast } from "@/components/Toast";
import { api, ApiError, type Crop, type ImageUpload, type JobStatus } from "@/lib/api";
import { JOB_STAGES, STAGE_LABELS, stageIndex, cn } from "@/lib/utils";
import { fadeUp } from "@/lib/motion";

type Phase = "idle" | "uploading" | "ready" | "running" | "done" | "error";

export default function AnalyzePage() {
  const router = useRouter();
  const toast = useToast();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [upload, setUpload] = useState<ImageUpload | null>(null);
  const [crops, setCrops] = useState<Crop[]>([]);
  const [cropId, setCropId] = useState("");
  const [phase, setPhase] = useState<Phase>("idle");
  const [job, setJob] = useState<JobStatus | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    void api.listCrops().then(setCrops).catch(() => undefined);
  }, []);

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  const onFile = useCallback((f: File) => {
    setFile(f);
    setUpload(null);
    setJob(null);
    setError("");
    setPhase("idle");
    setPreview((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return URL.createObjectURL(f);
    });
  }, []);

  async function handleUpload() {
    if (!file) return;
    setError("");
    setPhase("uploading");
    try {
      const result = await api.uploadImage(file);
      setUpload(result);
      setPhase("ready");
    } catch (err) {
      setPhase("error");
      const message = err instanceof ApiError ? err.message : "Upload failed.";
      setError(message);
      toast.push({ title: "Upload failed", description: message, tone: "error" });
    }
  }

  async function handleDiagnose() {
    if (!upload) return;
    setError("");
    setPhase("running");
    try {
      const created = await api.createDiagnosis({
        image_id: upload.id,
        crop_id: cropId || undefined,
      });
      setJob(created);
    } catch (err) {
      setPhase("error");
      const message = err instanceof ApiError ? err.message : "Diagnosis start failed.";
      setError(message);
      toast.push({ title: "Couldn't start diagnosis", description: message, tone: "error" });
    }
  }

  useEffect(() => {
    if (phase !== "running" || !job?.job_id) return;

    let cancelled = false;
    const tick = async () => {
      try {
        const status = await api.getJob(job.job_id);
        if (cancelled) return;
        setJob(status);
        const stage = status.stage || "";
        if (
          stage === "completed" ||
          status.status?.toUpperCase() === "COMPLETED"
        ) {
          setPhase("done");
          toast.push({ title: "Diagnosis ready", tone: "success" });
          router.push(`/diagnosis/${status.diagnosis_id}`);
          return;
        }
        if (
          stage === "failed" ||
          stage === "failed_quality" ||
          status.status?.toUpperCase() === "FAILED"
        ) {
          setPhase("error");
          const message =
            status.error_message || STAGE_LABELS[stage] || "Diagnosis failed.";
          setError(message);
          toast.push({ title: "Diagnosis failed", description: message, tone: "error" });
        }
      } catch (err) {
        if (!cancelled) {
          setPhase("error");
          setError(err instanceof ApiError ? err.message : "Polling failed.");
        }
      }
    };

    void tick();
    const id = window.setInterval(tick, 1500);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase, job?.job_id, router]);

  const currentStage = job?.stage || "queued";
  const activeIdx = stageIndex(currentStage);
  const stages = JOB_STAGES.filter((s) => s !== "completed");
  const progressPct =
    phase === "running" || phase === "done"
      ? Math.min(100, (Math.max(activeIdx, 0) / (stages.length - 1)) * 100)
      : 0;

  const qualityNotes = useMemo(() => {
    return upload?.quality_messages || [];
  }, [upload]);

  const cropOptions = [
    { value: "", label: "Auto / unspecified" },
    ...crops.map((c) => ({ value: c.id, label: c.name })),
  ];

  return (
    <AppShell>
      <motion.div initial="hidden" animate="show" variants={fadeUp} className="max-w-3xl">
        <p className="eyebrow">Analyze</p>
        <h1 className="mt-2 font-display text-4xl text-charcoal">
          Upload leaf imagery
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-charcoal/60">
          We classify visual symptom patterns and return confidence-scored
          predictions. This is not laboratory pathogen confirmation.
        </p>
      </motion.div>

      <div className="mt-10 grid gap-10 lg:grid-cols-[1.2fr_0.8fr]">
        <motion.div
          className="space-y-5"
          initial="hidden"
          animate="show"
          variants={fadeUp}
          transition={{ delay: 0.1 }}
        >
          <FileUploader onFile={onFile} previewUrl={preview} disabled={phase === "running"} />

          <AnimatePresence mode="wait">
            {file && phase === "idle" && (
              <motion.div key="upload-btn" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <Button onClick={handleUpload}>Upload image</Button>
              </motion.div>
            )}
            {phase === "uploading" && (
              <motion.div key="uploading-btn" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <Button loading disabled>
                  Uploading…
                </Button>
              </motion.div>
            )}
          </AnimatePresence>

          <AnimatePresence>
            {upload && (
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
                className="space-y-4 border-t border-charcoal/10 pt-6"
              >
                <div className="flex flex-wrap items-center gap-3">
                  <Badge
                    tone={
                      upload.quality_status === "pass" ||
                      upload.quality_status === "ok" ||
                      !upload.quality_status
                        ? "success"
                        : "warning"
                    }
                  >
                    Quality: {upload.quality_status || "assessed"}
                  </Badge>
                  {upload.quality_score != null && (
                    <span className="text-sm text-charcoal/55">
                      Score {(upload.quality_score * (upload.quality_score <= 1 ? 100 : 1)).toFixed(0)}
                      {upload.quality_score <= 1 ? "%" : ""}
                    </span>
                  )}
                  {upload.width && upload.height && (
                    <span className="text-sm text-charcoal/45">
                      {upload.width}×{upload.height}
                    </span>
                  )}
                </div>

                {qualityNotes.length > 0 && (
                  <ul className="space-y-1 text-sm text-charcoal/65">
                    {qualityNotes.map((note) => (
                      <li key={note}>• {note}</li>
                    ))}
                  </ul>
                )}

                <Select
                  label="Crop (optional)"
                  value={cropId}
                  onChange={setCropId}
                  options={cropOptions}
                  disabled={phase === "running"}
                />

                {(phase === "ready" || phase === "error") && (
                  <Button onClick={handleDiagnose}>Run diagnosis</Button>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {error && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-sm text-danger"
            >
              {error}
            </motion.p>
          )}
        </motion.div>

        <motion.aside
          className="lg:pl-4"
          initial="hidden"
          animate="show"
          variants={fadeUp}
          transition={{ delay: 0.2 }}
        >
          <h2 className="font-display text-xl text-charcoal">Pipeline stages</h2>

          <div className="relative mt-6">
            <div className="absolute left-[3px] top-1.5 h-[calc(100%-1.5rem)] w-px bg-charcoal/10" />
            <motion.div
              className="absolute left-[3px] top-1.5 w-px bg-emerald"
              initial={{ height: 0 }}
              animate={{ height: `${progressPct}%` }}
              transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
            />
            <ol className="space-y-4">
              {stages.map((stage, idx) => {
                const done = activeIdx > idx || currentStage === "completed";
                const active = activeIdx === idx && phase === "running";
                return (
                  <li key={stage} className="relative flex items-start gap-3">
                    <span className="relative z-10 mt-1.5">
                      <motion.span
                        className={cn(
                          "block h-2 w-2 rounded-full",
                          done ? "bg-leaf" : active ? "bg-emerald" : "bg-sage"
                        )}
                        animate={
                          active
                            ? { boxShadow: ["0 0 0 0 rgba(31,111,84,0.25)", "0 0 0 6px rgba(31,111,84,0)"] }
                            : { boxShadow: "0 0 0 0 rgba(31,111,84,0)" }
                        }
                        transition={active ? { duration: 1.4, repeat: Infinity, ease: "easeOut" } : undefined}
                      />
                    </span>
                    <div>
                      <p
                        className={cn(
                          "text-sm font-medium transition-colors",
                          active ? "text-emerald" : done ? "text-charcoal" : "text-charcoal/40"
                        )}
                      >
                        {STAGE_LABELS[stage]}
                      </p>
                    </div>
                  </li>
                );
              })}
            </ol>
          </div>

          {phase === "running" && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-6 text-sm text-charcoal/55"
            >
              Current: {STAGE_LABELS[currentStage] || currentStage}
            </motion.p>
          )}
        </motion.aside>
      </div>
    </AppShell>
  );
}
