import Link from "next/link";
import type { ReactNode } from "react";
import { ArrowUpRight, ShieldCheck, AlertTriangle } from "lucide-react";

export function Button({ href, children, variant = "primary", className = "", onClick, type }: {
  href?: string; children: ReactNode; variant?: "primary" | "dark" | "outline" | "lime";
  className?: string; onClick?: () => void; type?: "button" | "submit";
}) {
  const base = "inline-flex items-center justify-center gap-2 rounded-full px-5 py-3 text-sm font-semibold transition hover:-translate-y-px active:translate-y-0";
  const styles = {
    primary: "bg-ink text-white hover:bg-black",
    dark: "bg-ink text-white",
    outline: "border border-ink/20 bg-white text-ink hover:border-ink",
    lime: "bg-lime text-ink hover:bg-limeDark",
  }[variant];
  if (href) return <Link href={href} className={`${base} ${styles} ${className}`}>{children}</Link>;
  return <button type={type || "button"} onClick={onClick} className={`${base} ${styles} ${className}`}>{children}</button>;
}

export function Pill({ children, tone = "lime" }: { children: ReactNode; tone?: "lime" | "dark" | "plain" }) {
  const s = tone === "lime" ? "bg-lime text-ink" : tone === "dark" ? "bg-ink text-white" : "bg-black/5 text-ink";
  return <span className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold ${s}`}>{children}</span>;
}

export function CardShell({ children, className = "", dark = false }: { children: ReactNode; className?: string; dark?: boolean }) {
  return (
    <div className={`rounded-[24px] border ${dark ? "border-ink bg-ink text-white" : "border-line bg-card text-ink"} shadow-soft ${className}`}>
      {children}
    </div>
  );
}

export function Field({ label, children, hint }: { label: string; children: ReactNode; hint?: string }) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-semibold">{label}</span>
      {children}
      {hint && <span className="mt-1 block text-xs text-muted">{hint}</span>}
    </label>
  );
}

export const inputCls = "w-full rounded-[16px] border border-line bg-white px-4 py-3 text-sm text-ink placeholder:text-muted/70";

export function Notice({ children }: { children: ReactNode }) {
  return (
    <div className="flex gap-3 rounded-[20px] border border-line bg-white p-4 text-sm leading-relaxed">
      <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-ink" />
      <div>{children}</div>
    </div>
  );
}

export function VerifiedNote() {
  return (
    <p className="flex items-start gap-2 text-sm text-muted">
      <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-ink" />
      <span>All catalogue rules shown here are <strong className="text-ink">pending review</strong>, not issuer-verified. Do not rely on them for real spending until they are verified against official issuer terms.</span>
    </p>
  );
}

export function ArrowLink({ href, children }: { href: string; children: ReactNode }) {
  return (
    <Link href={href} className="inline-flex items-center gap-1 text-sm font-semibold underline decoration-lime decoration-4 underline-offset-4 hover:gap-2 transition-all">
      {children} <ArrowUpRight className="h-4 w-4" />
    </Link>
  );
}
