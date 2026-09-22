"use client";

import { cn } from "@/lib/utils";
import type { InputHTMLAttributes } from "react";

type Props = InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  hint?: string;
  error?: string;
};

export function Input({ label, hint, error, className, id, ...props }: Props) {
  const inputId = id || props.name;
  return (
    <label className="flex w-full flex-col gap-1.5">
      {label && (
        <span className="text-sm font-medium text-charcoal/85">{label}</span>
      )}
      <input
        id={inputId}
        className={cn(
          "h-11 w-full rounded-md border bg-white px-3.5 text-sm text-charcoal",
          "placeholder:text-charcoal/40 transition-colors duration-200",
          "focus:border-emerald focus:outline-none focus:ring-2 focus:ring-emerald/20",
          error ? "border-danger/50" : "border-charcoal/12",
          className
        )}
        {...props}
      />
      {error ? (
        <span className="text-xs text-danger">{error}</span>
      ) : hint ? (
        <span className="text-xs text-charcoal/50">{hint}</span>
      ) : null}
    </label>
  );
}
