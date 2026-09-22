"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";
import { Button } from "./Button";

const publicLinks = [
  { href: "/diseases", label: "Categories" },
  { href: "/crops", label: "Crops" },
  { href: "/help", label: "Help" },
];

const appLinks = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/analyze", label: "Analyze" },
  { href: "/history", label: "History" },
  { href: "/diseases", label: "Categories" },
  { href: "/help", label: "Help" },
];

export function Navbar({ variant = "marketing" }: { variant?: "marketing" | "app" }) {
  const { user, logout, loading } = useAuth();
  const pathname = usePathname();
  const links = variant === "app" ? appLinks : publicLinks;

  return (
    <header
      className={cn(
        "sticky top-0 z-40 border-b backdrop-blur-md",
        variant === "marketing"
          ? "border-white/10 bg-forest/80 text-cream"
          : "border-charcoal/8 bg-mist/90 text-charcoal"
      )}
    >
      <div className="container-narrow section-pad flex h-16 items-center justify-between gap-4">
        <div className="flex items-center gap-8">
          <Link
            href={user ? "/dashboard" : "/"}
            className="font-display text-xl tracking-tight transition-opacity hover:opacity-80"
          >
            PlantGuard<span className="text-leaf"> AI</span>
          </Link>
          <nav className="hidden items-center gap-6 md:flex">
            {links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "text-sm transition-colors duration-200",
                  pathname === link.href || pathname.startsWith(`${link.href}/`)
                    ? variant === "marketing"
                      ? "text-white"
                      : "text-emerald"
                    : variant === "marketing"
                      ? "text-cream/70 hover:text-white"
                      : "text-charcoal/60 hover:text-charcoal"
                )}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>

        <div className="flex items-center gap-2">
          {loading ? (
            <span className="text-xs opacity-50">…</span>
          ) : user ? (
            <>
              <span className="hidden text-sm opacity-70 sm:inline">
                {user.full_name.split(" ")[0]}
              </span>
              {variant === "marketing" && (
                <Link href="/dashboard">
                  <Button size="sm" variant="outline" className="border-cream/30 text-cream hover:border-leaf hover:text-white">
                    Dashboard
                  </Button>
                </Link>
              )}
              <Button
                size="sm"
                variant={variant === "marketing" ? "ghost" : "outline"}
                className={variant === "marketing" ? "text-cream hover:bg-white/10" : ""}
                onClick={logout}
              >
                Sign out
              </Button>
            </>
          ) : (
            <>
              <Link href="/login">
                <Button
                  size="sm"
                  variant="ghost"
                  className={variant === "marketing" ? "text-cream hover:bg-white/10" : ""}
                >
                  Sign in
                </Button>
              </Link>
              <Link href="/register">
                <Button size="sm" variant={variant === "marketing" ? "primary" : "primary"}>
                  Get started
                </Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
