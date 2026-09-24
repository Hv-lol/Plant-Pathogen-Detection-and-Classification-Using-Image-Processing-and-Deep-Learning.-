"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { cn } from "@/lib/utils";

type Option = { value: string; label: string };

export function Select({
  label,
  value,
  onChange,
  options,
  placeholder = "Select…",
  disabled,
}: {
  label?: string;
  value: string;
  onChange: (value: string) => void;
  options: Option[];
  placeholder?: string;
  disabled?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const current = options.find((o) => o.value === value);

  useEffect(() => {
    function onClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  return (
    <div className="flex flex-col gap-1.5" ref={ref}>
      {label && <span className="text-sm font-medium text-charcoal/85">{label}</span>}
      <div className="relative">
        <button
          type="button"
          disabled={disabled}
          onClick={() => setOpen((v) => !v)}
          className={cn(
            "flex h-11 w-full items-center justify-between rounded-md border border-charcoal/12 bg-white px-3.5 text-left text-sm text-charcoal transition-colors",
            "focus:border-emerald focus:outline-none focus:ring-2 focus:ring-emerald/20",
            disabled && "pointer-events-none opacity-60"
          )}
        >
          <span className={current ? "text-charcoal" : "text-charcoal/40"}>
            {current?.label || placeholder}
          </span>
          <motion.svg
            width="14"
            height="14"
            viewBox="0 0 14 14"
            fill="none"
            animate={{ rotate: open ? 180 : 0 }}
            transition={{ duration: 0.2 }}
            className="text-charcoal/40"
          >
            <path d="M3 5l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </motion.svg>
        </button>

        <AnimatePresence>
          {open && (
            <motion.ul
              initial={{ opacity: 0, y: -6, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -6, scale: 0.98 }}
              transition={{ duration: 0.15, ease: [0.22, 1, 0.36, 1] }}
              className="absolute z-20 mt-1.5 max-h-64 w-full overflow-auto rounded-md border border-charcoal/10 bg-white py-1 shadow-soft"
            >
              {options.length === 0 ? (
                <li className="px-3.5 py-2 text-sm text-charcoal/40">No options</li>
              ) : (
                options.map((opt) => (
                  <li key={opt.value || "__empty"}>
                    <button
                      type="button"
                      onClick={() => {
                        onChange(opt.value);
                        setOpen(false);
                      }}
                      className={cn(
                        "flex w-full items-center px-3.5 py-2 text-left text-sm transition-colors hover:bg-cream",
                        opt.value === value ? "text-emerald font-medium" : "text-charcoal/80"
                      )}
                    >
                      {opt.label}
                    </button>
                  </li>
                ))
              )}
            </motion.ul>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
