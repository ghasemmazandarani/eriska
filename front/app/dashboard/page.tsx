"use client";

import { useEffect, useState } from "react";
import {
    ShieldCheck,
    AlertTriangle,
    Activity,
    Wifi,
    Server,
    Plus
} from "lucide-react";
import StatCard from "@/components/dashboard/StatCard";
import AgentsList from "@/components/dashboard/AgentsList";
import ConnectAgentModal from "@/components/dashboard/ConnectAgentModal";
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell
} from "recharts";
import api from "@/lib/api";

export default function Dashboard() {
    const [stats, setStats] = useState({
        total_devices: 0,
        high_risk_devices: 0,
        online_devices: 0,
        avg_risk_score: 0,
        risk_trend_value: 0,
        total_devices_trend: 0,
        high_risk_trend: 0,
        online_devices_trend: 0,
        risk_trend: [],
        device_distribution: [],
        agent_count: 0,
        is_connected: false
    });
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await api.get("/stats/");
                setStats(response.data);
            } catch (error) {
                console.error("Failed to fetch dashboard stats", error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    const deviceDistribution = [
        { name: "دوربین‌ها", value: 45, color: "#10b981" }, // Emerald
        { name: "روترها", value: 25, color: "#3b82f6" },   // Blue
        { name: "سرورها", value: 20, color: "#8b5cf6" },   // Violet
        { name: "IoT", value: 10, color: "#f59e0b" },      // Amber
    ];

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full min-h-[400px]">
                <div className="text-emerald-500 animate-pulse">در حال بارگذاری اطلاعات...</div>
            </div>
        );
    }

    // Empty State
    if (stats.agent_count === 0) {
        return (
            <div className="h-[80vh] flex flex-col items-center justify-center text-center space-y-6">
                <div className="w-24 h-24 bg-slate-800 rounded-full flex items-center justify-center mb-4 animate-bounce">
                    <Server className="w-12 h-12 text-emerald-500" />
                </div>
                <h1 className="text-3xl font-bold text-white">خوش آمدید به اریسکا 👋</h1>
                <p className="text-slate-400 max-w-md text-lg">
                    برای شروع مانیتورینگ و آنالیز امنیت شبکه، ابتدا باید یک ایجنت را به داشبورد متصل کنید.
                </p>
                <button
                    onClick={() => setIsModalOpen(true)}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white px-8 py-3 rounded-xl font-bold text-lg shadow-lg shadow-emerald-500/20 transition-all flex items-center gap-2"
                >
                    <Plus className="w-6 h-6" />
                    اتصال اولین ایجنت
                </button>
                <ConnectAgentModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-white">نمای کلی داشبورد</h1>
                    <p className="text-slate-400 mt-1">وضعیت امنیتی شبکه و دستگاه‌های خود را رصد کنید.</p>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-400 bg-slate-800/50 px-3 py-1.5 rounded-lg border border-slate-700">
                    <span className={`w-2 h-2 rounded-full ${stats.is_connected ? "bg-emerald-500 animate-pulse" : "bg-red-500"}`}></span>
                    {stats.is_connected ? "سیستم فعال و در حال پایش است" : "ارتباط با ایجنت قطع شده است"}
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    title="کل دستگاه‌ها"
                    value={stats.total_devices.toString()}
                    icon={Server}
                    trend={{
                        value: Math.abs(stats.total_devices_trend || 0),
                        isPositive: (stats.total_devices_trend || 0) > 0
                    }}
                    color="blue"
                />
                <StatCard
                    title="دستگاه‌های پرریسک"
                    value={stats.high_risk_devices.toString()}
                    icon={AlertTriangle}
                    trend={{
                        value: Math.abs(stats.high_risk_trend || 0),
                        isPositive: (stats.high_risk_trend || 0) > 0
                    }}
                    color="red"
                />
                <StatCard
                    title="میانگین نمره ریسک"
                    value={`${stats.avg_risk_score}/100`}
                    icon={ShieldCheck}
                    trend={{
                        value: Math.abs(stats.risk_trend_value || 0),
                        isPositive: (stats.risk_trend_value || 0) > 0
                    }}
                    color="emerald"
                />
                <StatCard
                    title="دستگاه‌های آنلاین"
                    value={stats.online_devices.toString()}
                    icon={Wifi}
                    trend={{
                        value: Math.abs(stats.online_devices_trend || 0),
                        isPositive: (stats.online_devices_trend || 0) > 0
                    }}
                    color="blue"
                />
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Network Risk Trend */}
                <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
                    <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-emerald-500" />
                        روند ریسک شبکه (۷ روز گذشته)
                    </h3>
                    <div className="h-[300px] w-full" dir="ltr">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={stats.risk_trend}>
                                <defs>
                                    <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                <XAxis dataKey="name" stroke="#64748b" tick={{ fill: '#64748b' }} />
                                <YAxis stroke="#64748b" tick={{ fill: '#64748b' }} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc' }}
                                    itemStyle={{ color: '#10b981' }}
                                />
                                <Area type="monotone" dataKey="risk" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorRisk)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Right Column: Agents & Distribution */}
                <div className="space-y-6">
                    {/* Active Agents */}
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-bold text-white">ایجنت‌های فعال</h3>
                            <button onClick={() => setIsModalOpen(true)} className="text-emerald-500 hover:text-emerald-400">
                                <Plus className="w-5 h-5" />
                            </button>
                        </div>
                        <AgentsList />
                    </div>

                    {/* Device Distribution */}
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                        <h3 className="text-lg font-bold text-white mb-6">توزیع دستگاه‌ها</h3>
                        <div className="h-[200px] w-full relative" dir="ltr">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={stats.device_distribution || []}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {(stats.device_distribution || []).map((entry: any, index: number) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc' }}
                                    />
                                </PieChart>
                            </ResponsiveContainer>
                            {/* Center Text */}
                            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-white">{stats.total_devices}</div>
                                    <div className="text-xs text-slate-400">دستگاه</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <ConnectAgentModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
        </div>
    );
}
