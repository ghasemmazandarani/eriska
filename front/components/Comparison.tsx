import { Check, X, Minus } from 'lucide-react';

export default function Comparison() {
    return (
        <section className="container mx-auto px-4 py-24 relative z-10">
            <div className="text-center mb-16">
                <h2 className="text-3xl md:text-5xl font-black mb-6">چرا اریسکا؟</h2>
                <p className="text-slate-400 text-lg">مقایسه با روش‌های سنتی</p>
            </div>

            <div className="overflow-x-auto rounded-3xl border border-slate-700 shadow-2xl">
                <table className="w-full text-right border-collapse bg-slate-900/80 backdrop-blur">
                    <thead>
                        <tr className="border-b border-slate-700 bg-slate-800/50">
                            <th className="p-6 text-slate-400 font-normal text-lg">قابلیت</th>
                            <th className="p-6 text-emerald-400 font-bold text-xl bg-emerald-500/10 border-t-4 border-emerald-500">Eriska</th>
                            <th className="p-6 text-slate-300 font-bold text-lg">Nmap</th>
                            <th className="p-6 text-slate-300 font-bold text-lg">Shodan</th>
                        </tr>
                    </thead>
                    <tbody className="text-slate-300">
                        {[
                            { name: "فینگرپرینت تخصصی IoT", eriska: true, nmap: "partial", shodan: true },
                            { name: "تحلیل ریسک خودکار", eriska: true, nmap: false, shodan: "partial" },
                            { name: "حریم خصوصی (Local Only)", eriska: true, nmap: true, shodan: false },
                            { name: "رابط کاربری مدرن", eriska: true, nmap: false, shodan: true },
                            { name: "پیشنهاد اصلاح (Remediation)", eriska: true, nmap: false, shodan: false },
                        ].map((row, i) => (
                            <tr key={i} className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors">
                                <td className="p-6 font-medium">{row.name}</td>
                                <td className="p-6 bg-emerald-500/5 text-emerald-500 border-x border-slate-800/50">
                                    <div className="flex items-center gap-2 font-bold"><Check className="w-6 h-6" /> بله</div>
                                </td>
                                <td className="p-6 text-slate-500">
                                    {row.nmap === true ? <Check className="w-6 h-6 text-emerald-500" /> : row.nmap === "partial" ? <Minus className="w-6 h-6" /> : <X className="w-6 h-6 text-red-500" />}
                                </td>
                                <td className="p-6 text-slate-500">
                                    {row.shodan === true ? <Check className="w-6 h-6 text-emerald-500" /> : row.shodan === "partial" ? <Minus className="w-6 h-6" /> : <X className="w-6 h-6 text-red-500" />}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </section>
    );
}
