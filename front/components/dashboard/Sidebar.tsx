"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import {
    LayoutDashboard,
    Server,
    ShieldAlert,
    Network,
    Activity,
    Settings,
    LogOut,
    Plus
} from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/services/auth";
import { useState } from "react";
import ConnectAgentModal from "./ConnectAgentModal";

const menuItems = [
    { name: "نمای کلی", icon: LayoutDashboard, href: "/dashboard" },
    { name: "لیست دستگاه‌ها", icon: Server, href: "/dashboard/inventory" },
    { name: "مرکز آسیب‌پذیری", icon: ShieldAlert, href: "/dashboard/vulnerability" },
    { name: "مرکز پایش تهدید", icon: Activity, href: "/dashboard/scan" },
];

export default function Sidebar() {
    const pathname = usePathname();
    const [isModalOpen, setIsModalOpen] = useState(false);

    return (
        <>
            <aside className="hidden md:flex flex-col w-64 bg-slate-900 border-l border-slate-800 h-screen fixed right-0 top-0 z-50 text-slate-300">
                {/* Logo Area */}
                <div className="h-16 flex items-center px-6 border-b border-slate-800">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center overflow-hidden">
                            <Image src="/eriskalogo.png" alt="Eriska Logo" width={32} height={32} className="w-full h-full object-cover" />
                        </div>
                        <span className="text-xl font-bold text-white tracking-tight">Eriska</span>
                    </div>
                </div>

                {/* Navigation */}
                <nav className="flex-1 py-6 px-3 space-y-1">
                    {menuItems.map((item) => {
                        const isActive = pathname === item.href;
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative",
                                    isActive
                                        ? "text-white bg-emerald-500/10"
                                        : "hover:text-white hover:bg-slate-800"
                                )}
                            >
                                {isActive && (
                                    <motion.div
                                        layoutId="activeTab"
                                        className="absolute right-0 w-1 h-6 bg-emerald-500 rounded-l-full"
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        exit={{ opacity: 0 }}
                                    />
                                )}
                                <item.icon className={cn(
                                    "w-5 h-5 transition-colors",
                                    isActive ? "text-emerald-500" : "text-slate-400 group-hover:text-white"
                                )} />
                                <span className="font-medium">{item.name}</span>
                            </Link>
                        );
                    })}
                </nav>

                {/* Bottom Actions */}
                <div className="p-4 border-t border-slate-800">
                    <button
                        onClick={() => setIsModalOpen(true)}
                        className="flex items-center gap-3 px-3 py-2.5 w-full rounded-lg text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10 transition-all mb-1"
                    >
                        <Plus className="w-5 h-5" />
                        <span className="font-medium">افزودن ایجنت</span>
                    </button>
                    <Link href="/dashboard/profile" className="flex items-center gap-3 px-3 py-2.5 w-full rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-all">
                        <Settings className="w-5 h-5" />
                        <span className="font-medium">تنظیمات و پروفایل</span>
                    </Link>
                    <button
                        onClick={() => useAuthStore.getState().logout()}
                        className="flex items-center gap-3 px-3 py-2.5 w-full rounded-lg text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-all mt-1"
                    >
                        <LogOut className="w-5 h-5" />
                        <span className="font-medium">خروج</span>
                    </button>
                </div>
            </aside>

            <ConnectAgentModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
        </>
    );
}
