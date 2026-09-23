import type { ReactNode } from "react";
import { Button } from "./Button";

export function EmptyState({
  title,
  description,
  actionLabel,
  onAction,
  children,
}: {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  children?: ReactNode;
}) {
  return (
    <div className="fade-in flex flex-col items-start gap-4 py-12">
      <div>
        <h3 className="font-display text-2xl text-charcoal">{title}</h3>
        <p className="mt-2 max-w-md text-sm leading-relaxed text-charcoal/60">
          {description}
        </p>
      </div>
      {actionLabel && onAction && (
        <Button onClick={onAction}>{actionLabel}</Button>
      )}
      {children}
    </div>
  );
}
