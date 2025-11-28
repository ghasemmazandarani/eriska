import { ChevronDown, ChevronUp, Server, Video, Router, Printer, HelpCircle } from 'lucide-react';
import { useState } from 'react';

interface DeviceListProps {
    data: any;
}

export default function DeviceList({ data }: DeviceListProps) {
    const [expandedId, setExpandedId] = useState<string | null>(null);

    const toggleExpand = (ip: string) => {
        setExpandedId(expandedId === ip ? null : ip);
    };

    const getIcon = (type: string) => {
        const t = type?.toLowerCase() || '';
        if (t.includes('camera')) return <Video className="w-5 h-5 text-blue-400" />;
        if (t.includes('router') || t.includes('gateway')) return <Router className="w-5 h-5 text-emerald-400" />;
        if (t.includes('printer')) return <Printer className="w-5 h-5 text-yellow-400" />;
        if (t.includes('server')) return <Server className="w-5 h-5 text-purple-400" />;
        return <HelpCircle className="w-5 h-5 text-slate-500" />;
    };

    const getRiskColor = (score: number) => {
        if (score >= 70) return 'text-red-500 bg-red-500/10 border-red-500/20';
        if (score >= 40) return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
        return 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20';
    };

    const getRiskLabel = (score: number) => {
        if (score >= 70) return 'بحرانی';
        if (score >= 40) return 'متوسط';
        return 'ایمن';
    };

    return (
        <div className="glass-card rounded-2xl border border-slate-700/50 overflow-hidden">
            <div className="p-6 border-b border-slate-700/50">
                <h3 className="text-xl font-bold">لیست دستگاه‌ها</h3>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-right">
                    <thead className="bg-slate-800/50 text-slate-400 text-sm">
                        <tr>
                            <th className="p-4 font-medium">نوع</th>
                            <th className="p-4 font-medium">آدرس IP</th>
                            <th className="p-4 font-medium">آدرس MAC</th>
                            <th className="p-4 font-medium">سازنده</th>
                            <th className="p-4 font-medium">ریسک</th>
                            <th className="p-4 font-medium">جزئیات</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700/50">
                        {data?.scan_results?.map((device: any) => (
                            <>
                                <tr key={device.ip} className="hover:bg-slate-800/30 transition-colors">
                                    <td className="p-4">
                                        <div className="flex items-center gap-2">
                                            {getIcon(device.device_type)}
                                            <span className="text-slate-200">{device.device_type || 'Unknown'}</span>
                                        </div>
                                    </td>
                                    <td className="p-4 font-mono text-slate-300">{device.ip}</td>
                                    <td className="p-4 font-mono text-slate-400 text-sm">{device.mac}</td>
                                    <td className="p-4 text-slate-300">{device.vendor || 'Unknown'}</td>
                                    <td className="p-4">
                                        <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getRiskColor(device.risk_score)}`}>
                                            {getRiskLabel(device.risk_score)} ({device.risk_score})
                                        </span>
                                    </td>
                                    <td className="p-4">
                                        <button onClick={() => toggleExpand(device.ip)} className="p-2 hover:bg-slate-700 rounded-lg transition-colors">
                                            {expandedId === device.ip ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                                        </button>
                                    </td>
                                </tr>
                                {expandedId === device.ip && (
                                    <tr className="bg-slate-800/20">
                                        <td colSpan={6} className="p-6">
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                <div>
                                                    <h4 className="font-bold text-slate-400 mb-2 text-sm">پورت‌های باز:</h4>
                                                    <div className="flex flex-wrap gap-2">
                                                        {device.open_ports?.length > 0 ? (
                                                            device.open_ports.map((p: number) => (
                                                                <span key={p} className="bg-slate-700 text-slate-300 px-2 py-1 rounded text-xs font-mono">{p}</span>
                                                            ))
                                                        ) : (
                                                            <span className="text-slate-500 text-sm">هیچ پورت بازی یافت نشد.</span>
                                                        )}
                                                    </div>
                                                </div>
                                                <div>
                                                    <h4 className="font-bold text-slate-400 mb-2 text-sm">تحلیل ریسک:</h4>
                                                    <ul className="list-disc list-inside text-sm text-slate-300 space-y-1">
                                                        {device.risk_factors?.map((f: string, i: number) => (
                                                            <li key={i}>{f}</li>
                                                        ))}
                                                        {(!device.risk_factors || device.risk_factors.length === 0) && (
                                                            <li className="text-emerald-500">هیچ ریسک خاصی شناسایی نشد.</li>
                                                        )}
                                                    </ul>
                                                </div>
                                            </div>
                                        </td>
                                    </tr>
                                )}
                            </>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
