"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/Button";
import { Input } from "@/components/Input";
import { useToast } from "@/components/Toast";
import { useAuth } from "@/lib/auth";
import { ApiError } from "@/lib/api";

export default function RegisterPage() {
  const { register } = useAuth();
  const toast = useToast();
  const router = useRouter();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(email, password, fullName);
      router.replace("/dashboard");
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Registration failed.";
      setError(message);
      toast.push({ title: "Registration failed", description: message, tone: "error" });
    } finally {
      setLoading(false);
    }
  }

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
              Start diagnosing with confidence.
            </h1>
            <p className="mt-4 max-w-sm text-cream/70">
              Create an account to upload imagery, track analyses, and explore
              the disease knowledge base.
            </p>
          </div>
        </div>
      </aside>

      <main className="flex items-center justify-center bg-mist px-6 py-16">
        <form onSubmit={onSubmit} className="w-full max-w-md space-y-5 slide-up">
          <div>
            <p className="eyebrow">Register</p>
            <h2 className="mt-2 font-display text-3xl text-charcoal">
              Create your account
            </h2>
          </div>
          <Input
            label="Full name"
            name="full_name"
            required
            minLength={2}
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />
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
            autoComplete="new-password"
            required
            minLength={8}
            hint="At least 8 characters"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <p className="text-sm text-danger">{error}</p>}
          <Button type="submit" className="w-full" loading={loading}>
            Create account
          </Button>
          <p className="text-sm text-charcoal/55">
            Already registered?{" "}
            <Link href="/login" className="text-emerald link-underline">
              Sign in
            </Link>
          </p>
        </form>
      </main>
    </div>
  );
}
