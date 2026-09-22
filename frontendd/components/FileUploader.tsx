"use client";

import { useCallback, useRef, useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "./Button";

type Props = {
  onFile: (file: File) => void;
  accept?: string;
  disabled?: boolean;
  previewUrl?: string | null;
};

export function FileUploader({
  onFile,
  accept = "image/jpeg,image/png,image/webp",
  disabled,
  previewUrl,
}: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const handleFiles = useCallback(
    (files: FileList | null) => {
      const file = files?.[0];
      if (file) onFile(file);
    },
    [onFile]
  );

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-lg border-2 border-dashed transition-all duration-300 ease-smooth",
        dragging
          ? "border-emerald bg-emerald/5"
          : "border-charcoal/15 bg-white hover:border-leaf/60",
        disabled && "pointer-events-none opacity-60"
      )}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        handleFiles(e.dataTransfer.files);
      }}
    >
      {previewUrl ? (
        <div className="relative aspect-[4/3] w-full">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={previewUrl}
            alt="Upload preview"
            className="h-full w-full object-cover"
          />
          <div className="absolute inset-x-0 bottom-0 flex items-center justify-between gap-3 bg-gradient-to-t from-forest/80 to-transparent p-4">
            <p className="text-sm text-cream">Preview ready</p>
            <Button
              size="sm"
              variant="outline"
              className="border-cream/40 text-cream hover:border-white hover:text-white"
              onClick={() => inputRef.current?.click()}
            >
              Replace
            </Button>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center gap-3 px-6 py-16 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-cream text-emerald">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden>
              <path
                d="M12 16V4M12 4l-4 4M12 4l4 4M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2"
                stroke="currentColor"
                strokeWidth="1.75"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <div>
            <p className="font-medium text-charcoal">Drop a leaf image here</p>
            <p className="mt-1 text-sm text-charcoal/50">
              JPEG, PNG, or WebP · clear, well-lit foliage works best
            </p>
          </div>
          <Button
            type="button"
            variant="outline"
            onClick={() => inputRef.current?.click()}
          >
            Browse files
          </Button>
        </div>
      )}
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
    </div>
  );
}
