
"use client";

import { SidebarTrigger } from "@/components/ui/sidebar";
import { AppLogo } from "@/components/icons";
import Link from "next/link";

export function AppHeader() {
  return (
    <header className="sticky top-0 z-10 flex h-16 items-center gap-4 border-b bg-background px-4 md:px-6 shadow-sm">
      <div className="flex items-center gap-2 md:hidden">
        <SidebarTrigger />
      </div>
      <Link href="/qa" className="flex items-center gap-2">
        <AppLogo className="h-8 w-auto" />
        <span className="font-semibold text-lg hidden sm:inline-block">Intelligent Standards Assistant</span>
      </Link>
      {/* Add UserMenu or other header items here if needed */}
      {/* <div className="ml-auto"> User Profile </div> */}
    </header>
  );
}
