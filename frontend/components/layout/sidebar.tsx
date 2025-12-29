"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  FileText,
  SlidersHorizontal,
} from "lucide-react";
import { Button } from "@/components/ui/button";

import { cn } from "@/lib/utils";

const navItems = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/leads", icon: FileText, label: "Leads" },
  { href: "/scoring", icon: SlidersHorizontal, label: "Scoring" },
  { href: "/settings", icon: Users, label: "Settings" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="hidden border-r bg-sidebar md:block border-sidebar-border text-sidebar-foreground">
      <div className="flex h-full max-h-screen flex-col gap-2">
        <div className="flex h-14 items-center border-b border-sidebar-border px-4 lg:h-[60px] lg:px-6 bg-sidebar">
          <Link href="/" className="flex items-center gap-2 font-semibold">
            {/* Logo Icon */}
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <LayoutDashboard className="h-5 w-5" />
            </div>
            <span className="text-lg font-bold tracking-tight">
              LeadManager
            </span>
          </Link>
        </div>
        <div className="flex-1 overflow-auto py-2">
          <nav className="grid items-start px-2 text-sm font-medium lg:px-4">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.label}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-md px-3 py-2.5 transition-all",
                    isActive
                      ? "bg-sidebar-accent text-sidebar-accent-foreground font-semibold shadow-sm"
                      : "text-muted-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
                  )}
                >
                  <item.icon
                    className={cn("h-4 w-4", isActive ? "text-primary" : "")}
                  />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer area could go here */}
        <div className="mt-auto p-4 border-t border-sidebar-border">
          <div className="rounded-lg bg-sidebar-accent p-4">
            <h4 className="mb-1 text-sm font-semibold text-sidebar-accent-foreground">
              Need Help?
            </h4>
            <p className="text-xs text-muted-foreground mb-3">
              Check our documentation for AI scoring tips.
            </p>
            <Button size="sm" className="w-full" variant="secondary">
              Documentation
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
