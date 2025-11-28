"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/services/auth";
import { User, Mail, Shield, LogOut } from "lucide-react";
import { useRouter } from "next/navigation";

export default function ProfilePage() {
    const { user, logout, fetchProfile } = useAuthStore();
    const router = useRouter();

    useEffect(() => {
        fetchProfile();
    }, []);

    if (!user) {
        return <div className="text-white">در حال بارگذاری...</div>;
    }

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">پروفایل کاربری</h1>
                    <p className="text-slate-400 mt-1">مدیریت اطلاعات حساب کاربری.</p>
                </div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-8">
                <div className="flex items-center gap-6 mb-8">
                    <div className="w-20 h-20 bg-slate-800 rounded-full flex items-center justify-center border-2 border-slate-700">
                        <User className="w-10 h-10 text-slate-400" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-white">{user.first_name} {user.last_name}</h2>
                        <p className="text-slate-400">@{user.username}</p>
                    </div>
                </div>

                <div className="space-y-4">
                    <div className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                        <Mail className="w-5 h-5 text-slate-400" />
                        <div>
                            <div className="text-xs text-slate-500 uppercase">ایمیل</div>
                            <div className="text-white">{user.email}</div>
                        </div>
                    </div>

                    <div className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                        <Shield className="w-5 h-5 text-emerald-500" />
                        <div>
                            <div className="text-xs text-slate-500 uppercase">نقش</div>
                            <div className="text-white">مدیر سیستم (Admin)</div>
                        </div>
                    </div>
                </div>

                <div className="mt-8 pt-6 border-t border-slate-800">
                    <button
                        onClick={logout}
                        className="flex items-center gap-2 text-red-400 hover:text-red-300 transition-colors font-medium"
                    >
                        <LogOut className="w-5 h-5" />
                        خروج از حساب کاربری
                    </button>
                </div>
            </div>
        </div>
    );
}
