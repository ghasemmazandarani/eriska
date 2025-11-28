"use client";

import DashboardLayout from "@/components/dashboard/DashboardLayout";
import { useAuthStore } from "@/services/auth";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function Layout({ children }: { children: React.ReactNode }) {
    const { isAuthenticated, fetchProfile } = useAuthStore();
    const router = useRouter();
    const [isChecking, setIsChecking] = useState(true);

    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem('access_token');
            if (!token) {
                router.push('/login');
                return;
            }

            try {
                // If we have a token but state says not authenticated, try to fetch profile
                if (!isAuthenticated) {
                    await fetchProfile();
                }
            } catch (error) {
                router.push('/login');
            } finally {
                setIsChecking(false);
            }
        };

        checkAuth();
    }, [isAuthenticated, router, fetchProfile]);

    if (isChecking) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center">
                <div className="text-emerald-500 animate-pulse">در حال بررسی دسترسی...</div>
            </div>
        );
    }

    return <DashboardLayout>{children}</DashboardLayout>;
}
