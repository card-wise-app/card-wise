"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, CreditCard, Search, TrendingUp, Wallet, Settings, Home } from "lucide-react";

const NAV = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/my-cards", label: "My Cards", icon: CreditCard },
  { href: "/dashboard/finder", label: "Best Card Finder", icon: Search },
  { href: "/dashboard/rewards", label: "Rewards", icon: TrendingUp },
  { href: "/dashboard/spending", label: "Spending", icon: Wallet },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  return (
    <div className="min-h-screen lg:flex">
      <aside className="border-b border-line bg-white lg:sticky lg:top-0 lg:flex lg:h-screen lg:w-64 lg:shrink-0 lg:flex-col lg:border-b-0 lg:border-r">
        <Link href="/" className="flex items-center gap-2 px-5 py-5">
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-lime text-lg font-bold">C</span>
          <span className="text-xl font-bold">CardWise</span>
        </Link>
        <nav className="flex gap-1 overflow-x-auto px-3 pb-3 lg:flex-col lg:overflow-visible">
          {NAV.map((n) => {
            const active = path === n.href;
            return (
              <Link key={n.href} href={n.href} className={`flex shrink-0 items-center gap-3 rounded-full px-4 py-2.5 text-sm font-semibold lg:rounded-[16px] ${active ? "bg-ink text-white" : "text-ink hover:bg-paper"}`}>
                <n.icon className="h-4 w-4" /> {n.label}
              </Link>
            );
          })}
        </nav>
        <div className="mt-auto hidden p-4 lg:block">
          <div className="rounded-[20px] bg-lime p-4 text-sm">
            <p className="font-bold">Find the best card for my purchase.</p>
            <Link href="/dashboard/finder" className="mt-2 inline-block font-semibold underline">Open the finder →</Link>
          </div>
          <Link href="/" className="mt-3 flex items-center gap-2 px-2 text-sm font-medium text-muted"><Home className="h-4 w-4" /> Back to landing page</Link>
        </div>
      </aside>
      <main className="flex-1 px-5 py-8 lg:px-10">
        <div className="mx-auto max-w-6xl">{children}</div>
      </main>
    </div>
  );
}
