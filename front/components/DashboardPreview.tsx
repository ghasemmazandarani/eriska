import { Activity, Shield, Map, AlertOctagon, Server, Wifi } from 'lucide-react';

export default function DashboardPreview() {
    return (
        <section className="container mx-auto px-4 py-24 relative z-10">
            <div className="text-center mb-16">
                <h2 className="text-3xl md:text-5xl font-black mb-6">داشبورد امنیتی پیشرفته</h2>
                <p className="text-slate-400 text-lg">ساخته شده برای تیم‌های امنیتی — سریع، ساده، عملیاتی</p>
            </div>

            <div className="relative max-w-6xl mx-auto">
                {/* Glow Effect */}
                <div className="absolute -inset-4 bg-gradient-to-r from-emerald-500/20 to-blue-500/20 rounded-[2.5rem] blur-2xl -z-10"></div>

                {/* Main Dashboard Mockup */}
                <div className="glass-card rounded-[2rem] border border-slate-700/50 overflow-hidden shadow-2xl shadow-black/50 bg-slate-900/95">
                    {/* Window Controls */}
                    <div className="bg-slate-900 border-b border-slate-800 p-4 flex items-center gap-4">
                        <div className="flex gap-2">
                            <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
                            <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                            <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
                        </div>
                        <div className="bg-slate-800 px-6 py-1.5 rounded-full text-xs text-slate-400 flex-1 text-center font-mono border border-slate-700/50 flex items-center justify-center gap-2">
                            <Shield className="w-3 h-3" />
                            dashboard.eriska.security
                        </div>
                    </div>

                    <div className="p-8 grid grid-cols-12 gap-8 h-[600px]">
                        {/* Sidebar */}
                        <div className="col-span-2 hidden md:flex flex-col gap-2 border-l border-slate-800 pl-4">
                            <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-xl flex items-center gap-3 font-bold border border-emerald-500/20">
                                <Activity className="w-5 h-5" /> وضعیت
                            </div>
                            <div className="p-3 text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 rounded-xl flex items-center gap-3 transition-colors cursor-pointer">
                                <Map className="w-5 h-5" /> نقشه شبکه
                            </div>
                            <div className="p-3 text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 rounded-xl flex items-center gap-3 transition-colors cursor-pointer">
                                <Shield className="w-5 h-5" /> آسیب‌پذیری‌ها
                            </div>
                            <div className="p-3 text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 rounded-xl flex items-center gap-3 transition-colors cursor-pointer">
                                <Server className="w-5 h-5" /> دارایی‌ها
                            </div>
                        </div>

                        {/* Main Content */}
                        <div className="col-span-12 md:col-span-10 grid grid-cols-3 gap-6 content-start">
                            {/* Stats Cards */}
                            <div className="bg-slate-800/40 p-6 rounded-2xl border border-slate-700/50 backdrop-blur-sm">
                                <div className="flex justify-between items-start mb-4">
                                    <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400"><Wifi className="w-6 h-6" /></div>
                                    <span className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded">+12%</span>
                                </div>
                                <div className="text-slate-400 text-sm mb-1">دستگاه‌های آنلاین</div>
                                <div className="text-4xl font-bold text-white">124</div>
                            </div>
                            <div className="bg-slate-800/40 p-6 rounded-2xl border border-slate-700/50 backdrop-blur-sm">
                                <div className="flex justify-between items-start mb-4">
                                    <div className="p-2 bg-red-500/10 rounded-lg text-red-400"><AlertOctagon className="w-6 h-6" /></div>
                                    <span className="text-xs text-red-400 bg-red-500/10 px-2 py-1 rounded">+2</span>
                                </div>
                                <div className="text-slate-400 text-sm mb-1">ریسک‌های بحرانی</div>
                                <div className="text-4xl font-bold text-white">3</div>
                            </div>
                            <div className="bg-slate-800/40 p-6 rounded-2xl border border-slate-700/50 backdrop-blur-sm">
                                <div className="flex justify-between items-start mb-4">
                                    <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-400"><Shield className="w-6 h-6" /></div>
                                </div>
                                <div className="text-slate-400 text-sm mb-1">امتیاز امنیت</div>
                                <div className="text-4xl font-bold text-emerald-400">87/100</div>
                            </div>

                            {/* Chart Area (Fake) */}
                            <div className="col-span-2 bg-slate-800/40 p-6 rounded-2xl border border-slate-700/50 h-72 flex flex-col justify-between">
                                <div className="flex justify-between items-center mb-4">
                                    <h4 className="font-bold text-slate-200">ترافیک شبکه</h4>
                                    <select className="bg-slate-900 border border-slate-700 rounded-lg text-xs p-1 text-slate-400 outline-none">
                                        <option>۲۴ ساعت گذشته</option>
                                    </select>
                                </div>
                                <div className="flex items-end justify-between gap-2 h-full px-2 pb-2">
                                    {[40, 60, 45, 70, 85, 65, 90, 75, 60, 80, 55, 70, 95, 60, 50].map((h, i) => (
                                        <div key={i} className="w-full bg-gradient-to-t from-emerald-500/20 to-emerald-500/60 rounded-t-sm hover:to-emerald-400 transition-all cursor-pointer group relative" style={{ height: `${h}%` }}>
                                            <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-slate-900 text-xs px-2 py-1 rounded border border-slate-700 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                                                {h} Mbps
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Alerts List */}
                            <div className="bg-slate-800/40 p-6 rounded-2xl border border-slate-700/50 h-72 overflow-hidden flex flex-col">
                                <h4 className="font-bold mb-4 flex items-center gap-2 text-slate-200"><AlertOctagon className="w-4 h-4 text-red-500" /> هشدارهای اخیر</h4>
                                <div className="space-y-3 overflow-y-auto pr-2 custom-scrollbar">
                                    <div className="text-xs bg-red-500/5 text-red-300 p-3 rounded-xl border border-red-500/10 hover:bg-red-500/10 transition-colors cursor-pointer">
                                        <div className="font-bold mb-1">SMB Port Open</div>
                                        <div className="opacity-70">192.168.1.50 • Just now</div>
                                    </div>
                                    <div className="text-xs bg-yellow-500/5 text-yellow-300 p-3 rounded-xl border border-yellow-500/10 hover:bg-yellow-500/10 transition-colors cursor-pointer">
                                        <div className="font-bold mb-1">New Device Found</div>
                                        <div className="opacity-70">Unknown Vendor • 5m ago</div>
                                    </div>
                                    <div className="text-xs bg-blue-500/5 text-blue-300 p-3 rounded-xl border border-blue-500/10 hover:bg-blue-500/10 transition-colors cursor-pointer">
                                        <div className="font-bold mb-1">Scan Completed</div>
                                        <div className="opacity-70">Zone A • 1h ago</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
