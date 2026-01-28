"use client";

import { useState } from "react";
import { LayoutDashboard, Settings, Bot, Menu, X, BrainCircuit, Zap } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const pathname = usePathname();

    const navItems = [
        { name: "Command Center", href: "/dashboard", icon: Bot },
        { name: "Agent History", href: "/dashboard/history", icon: LayoutDashboard },
        { name: "Knowledge", href: "/dashboard/knowledge", icon: BrainCircuit },
    ];

    const NavLink = ({ item, onClick }: { item: { name: string; href: string; icon: any }; onClick?: () => void }) => (
        <Link
            href={item.href}
            onClick={onClick}
            className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors",
                pathname === item.href
                    ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                    : "text-slate-400 hover:bg-slate-800 hover:text-slate-100"
            )}
        >
            <item.icon className="w-5 h-5" />
            {item.name}
        </Link>
    );

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 flex">
            {/* Sidebar (Desktop) */}
            <aside
                className={cn(
                    "fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 border-r border-slate-800 transition-transform duration-300 ease-in-out md:relative md:translate-x-0 hidden md:flex flex-col",
                    !sidebarOpen && "md:hidden"
                )}
            >
                <div className="h-16 flex items-center px-6 border-b border-slate-800 shrink-0">
                    <BrainCircuit className="w-6 h-6 text-blue-500 mr-2" />
                    <span className="font-bold text-lg tracking-tight">AI Ops Platform</span>
                </div>

                <nav className="p-4 space-y-1 flex-1 overflow-y-auto">
                    {navItems.map((item) => (
                        <NavLink key={item.href} item={item} />
                    ))}
                </nav>

                <div className="p-4 border-t border-slate-800 shrink-0">
                    <NavLink item={{ name: "Settings", href: "/dashboard/settings", icon: Settings }} />
                    {/* <div className="mt-4 p-4 bg-slate-950/50 rounded-lg border border-slate-800/50">
                        <p className="text-xs text-slate-500 font-mono">Build: Phase 2 (Dev)</p>
                        <p className="text-xs text-slate-500 font-mono">User: Admin</p>
                    </div> */}
                </div>
            </aside>

            {/* Mobile Sidebar (Overlay) */}
            <div className={`fixed inset-0 z-40 md:hidden ${sidebarOpen ? "block" : "hidden"}`} onClick={() => setSidebarOpen(false)}>
                <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm" />
            </div>
            <aside
                className={cn(
                    "fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 border-r border-slate-800 transition-transform duration-300 ease-in-out md:hidden flex flex-col",
                    sidebarOpen ? "translate-x-0" : "-translate-x-full"
                )}
            >
                <div className="h-16 flex items-center px-6 border-b border-slate-800 justify-between shrink-0">
                    <div className="flex items-center">
                        <BrainCircuit className="w-6 h-6 text-blue-500 mr-2" />
                        <span className="font-bold text-lg tracking-tight">AI Ops</span>
                    </div>
                    <button onClick={() => setSidebarOpen(false)} className="text-slate-400 hover:text-white">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <nav className="p-4 space-y-1 flex-1 overflow-y-auto">
                    {navItems.map((item) => (
                        <NavLink key={item.href} item={item} onClick={() => setSidebarOpen(false)} />
                    ))}
                </nav>

                <div className="p-4 border-t border-slate-800 shrink-0">
                    <NavLink item={{ name: "Settings", href: "/dashboard/settings", icon: Settings }} onClick={() => setSidebarOpen(false)} />
                </div>
            </aside>


            {/* Main Content */}
            <div className="flex-1 flex flex-col min-w-0">
                <header className="h-16 flex items-center justify-between px-6 border-b border-slate-800 bg-slate-950/50 backdrop-blur-sm sticky top-0 z-30">
                    <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 -ml-2 text-slate-400 hover:text-white rounded-md">
                        <Menu className="w-5 h-5" />
                    </button>

                    <div className="flex items-center gap-4">
                        <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                        <span className="text-sm text-slate-400">System Online</span>
                    </div>
                </header>

                <main className="flex-1 overflow-auto p-6 md:p-8">
                    {children}
                </main>
            </div>
        </div>
    );
}
