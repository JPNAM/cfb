"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "../lib/utils";

const links = [
  { href: "/", label: "Home" },
  { href: "/builder", label: "Lineup Builder" },
  { href: "/coaches", label: "Coaches" }
];

export function Header() {
  const pathname = usePathname();
  return (
    <header className="mb-10 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <div>
        <h1 className="text-3xl font-semibold">NFL Cohesion</h1>
        <p className="text-sm text-slate-500">Build optimized lineups and quantify chemistry with transparent system states.</p>
      </div>
      <nav className="flex gap-2 rounded-full bg-white/70 p-1 shadow-sm backdrop-blur">
        {links.map(link => (
          <Link
            key={link.href}
            href={link.href}
            className={cn(
              "rounded-full px-4 py-2 text-sm font-medium transition",
              pathname === link.href ? "bg-primary text-white" : "text-slate-600 hover:bg-slate-100"
            )}
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
