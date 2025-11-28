import { Cpu, Search, Database, AlertTriangle, Layers, Zap } from 'lucide-react';

export default function Features() {
    const features = [
        { icon: <Cpu />, title: "موتور کشف هوشمند", desc: "اسکن سریع و دقیق بدون ایجاد اختلال در شبکه.", color: "blue" },
        { icon: <Search />, title: "فینگرپرینت عمیق", desc: "شناسایی جزئیات فنی تا سطح فریم‌ور و چیپ‌ست.", color: "purple" },
        { icon: <Database />, title: "هوش CVE محلی", desc: "دیتابیس آفلاین آسیب‌پذیری‌ها برای امنیت بیشتر.", color: "emerald" },
        { icon: <AlertTriangle />, title: "امتیازدهی ریسک", desc: "محاسبه کمی میزان خطر برای اولویت‌بندی اصلاحات.", color: "red" },
        { icon: <Layers />, title: "بینش فروشنده", desc: "شناسایی دقیق سازنده و مدل دستگاه‌های ناشناس.", color: "orange" },
        { icon: <Zap />, title: "پیشنهادات فوری", desc: "ارائه راهکارهای عملی برای رفع حفره‌های امنیتی.", color: "yellow" },
    ];

    return (
        <section id="features" className="container mx-auto px-4 py-24 relative z-10">
            <div className="text-center mb-20">
                <h2 className="text-3xl md:text-5xl font-black mb-6 bg-clip-text text-transparent bg-gradient-to-r from-slate-100 to-slate-500">
                    ویژگی‌های کلیدی
                </h2>
                <p className="text-slate-400 text-lg max-w-2xl mx-auto">
                    ابزارهای قدرتمند مهندسی شده برای تیم‌های امنیتی که به دقت و سرعت نیاز دارند.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {features.map((f, i) => (
                    <div key={i} className="glass-card p-6 rounded-2xl flex items-start gap-5 hover:bg-slate-800/60 transition-all duration-300 border border-slate-800 hover:border-slate-600 group">
                        <div className={`p-3 rounded-xl bg-slate-900 border border-slate-700 text-${f.color}-400 group-hover:scale-110 transition-transform`}>
                            {f.icon}
                        </div>
                        <div>
                            <h4 className="text-lg font-bold mb-2 text-slate-200 group-hover:text-white">{f.title}</h4>
                            <p className="text-slate-400 text-sm leading-relaxed">{f.desc}</p>
                        </div>
                    </div>
                ))}
            </div>
        </section>
    );
}
