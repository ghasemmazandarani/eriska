import { Shield, Activity, AlertTriangle, Network } from 'lucide-react';

interface SummaryStatsProps {
    data: any;
}

export default function SummaryStats({ data }: SummaryStatsProps) {
    // Calculate stats safely
    const devices = data?.scan_results || [];
    const totalDevices = devices.length;
    const criticalRisks = devices.filter((d: any) => d.risk_score >= 70).length;

    // Calculate average score
    const avgScore = totalDevices > 0
        ? Math.round(devices.reduce((acc: number, d: any) => acc + (100 - d.risk_score), 0) / totalDevices)
        : 0;

    return (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="glass-card p-6 rounded-2xl border border-slate-700/50 flex items-center gap-4">
                <div className="p-3 bg-emerald-500/10 rounded-xl text-emerald-500">
                    <Shield className="w-8 h-8" />
                </div>
                <div>
                    <div className="text-slate-400 text-sm">امتیاز امنیت شبکه</div>
                    <div className="text-3xl font-black text-white">{avgScore}/100</div>
                </div>
            </div>

            <div className="glass-card p-6 rounded-2xl border border-slate-700/50 flex items-center gap-4">
                <div className="p-3 bg-blue-500/10 rounded-xl text-blue-500">
                    <Network className="w-8 h-8" />
                </div>
                <div>
                    <div className="text-slate-400 text-sm">دستگاه‌های آنلاین</div>
                    <div className="text-3xl font-black text-white">{totalDevices}</div>
                </div>
            </div>

            <div className="glass-card p-6 rounded-2xl border border-slate-700/50 flex items-center gap-4">
                <div className="p-3 bg-red-500/10 rounded-xl text-red-500">
                    <AlertTriangle className="w-8 h-8" />
                </div>
                <div>
                    <div className="text-slate-400 text-sm">ریسک‌های بحرانی</div>
                    <div className="text-3xl font-black text-white">{criticalRisks}</div>
                </div>
            </div>

            <div className="glass-card p-6 rounded-2xl border border-slate-700/50 flex items-center gap-4">
                <div className="p-3 bg-purple-500/10 rounded-xl text-purple-500">
                    <Activity className="w-8 h-8" />
                </div>
                <div>
                    <div className="text-slate-400 text-sm">وضعیت اسکن</div>
                    <div className="text-lg font-bold text-emerald-400">تکمیل شده</div>
                </div>
            </div>
        </div>
    );
}
