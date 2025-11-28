"use client";

import { useEffect, useState, use } from "react";
import { motion } from "framer-motion";
import {
    Shield,
    Wifi,
    Activity,
    Globe,
    Server,
    Cpu,
    Clock,
    AlertTriangle,
    CheckCircle,
    XCircle,
    Terminal,
    Lock,
    ArrowRight
} from "lucide-react";
import { cn } from "@/lib/utils";
import api from "@/lib/api";
import { useRouter } from "next/navigation";

interface Device {
    id: string;
    ip_address: string;
    mac_address: string;
    hostname: string;
    vendor: string;
    device_type: string;
    risk_score: number;
    os: string;
    firmware: string;
    ports: any[];
    vulnerabilities: any[];
    timeline: any[];
    last_seen: string;
}

export default function DeviceDetailPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = use(params);
    const [activeTab, setActiveTab] = useState("overview");
    const [device, setDevice] = useState<Device | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const fetchDevice = async () => {
            try {
                const response = await api.get(`/devices/${id}/`);
                setDevice(response.data);
            } catch (error) {
                console.error("Failed to fetch device details", error);
            } finally {
                setLoading(false);
            }
        };

        if (id) {
            fetchDevice();
        }
    }, [id]);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[50vh]">
                <div className="text-emerald-500 animate-pulse">در حال دریافت اطلاعات دستگاه...</div>
            </div>
        );
    }

    if (!device) {
        return (
            <div className="flex flex-col items-center justify-center h-[50vh] space-y-4">
                <div className="text-slate-400">دستگاه مورد نظر یافت نشد.</div>
                <button
                    onClick={() => router.back()}
                    className="flex items-center gap-2 text-emerald-500 hover:text-emerald-400"
                >
                    <ArrowRight className="w-4 h-4" />
                    بازگشت
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header Profile */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                <div className="flex flex-col md:flex-row gap-6 items-start">
                    {/* Icon/Image */}
                    <div className="w-24 h-24 bg-slate-800 rounded-2xl flex items-center justify-center border border-slate-700">
                        <Server className="w-10 h-10 text-slate-400" />
                    </div>

                    {/* Info */}
                    <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                            <h1 className="text-2xl font-bold text-white dir-ltr text-right">{device.hostname || device.ip_address}</h1>
                            <span className="px-2 py-1 bg-emerald-500/10 text-emerald-500 text-xs font-bold rounded-full border border-emerald-500/20 flex items-center gap-1">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                                آنلاین
                            </span>
                        </div>
                        <div className="flex flex-wrap gap-4 text-sm text-slate-400">
                            <div className="flex items-center gap-1 dir-ltr">
                                <Globe className="w-4 h-4" />
                                {device.ip_address}
                            </div>
                            <div className="flex items-center gap-1 dir-ltr">
                                <Cpu className="w-4 h-4" />
                                {device.mac_address || 'N/A'}
                            </div>
                            <div className="flex items-center gap-1">
                                <Server className="w-4 h-4" />
                                {device.vendor || 'Unknown'}
                            </div>
                        </div>
                    </div>

                    {/* Risk Badge */}
                    <div className="text-left">
                        <div className="text-sm text-slate-400 mb-1">امتیاز ریسک</div>
                        <div className="flex items-center gap-2 justify-end">
                            <div className={cn(
                                "text-4xl font-bold",
                                device.risk_score >= 70 ? "text-red-500" : device.risk_score >= 40 ? "text-amber-500" : "text-emerald-500"
                            )}>{device.risk_score}</div>
                            <div className="text-sm text-slate-500">/100</div>
                        </div>
                        <div className={cn(
                            "mt-2 px-3 py-1 text-xs font-medium rounded-lg border inline-block",
                            device.risk_score >= 70 ? "bg-red-500/10 text-red-400 border-red-500/20" :
                                device.risk_score >= 40 ? "bg-amber-500/10 text-amber-400 border-amber-500/20" :
                                    "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                        )}>
                            {device.risk_score >= 70 ? "ریسک بحرانی" : device.risk_score >= 40 ? "ریسک متوسط" : "امن"}
                        </div>
                    </div>
                </div>

                {/* Tabs */}
                <div className="flex gap-6 mt-8 border-b border-slate-800 overflow-x-auto">
                    {[
                        { id: "overview", label: "نمای کلی" },
                        { id: "network", label: "شبکه" },
                        { id: "vulnerabilities", label: "آسیب‌پذیری‌ها" },
                        { id: "timeline", label: "تایم‌لاین" }
                    ].map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={cn(
                                "pb-3 text-sm font-medium transition-colors relative whitespace-nowrap",
                                activeTab === tab.id ? "text-white" : "text-slate-400 hover:text-slate-300"
                            )}
                        >
                            {tab.label}
                            {activeTab === tab.id && (
                                <motion.div
                                    layoutId="activeTabLine"
                                    className="absolute bottom-0 left-0 w-full h-0.5 bg-emerald-500"
                                />
                            )}
                        </button>
                    ))}
                </div>
            </div>

            {/* Content */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Left Column (Main Info) */}
                <div className="lg:col-span-2 space-y-6">

                    {/* Overview Tab */}
                    {activeTab === "overview" && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                            {/* Basic Info Card */}
                            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                    <Activity className="w-5 h-5 text-emerald-500" />
                                    اطلاعات دستگاه
                                </h3>
                                <div className="grid grid-cols-2 gap-y-4 gap-x-8">
                                    <div>
                                        <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">مدل</div>
                                        <div className="text-white font-medium">{device.hostname || '-'}</div>
                                    </div>
                                    <div>
                                        <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">فریمور</div>
                                        <div className="text-white font-medium">{device.firmware || '-'}</div>
                                    </div>
                                    <div>
                                        <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">سیستم عامل</div>
                                        <div className="text-white font-medium">{device.os || '-'}</div>
                                    </div>
                                    <div>
                                        <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">نوع</div>
                                        <div className="text-white font-medium">{device.device_type}</div>
                                    </div>
                                </div>
                            </div>

                            {/* Open Ports */}
                            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                    <Terminal className="w-5 h-5 text-blue-500" />
                                    پورت‌ها و سرویس‌های باز
                                </h3>
                                {device.ports && device.ports.length > 0 ? (
                                    <div className="space-y-3">
                                        {device.ports.map((p: any, idx: number) => (
                                            <div key={idx} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-8 h-8 bg-slate-700 rounded flex items-center justify-center font-mono text-xs text-white">
                                                        {p.port}
                                                    </div>
                                                    <div>
                                                        <div className="text-white font-medium">{p.service || 'Unknown'}</div>
                                                        {p.banner && <div className="text-xs text-slate-400 font-mono dir-ltr text-right">{p.banner}</div>}
                                                    </div>
                                                </div>
                                                <div className="px-2 py-1 bg-emerald-500/10 text-emerald-500 text-xs rounded border border-emerald-500/20">
                                                    باز
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-slate-500 text-sm">هیچ پورت بازی شناسایی نشد.</div>
                                )}
                            </div>
                        </motion.div>
                    )}

                    {/* Vulnerabilities Tab */}
                    {activeTab === "vulnerabilities" && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                            {device.vulnerabilities && device.vulnerabilities.length > 0 ? (
                                device.vulnerabilities.map((vuln: any, idx: number) => (
                                    <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-red-500/30 transition-colors">
                                        <div className="flex justify-between items-start mb-2">
                                            <div className="flex items-center gap-3">
                                                <Shield className="w-5 h-5 text-red-500" />
                                                <h4 className="text-lg font-bold text-white dir-ltr">{vuln.id || 'Unknown Vuln'}</h4>
                                            </div>
                                            <span className="px-3 py-1 bg-red-500/10 text-red-400 text-xs font-bold rounded-full border border-red-500/20 dir-ltr">
                                                {vuln.severity || 'HIGH'} ({vuln.score || 'N/A'})
                                            </span>
                                        </div>
                                        <p className="text-slate-400">{vuln.description || 'توضیحات در دسترس نیست.'}</p>
                                        <div className="mt-4 flex gap-3">
                                            <button className="text-sm text-blue-400 hover:text-blue-300">مشاهده جزئیات</button>
                                            <button className="text-sm text-emerald-400 hover:text-emerald-300">راه حل موجود است</button>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="text-slate-500 text-center py-8">هیچ آسیب‌پذیری شناخته شده‌ای یافت نشد.</div>
                            )}
                        </motion.div>
                    )}

                    {/* Other tabs placeholders */}
                    {(activeTab === "network" || activeTab === "timeline") && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-center text-slate-500">
                            اطلاعات این بخش هنوز در دسترس نیست.
                        </motion.div>
                    )}

                </div>

                {/* Right Column (Timeline/Actions) */}
                <div className="space-y-6">
                    {/* Actions */}
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">عملیات</h3>
                        <div className="space-y-3">
                            <button className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium transition-colors">
                                اسکن فوری دستگاه
                            </button>
                            <button className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm font-medium transition-colors border border-slate-700">
                                ویرایش متادیتا
                            </button>
                            <button className="w-full py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg text-sm font-medium transition-colors border border-red-500/20">
                                قرنطینه دستگاه
                            </button>
                        </div>
                    </div>

                    {/* Timeline Preview */}
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">فعالیت‌های اخیر</h3>
                        <div className="space-y-6 relative before:absolute before:right-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800 pr-8">
                            {device.timeline && device.timeline.length > 0 ? (
                                device.timeline.map((item: any, i: number) => (
                                    <div key={i} className="relative">
                                        <div className={cn(
                                            "absolute -right-10 top-1 w-4 h-4 rounded-full border-2 border-slate-900",
                                            item.type === 'info' ? "bg-blue-500" : item.type === 'warning' ? "bg-amber-500" : "bg-emerald-500"
                                        )} />
                                        <div className="text-sm text-white font-medium">{item.event}</div>
                                        <div className="text-xs text-slate-500 dir-ltr text-right">{item.time}</div>
                                    </div>
                                ))
                            ) : (
                                <div className="text-sm text-slate-500">فعالیت اخیر ثبت نشده است.</div>
                            )}
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}
