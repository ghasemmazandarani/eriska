"use client";

import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatCardProps {
    title: string;
    value: string | number;
    icon: LucideIcon;
    trend?: {
        value: number;
        isPositive: boolean;
    };
    color?: "emerald" | "blue" | "red" | "amber";
    delay?: number;
}

export default function StatCard({ title, value, icon: Icon, trend, color = "blue", delay = 0 }: StatCardProps) {
    const colorStyles = {
        emerald: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
        blue: "bg-blue-500/10 text-blue-500 border-blue-500/20",
        red: "bg-red-500/10 text-red-500 border-red-500/20",
        amber: "bg-amber-500/10 text-amber-500 border-amber-500/20",
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay }}
            className="bg-slate-900 border border-slate-800 rounded-xl p-6 relative overflow-hidden group hover:border-slate-700 transition-colors"
        >
            <div className="flex justify-between items-start">
                <div>
                    <p className="text-slate-400 text-sm font-medium mb-1">{title}</p>
                    <h3 className="text-2xl font-bold text-white">{value}</h3>
                </div>
                <div className={cn("p-3 rounded-lg", colorStyles[color])}>
                    <Icon className="w-5 h-5" />
                </div>
            </div>

            {trend && (
                <div className="mt-4 flex items-center gap-2 text-sm">
                    <span className={cn(
                        "font-medium dir-ltr",
                        trend.value === 0 ? "text-slate-400" : trend.isPositive ? "text-emerald-400" : "text-red-400"
                    )}>
                        {Math.abs(trend.value)}%
                        {trend.value !== 0 && (trend.isPositive ? "+" : "-")}
                    </span>
                    <span className="text-slate-500">نسبت به اسکن قبلی</span>
                </div>
            )}

            {/* Background Glow Effect */}
            <div className={cn(
                "absolute -left-6 -bottom-6 w-24 h-24 rounded-full blur-3xl opacity-0 group-hover:opacity-20 transition-opacity duration-500",
                color === "emerald" && "bg-emerald-500",
                color === "blue" && "bg-blue-500",
                color === "red" && "bg-red-500",
                color === "amber" && "bg-amber-500",
            )} />
        </motion.div>
    );
}
