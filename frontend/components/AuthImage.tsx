"use client";

import { useEffect, useState } from "react";
import { fetchAuthorizedBlobUrl } from "@/lib/api";
import { cn } from "@/lib/utils";

export function AuthImage({
  src,
  alt,
  className,
}: {
  src?: string | null;
  alt: string;
  className?: string;
}) {
  const [url, setUrl] = useState<string | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let objectUrl: string | null = null;
    let cancelled = false;

    async function load() {
      if (!src) {
        setUrl(null);
        return;
      }
      try {
        objectUrl = await fetchAuthorizedBlobUrl(src);
        if (!cancelled) {
          setUrl(objectUrl);
          setError(false);
        } else {
          URL.revokeObjectURL(objectUrl);
        }
      } catch {
        if (!cancelled) setError(true);
      }
    }

    void load();

    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [src]);

  if (!src) {
    return (
      <div
        className={cn(
          "flex items-center justify-center bg-cream text-sm text-charcoal/40",
          className
        )}
      >
        No image
      </div>
    );
  }

  if (error) {
    return (
      <div
        className={cn(
          "flex items-center justify-center bg-cream text-sm text-danger/80",
          className
        )}
      >
        Unable to load image
      </div>
    );
  }

  if (!url) {
    return (
      <div
        className={cn(
          "flex animate-pulse items-center justify-center bg-cream text-sm text-charcoal/40",
          className
        )}
      >
        Loading…
      </div>
    );
  }

  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img src={url} alt={alt} className={cn("object-cover", className)} />
  );
}
