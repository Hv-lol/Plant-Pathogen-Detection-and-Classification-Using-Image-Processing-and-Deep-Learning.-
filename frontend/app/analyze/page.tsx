"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { Badge } from "@/components/Badge";
import { Button } from "@/components/Button";
import { FileUploader } from "@/components/FileUploader";
import { api, ApiError, type Crop, type ImageUpload, type JobStatus } from "@/lib/api";
import { JOB_STAGES, STAGE_LABELS, stageIndex, cn } from "@/lib/utils";

type Phase = "idle" | "uploading" | "ready" | "running" | "done" | "error";

export default function AnalyzePage() {
  const router = useRouter();
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
      setError(err instanceof ApiError ? err.message : "Upload failed.");
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
      setError(err instanceof ApiError ? err.message : "Diagnosis start failed.");
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
          router.push(`/diagnosis/${status.diagnosis_id}`);
          return;
        }
        if (
          stage === "failed" ||
          stage === "failed_quality" ||
          status.status?.toUpperCase() === "FAILED"
        ) {
          setPhase("error");
          setError(
            status.error_message ||
              STAGE_LABELS[stage] ||
              "Diagnosis failed."
          );
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
  }, [phase, job?.job_id, router]);

  const currentStage = job?.stage || "queued";
  const activeIdx = stageIndex(currentStage);

  const qualityNotes = useMemo(() => {
    return upload?.quality_messages || [];
  }, [upload]);

  return (
    <AppShell>
      <div className="max-w-3xl">
        <p className="eyebrow">Analyze</p>
        <h1 className="mt-2 font-display text-4xl text-charcoal">
          Upload leaf imagery
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-charcoal/60">
          We classify visual symptom patterns and return confidence-scored
          predictions. This is not laboratory pathogen confirmation.
        </p>
      </div>

      <div className="mt-10 grid gap-10 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-5">
          <FileUploader onFile={onFile} previewUrl={preview} disabled={phase === "running"} />

          {file && phase === "idle" && (
            <Button onClick={handleUpload}>Upload image</Button>
          )}
          {phase === "uploading" && (
            <Button loading disabled>
              Uploading…
            </Button>
          )}

          {upload && (
            <div className="space-y-4 border-t border-charcoal/10 pt-6">
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

              <label className="flex flex-col gap-1.5">
                <span className="text-sm font-medium text-charcoal/85">
                  Crop (optional)
                </span>
                <select
                  className="h-11 rounded-md border border-charcoal/12 bg-white px-3 text-sm focus:border-emerald focus:outline-none focus:ring-2 focus:ring-emerald/20"
                  value={cropId}
                  onChange={(e) => setCropId(e.target.value)}
                  disabled={phase === "running"}
                >
                  <option value="">Auto / unspecified</option>
                  {crops.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </label>

              {(phase === "ready" || phase === "error") && (
                <Button onClick={handleDiagnose}>Run diagnosis</Button>
              )}
            </div>
          )}

          {error && <p className="text-sm text-danger">{error}</p>}
        </div>

        <aside className="lg:pl-4">
          <h2 className="font-display text-xl text-charcoal">Pipeline stages</h2>
          <ol className="mt-6 space-y-4">
            {JOB_STAGES.filter((s) => s !== "completed").map((stage, idx) => {
              const done = activeIdx > idx || currentStage === "completed";
              const active = activeIdx === idx && phase === "running";
              return (
                <li key={stage} className="flex items-start gap-3">
                  <span
                    className={cn(
                      "stage-dot mt-1.5",
                      done && "stage-dot-done",
                      active && "stage-dot-active"
                    )}
                  />
                  <div>
                    <p
                      className={cn(
                        "text-sm font-medium",
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

          {phase === "running" && (
            <p className="mt-6 text-sm text-charcoal/55 fade-in">
              Current: {STAGE_LABELS[currentStage] || currentStage}
            </p>
          )}
        </aside>
      </div>
    </AppShell>
  );
}
