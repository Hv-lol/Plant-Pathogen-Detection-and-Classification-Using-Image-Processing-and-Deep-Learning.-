"use client";

import Link from "next/link";
import { Suspense, useState, type FormEvent } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/Button";
import { Input } from "@/components/Input";
import { useAuth } from "@/lib/auth";
import { ApiError } from "@/lib/api";

function LoginForm() {
  const { login } = useAuth();
  const router = useRouter();
  const search = useSearchParams();
  const next = search.get("next") || "/dashboard";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      router.replace(next);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Sign in failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="w-full max-w-md space-y-5 slide-up">
      <div>
        <p className="eyebrow">Sign in</p>
        <h2 className="mt-2 font-display text-3xl text-charcoal">
          Enter your account
        </h2>
      </div>
      <Input
        label="Email"
        type="email"
        name="email"
        autoComplete="email"
        required
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <Input
        label="Password"
        type="password"
        name="password"
        autoComplete="current-password"
        required
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {error && <p className="text-sm text-danger">{error}</p>}
      <Button type="submit" className="w-full" loading={loading}>
        Sign in
      </Button>
      <p className="text-sm text-charcoal/55">
        New here?{" "}
        <Link href="/register" className="text-emerald link-underline">
          Create an account
        </Link>
      </p>
    </form>
  );
}

export default function LoginPage() {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <aside className="relative hidden bg-leaf-mesh lg:block">
        <div className="absolute inset-0 bg-forest-glow" />
        <div className="relative flex h-full flex-col justify-between p-12 text-cream">
          <Link href="/" className="font-display text-2xl">
            PlantGuard AI
          </Link>
          <div>
            <h1 className="font-display text-4xl leading-tight">
              Welcome back to the field.
            </h1>
            <p className="mt-4 max-w-sm text-cream/70">
              Access your diagnosis history, analytics, and new leaf analyses.
            </p>
          </div>
        </div>
      </aside>

      <main className="flex items-center justify-center bg-mist px-6 py-16">
        <Suspense fallback={<p className="text-sm text-charcoal/45">Loading…</p>}>
          <LoginForm />
        </Suspense>
      </main>
    </div>
  );
}
