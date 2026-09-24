"use client";

import { useEffect, useRef, useState } from "react";
import { animate } from "framer-motion";

/** Counts up from 0 to `value` whenever `value` changes. Non-numeric or
 * already-formatted strings (e.g. "94.7%") pass through unanimated. */
export function AnimatedNumber({
  value,
  format,
  duration = 0.9,
}: {
  value: number;
  format?: (n: number) => string;
  duration?: number;
}) {
  const [display, setDisplay] = useState(0);
  const prev = useRef(0);

  useEffect(() => {
    const controls = animate(prev.current, value, {
      duration,
      ease: [0.22, 1, 0.36, 1],
      onUpdate: (v) => setDisplay(v),
    });
    prev.current = value;
    return () => controls.stop();
  }, [value, duration]);

  const rounded = Math.round(display);
  return <>{format ? format(rounded) : rounded.toLocaleString()}</>;
}
