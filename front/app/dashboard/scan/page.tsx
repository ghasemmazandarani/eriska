"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
    Play,
    StopCircle,
    Clock,
    FileText,
    Download,
    Terminal,
    Settings,
    CheckCircle,
    XCircle
} from "lucide-react";
import { cn } from "@/lib/utils";
import api from "@/lib/api";
import { formatDistanceToNow } from "date-fns";
import { faIR } from "date-fns/locale";

export default function ScanPage() {
    const [isScanning, setIsScanning] = useState(false);
    const [logs, setLogs] = useState<string[]>([
        "[System] Ready to scan."
    ]);
    const [scanHistory, setScanHistory] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchScans = async () => {
            try {
                const response = await api.get("/scans/");
                setScanHistory(response.data);
            } catch (error) {
                console.error("Failed to fetch scans", error);
            } finally {
                setLoading(false);
            }
        };

        fetchScans();
    }, []);

    const toggleScan = () => {
        setIsScanning(!isScanning);
        if (!isScanning) {
            setLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] Starting new scan...`]);
            // Here you would trigger the actual scan via API if implemented
        } else {
            setLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] Scan stopped by user.`]);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">مرکز پایش تهدید</h1>
                    <p className="text-slate-400 mt-1">کنترل ایجنت Eriska و مشاهده گزارش‌های پایش تهدید</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Controls */}
                <div className="space-y-6">
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                        <h3 className="text-lg font-semibold text-white mb-4">کنترل اسکن</h3>

                        <div className="space-y-4">
                            <button
                                onClick={toggleScan}
                                className={cn(
                                    "w-full py-4 rounded-xl flex items-center justify-center gap-3 font-bold text-lg transition-all shadow-lg",
                                    isScanning
                                        ? "bg-red-500 hover:bg-red-600 text-white shadow-red-500/20"
                                        : "bg-emerald-500 hover:bg-emerald-600 text-white shadow-emerald-500/20"
                                )}
                            >
                                {isScanning ? (
                                    <>
                                        <StopCircle className="w-6 h-6" /> توقف اسکن
                                    </>
                                ) : (
                                    <>
                                        <Play className="w-6 h-6" /> شروع اسکن جدید
                                    </>
                                )}
                            </button>

                            <div className="grid grid-cols-2 gap-3">
                                <button className="py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium transition-colors border border-slate-700 flex flex-col items-center gap-1">
                                    <Clock className="w-5 h-5 text-blue-400" />
                                    <span className="text-xs">زمان‌بندی</span>
                                </button>
                                <button className="py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium transition-colors border border-slate-700 flex flex-col items-center gap-1">
                                    <Settings className="w-5 h-5 text-slate-400" />
                                    <span className="text-xs">تنظیمات</span>
                                </button>
                            </div>
                        </div>

                        <div className="mt-6 pt-6 border-t border-slate-800">
                            <div className="text-sm text-slate-400 mb-2">حالت اسکن</div>
                            <select className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500/50">
                                <option>کشف فعال (ARP + Ports)</option>
                                <option>مانیتورینگ غیرفعال (Sniffer)</option>
                                <option>اسکن رابط روتر</option>
                                <option>بازرسی امنیتی دوربین</option>
                            </select>
                        </div>
                    </div>

                    {/* Live Logs */}
                    <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 font-mono text-xs h-[300px] overflow-y-auto relative dir-ltr text-left">
                        <div className="absolute top-2 right-2 px-2 py-1 bg-slate-800 rounded text-slate-400 flex items-center gap-1">
                            <Terminal className="w-3 h-3" /> Terminal
                        </div>
                        <div className="space-y-1 mt-6">
                            {logs.map((log, i) => (
                                <div key={i} className="text-emerald-500/80 border-l-2 border-slate-800 pl-2">
                                    {log}
                                </div>
                            ))}
                            {isScanning && (
                                <div className="text-emerald-500 animate-pulse">_</div>
                            )}
                        </div>
                    </div>
                </div>

                {/* History */}
                <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                        <FileText className="w-5 h-5 text-slate-400" />
                        تاریخچه اسکن
                    </h3>

                    {loading ? (
                        <div className="text-center text-slate-500 py-10">در حال بارگذاری...</div>
                    ) : scanHistory.length === 0 ? (
                        <div className="text-center text-slate-500 py-10 border border-dashed border-slate-800 rounded-lg">
                            هنوز اسکنی انجام نشده است.
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {scanHistory.map((scan) => (
                                <div key={scan.id} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-slate-700/50 hover:bg-slate-800 transition-colors group">
                                    <div className="flex items-center gap-4">
                                        <div className={cn(
                                            "w-10 h-10 rounded-full flex items-center justify-center",
                                            "bg-emerald-500/10 text-emerald-500"
                                        )}>
                                            <CheckCircle className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <h4 className="text-white font-medium capitalize">{scan.scan_type} Scan</h4>
                                            <p className="text-sm text-slate-400 dir-ltr text-right">
                                                {formatDistanceToNow(new Date(scan.created_at), { addSuffix: true, locale: faIR })}
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-6">
                                        <button className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors">
                                            <Download className="w-5 h-5" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
}
