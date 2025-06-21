
"use client"; // Top-level layout interacting with sidebar state needs to be client component

import * as React from "react";
import {
  SidebarProvider,
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarInset,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { AppLogo } from "@/components/icons";
import { SidebarNavItems } from "@/components/layout/sidebar-nav-items";
import { AppHeader } from "@/components/layout/app-header";
import { Button } from "@/components/ui/button";
import { PanelLeftClose, PanelLeftOpen } from "lucide-react"; // Using different icons for open/close state

export default function IsaAppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(true);

  // Default open on desktop, closed on mobile (handled by Sidebar component's responsiveness)
  // This explicit state is for the toggle button icon
  React.useEffect(() => {
    const mediaQuery = window.matchMedia('(max-width: 768px)');
    setIsSidebarOpen(!mediaQuery.matches); 
    
    const handleChange = (e: MediaQueryListEvent) => {
      setIsSidebarOpen(!e.matches);
    };
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);


  return (
    <SidebarProvider defaultOpen={true} open={isSidebarOpen} onOpenChange={setIsSidebarOpen}>
      <Sidebar variant="sidebar" collapsible="icon" className="border-r">
        <SidebarHeader className="p-4 flex items-center justify-between">
          <AppLogo className="h-10 w-auto" />
          {/* Sidebar trigger for desktop icon-only collapse, hidden when sidebar is text-visible */}
          <Button 
            variant="ghost" 
            size="icon" 
            className="hidden group-data-[collapsible=icon]:hidden group-data-[state=expanded]:flex" // Show when expanded
            onClick={() => setIsSidebarOpen(false)}
            aria-label="Collapse sidebar"
          >
            <PanelLeftClose />
          </Button>
           <Button 
            variant="ghost" 
            size="icon" 
            className="hidden group-data-[collapsible=icon]:flex group-data-[state=collapsed]:flex" // Show when collapsed
            onClick={() => setIsSidebarOpen(true)}
            aria-label="Expand sidebar"
          >
            <PanelLeftOpen />
          </Button>
        </SidebarHeader>
        <SidebarContent>
          <SidebarNavItems />
        </SidebarContent>
        <SidebarFooter className="p-2">
          {/* Footer content if any */}
        </SidebarFooter>
      </Sidebar>
      <SidebarInset>
        <AppHeader />
        <main className="flex-1 p-6 overflow-auto">
          {children}
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}
