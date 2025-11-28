import { Building2, Cctv, Home, Router, Briefcase } from 'lucide-react';

export default function UseCases() {
    const cases = [
        { icon: <Building2 />, title: "امنیت سازمانی IT", desc: "کشف دستگاه‌های سایه و مدیریت دارایی‌ها." },
        { icon: <Cctv />, title: "شبکه‌های دوربین مداربسته", desc: "جلوگیری از نفوذ به NVR و دوربین‌های IP." },
        { icon: <Home />, title: "هوشمندسازی ساختمان", desc: "ایمن‌سازی خانه هوشمند و تجهیزات IoT." },
        { icon: <Router />, title: "کسب‌وکارهای کوچک", desc: "تست نفوذ سریع روترها و مودم‌ها." },
        { icon: <Briefcase />, title: "ارائه‌دهندگان سرویس (MSP)", desc: "ارائه خدمات اسکن آسیب‌پذیری به مشتریان." },
    ];

    return (
        <section id="use-cases" className="container mx-auto px-4 py-24 relative z-10">
            <div className="text-center mb-16">
                <h2 className="text-3xl md:text-5xl font-black mb-6">موارد کاربرد</h2>
                <p className="text-slate-400 text-lg">اریسکا برای چه کسانی ساخته شده است؟</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {cases.map((c, i) => (
                    <div key={i} className="glass-card p-8 rounded-2xl flex items-center gap-6 hover:bg-slate-800 transition-all border-l-4 border-transparent hover:border-emerald-500 group cursor-default">
                        <div className="bg-slate-700/50 p-4 rounded-full text-slate-300 group-hover:bg-emerald-500/20 group-hover:text-emerald-400 transition-colors">
                            {c.icon}
                        </div>
                        <div>
                            <h4 className="font-bold text-xl mb-2 text-slate-200 group-hover:text-white">{c.title}</h4>
                            <p className="text-sm text-slate-400 group-hover:text-slate-300">{c.desc}</p>
                        </div>
                    </div>
                ))}

                {/* Call to Action Card */}
                <div className="glass-card p-8 rounded-2xl flex flex-col items-center justify-center text-center bg-gradient-to-br from-emerald-900/20 to-slate-900 border border-emerald-500/30 hover:border-emerald-500/50 transition-colors">
                    <h4 className="font-bold text-xl mb-2 text-white">شما چطور؟</h4>
                    <p className="text-sm text-slate-400 mb-4">نیاز خاصی دارید؟ با ما تماس بگیرید.</p>
                    <button className="text-emerald-400 font-bold hover:text-emerald-300 text-sm">تماس با مشاوره &larr;</button>
                </div>
            </div>
        </section>
    );
}
