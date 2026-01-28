"use client";

import { useState } from "react";
import { LayoutDashboard, Settings, Bot, Menu, X, BrainCircuit } from "lucide-react";
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
        { name: "Settings", href: "/dashboard/settings", icon: Settings },
    ];

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 flex">
            {/* Sidebar */}
            <aside
                className={cn(
                    "fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 border-r border-slate-800 transition-transform duration-300 ease-in-out md:relative md:translate-x-0",
                    !sidebarOpen && "-translate-x-full md:w-0 md:overflow-hidden md:border-none"
                )}
            >
                <div className="h-16 flex items-center px-6 border-b border-slate-800">
                    <BrainCircuit className="w-6 h-6 text-blue-500 mr-2" />
                    <span className="font-bold text-lg tracking-tight">AI Ops Platform</span>
                </div>

                <nav className="p-4 space-y-1">
                    {navItems.map((item) => (
                        <Link
                            key={item.href}
                            href={item.href}
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
                    ))}
                </nav>

                <div className="absolute bottom-4 left-4 right-4 p-4 bg-slate-800/50 rounded-lg">
                    <p className="text-xs text-slate-500 font-mono">Build: Phase 2 (Dev)</p>
                    <p className="text-xs text-slate-500 font-mono">User: Admin</p>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col min-w-0">
                <header className="h-16 flex items-center justify-between px-6 border-b border-slate-800 bg-slate-950/50 backdrop-blur-sm sticky top-0 z-40">
                    <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 -ml-2 text-slate-400 hover:text-white rounded-md">
                        {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
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
