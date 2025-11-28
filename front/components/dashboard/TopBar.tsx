"use client";

import { Bell, Search, User } from "lucide-react";
import { useAuthStore } from "@/services/auth";
import { useEffect } from "react";

export default function TopBar() {
    const { user, fetchProfile } = useAuthStore();

    useEffect(() => {
        fetchProfile();
    }, []);

    return (
        <header className="h-16 bg-slate-900/50 backdrop-blur-md border-b border-slate-800 fixed top-0 left-0 right-0 md:right-64 z-40 flex items-center justify-between px-6">
            {/* Search Bar */}
            <div className="flex items-center gap-4 flex-1 max-w-xl">
                <div className="relative w-full">
                    <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <input
                        type="text"
                        placeholder="جستجو در دستگاه‌ها، IPها یا آسیب‌پذیری‌ها..."
                        className="w-full bg-slate-800/50 border border-slate-700 rounded-full pr-10 pl-4 py-2 text-sm text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all text-right"
                    />
                </div>
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-4">
                {/* Notifications */}
                <button className="relative p-2 text-slate-400 hover:text-white transition-colors rounded-full hover:bg-slate-800">
                    <Bell className="w-5 h-5" />
                    <span className="absolute top-2 left-2 w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                </button>

                {/* User Profile */}
                <div className="flex items-center gap-3 pr-4 border-r border-slate-800">
                    <div className="text-left hidden sm:block">
                        <div className="text-sm font-medium text-white">{user?.first_name || "کاربر"} {user?.last_name || "مهمان"}</div>
                        <div className="text-xs text-slate-400">@{user?.username || "user"}</div>
                    </div>
                    <div className="w-9 h-9 bg-slate-700 rounded-full flex items-center justify-center border border-slate-600">
                        <User className="w-5 h-5 text-slate-300" />
                    </div>
                </div>
            </div>
        </header>
    );
}
