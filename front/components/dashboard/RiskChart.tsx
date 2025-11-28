export default function RiskChart({ data }: { data: any }) {
    const devices = data?.scan_results || [];
    const high = devices.filter((d: any) => d.risk_score >= 70).length;
    const medium = devices.filter((d: any) => d.risk_score >= 40 && d.risk_score < 70).length;
    const low = devices.filter((d: any) => d.risk_score < 40).length;
    const total = devices.length || 1; // Avoid division by zero

    return (
        <div className="glass-card p-6 rounded-2xl border border-slate-700/50 h-full">
            <h3 className="text-xl font-bold mb-6">توزیع ریسک</h3>

            <div className="flex items-center gap-4 mb-6">
                <div className="flex-1 h-4 bg-slate-700 rounded-full overflow-hidden flex">
                    <div className="bg-red-500 h-full" style={{ width: `${(high / total) * 100}%` }}></div>
                    <div className="bg-yellow-500 h-full" style={{ width: `${(medium / total) * 100}%` }}></div>
                    <div className="bg-emerald-500 h-full" style={{ width: `${(low / total) * 100}%` }}></div>
                </div>
            </div>

            <div className="space-y-3">
                <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-red-500"></div>
                        <span className="text-slate-300">پرخطر (Critical)</span>
                    </div>
                    <span className="font-bold text-white">{high}</span>
                </div>
                <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                        <span className="text-slate-300">متوسط (Warning)</span>
                    </div>
                    <span className="font-bold text-white">{medium}</span>
                </div>
                <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
                        <span className="text-slate-300">ایمن (Safe)</span>
                    </div>
                    <span className="font-bold text-white">{low}</span>
                </div>
            </div>
        </div>
    );
}
