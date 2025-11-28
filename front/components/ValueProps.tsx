import { Search, Fingerprint, ShieldAlert } from 'lucide-react';

export default function ValueProps() {
    const values = [
        {
            icon: <Search className="w-8 h-8" />,
            title: "کشف کامل دستگاه‌ها",
            desc: "شناسایی فوری روترها، دوربین‌ها، NVRها و دستگاه‌های سایه (Shadow IoT) در شبکه شما.",
            color: "blue"
        },
        {
            icon: <Fingerprint className="w-8 h-8" />,
            title: "فینگرپرینت دقیق",
            desc: "تشخیص برند، مدل، پروتکل‌ها و الگوهای رفتاری با استفاده از تکنیک‌های ترکیبی فعال و غیرفعال.",
            color: "emerald"
        },
        {
            icon: <ShieldAlert className="w-8 h-8" />,
            title: "امتیازدهی خودکار ریسک",
            desc: "تطبیق آسیب‌پذیری‌ها (CVE)، محاسبه سطح نفوذ و ارائه راهکارهای امنیتی فوری.",
            color: "red"
        }
    ];

    return (
        <section className="container mx-auto px-4 py-20 relative z-10">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {values.map((v, i) => (
                    <div key={i} className={`glass-card p-8 rounded-3xl hover:-translate-y-2 transition-all duration-300 group border border-slate-700/50 hover:border-${v.color}-500/30`}>
                        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-6 text-${v.color}-400 bg-${v.color}-500/10 group-hover:bg-${v.color}-500/20 transition-colors`}>
                            {v.icon}
                        </div>
                        <h3 className="text-xl font-bold mb-4 text-slate-100 group-hover:text-white transition-colors">{v.title}</h3>
                        <p className="text-slate-400 text-sm leading-relaxed group-hover:text-slate-300 transition-colors">
                            {v.desc}
                        </p>
                    </div>
                ))}
            </div>
        </section>
    );
}
