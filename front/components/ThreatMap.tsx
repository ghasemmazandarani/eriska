"use client";

import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { Shield, AlertOctagon, Globe } from 'lucide-react';

export default function ThreatMap() {
    const [threats, setThreats] = useState<{ id: number, x: number, y: number, type: 'block' | 'scan' }[]>([]);

    // Generate random threats
    useEffect(() => {
        const interval = setInterval(() => {
            const newThreat = {
                id: Date.now(),
                x: Math.random() * 100,
                y: Math.random() * 100,
                type: Math.random() > 0.7 ? 'block' as const : 'scan' as const
            };

            setThreats(prev => [...prev.slice(-15), newThreat]); // Keep last 15
        }, 800);

        return () => clearInterval(interval);
    }, []);

    return (
        <section className="container mx-auto px-4 py-24 relative z-10 overflow-hidden">
            <div className="flex flex-col lg:flex-row items-center gap-16">

                {/* Text Content */}
                <div className="flex-1 space-y-8 text-right order-2 lg:order-1">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-sm font-medium animate-pulse">
                        <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                        <span>رصد لحظه‌ای تهدیدات</span>
                    </div>

                    <h2 className="text-4xl md:text-6xl font-black leading-tight">
                        دفاع سایبری <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-l from-red-500 to-orange-500">
                            در مقیاس جهانی
                        </span>
                    </h2>

                    <p className="text-slate-400 text-lg leading-relaxed">
                        شبکه هوشمند اریسکا به صورت ۲۴/۷ در حال پایش و خنثی‌سازی تهدیدات است. با هر حمله جدید، سیستم ایمنی ما قوی‌تر می‌شود و این دانش فوراً به تمام ایجنت‌ها منتقل می‌گردد.
                    </p>

                    <div className="grid grid-cols-2 gap-6">
                        <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800">
                            <div className="text-3xl font-bold text-white mb-1">۲.۴M+</div>
                            <div className="text-sm text-slate-500">تهدید مسدود شده امروز</div>
                        </div>
                        <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800">
                            <div className="text-3xl font-bold text-emerald-400 mb-1">۹۹.۹٪</div>
                            <div className="text-sm text-slate-500">نرخ تشخیص موفق</div>
                        </div>
                    </div>
                </div>

                {/* Map Visual */}
                <div className="flex-1 w-full relative order-1 lg:order-2">
                    <div className="aspect-square md:aspect-video lg:aspect-square relative bg-slate-900/30 rounded-full border border-slate-800/50 backdrop-blur-sm overflow-hidden shadow-2xl shadow-emerald-900/20">

                        {/* Grid Lines */}
                        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:40px_40px]"></div>

                        {/* Radar Scan Effect */}
                        <div className="absolute inset-0 rounded-full border-[1px] border-emerald-500/20 animate-[ping_3s_linear_infinite]"></div>
                        <div className="absolute inset-0 rounded-full border-[1px] border-emerald-500/10 animate-[ping_3s_linear_infinite_1.5s]"></div>

                        {/* Rotating Radar Line */}
                        <div className="absolute inset-0 animate-[spin_4s_linear_infinite] origin-center">
                            <div className="w-1/2 h-full bg-gradient-to-l from-emerald-500/10 to-transparent absolute right-1/2 top-0" style={{ clipPath: 'polygon(100% 0, 0 50%, 100% 100%)' }}></div>
                        </div>

                        {/* Threats */}
                        {threats.map((t) => (
                            <motion.div
                                key={t.id}
                                initial={{ scale: 0, opacity: 1 }}
                                animate={{ scale: [1, 2], opacity: 0 }}
                                transition={{ duration: 2 }}
                                className="absolute w-4 h-4 -ml-2 -mt-2"
                                style={{ left: `${t.x}%`, top: `${t.y}%` }}
                            >
                                {t.type === 'block' ? (
                                    <div className="w-full h-full bg-red-500 rounded-full shadow-[0_0_10px_rgba(239,68,68,0.8)]"></div>
                                ) : (
                                    <div className="w-full h-full bg-emerald-500 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.8)]"></div>
                                )}
                            </motion.div>
                        ))}

                        {/* Central Hub */}
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
                            <div className="relative">
                                <div className="absolute inset-0 bg-emerald-500 blur-xl opacity-20 animate-pulse"></div>
                                <Globe className="w-16 h-16 text-slate-700 relative z-10" />
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </section>
    );
}
