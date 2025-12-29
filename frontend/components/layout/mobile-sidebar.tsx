"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  FileText,
  SlidersHorizontal,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/leads", icon: FileText, label: "Leads" },
  { href: "/scoring", icon: SlidersHorizontal, label: "Scoring" },
  { href: "/settings", icon: Users, label: "Settings" },
];

export function MobileSidebar() {
  const pathname = usePathname();

  return (
    <nav className="grid gap-2 text-lg font-medium">
      <Link
        href="#"
        className="flex items-center gap-2 text-lg font-semibold mb-4"
      >
        <span className="">LeadManager</span>
      </Link>
      {navItems.map((item) => (
        <Link
          key={item.label}
          href={item.href}
          className={cn(
            "mx-[-0.65rem] flex items-center gap-4 rounded-xl px-3 py-2 text-muted-foreground hover:text-foreground",
            {
              "bg-muted text-foreground": pathname === item.href,
            }
          )}
        >
          <item.icon className="h-5 w-5" />
          {item.label}
        </Link>
      ))}
    </nav>
  );
}
