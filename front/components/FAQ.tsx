import { ChevronDown } from 'lucide-react';

export default function FAQ() {
    const faqs = [
        { q: "آیا اریسکا امن است؟", a: "بله، اریسکا فقط شبکه داخلی شما را اسکن می‌کند و هیچ داده‌ای را به خارج از شبکه نمی‌فرستد (Local-First)." },
        { q: "آیا نیاز به نصب سخت‌افزار دارم؟", a: "خیر، اریسکا یک نرم‌افزار است که روی ویندوز، لینوکس یا مک نصب می‌شود." },
        { q: "چه دستگاه‌هایی پشتیبانی می‌شوند؟", a: "تمام دستگاه‌های متصل به شبکه IP شامل دوربین‌ها، روترها، پرینترها و تجهیزات IoT." },
        { q: "تفاوت نسخه رایگان و حرفه‌ای چیست؟", a: "نسخه رایگان برای استفاده شخصی و شبکه‌های کوچک است. نسخه حرفه‌ای امکانات گزارش‌دهی و دیتابیس کامل‌تری دارد." },
    ];

    return (
        <section className="container mx-auto px-4 py-20 relative z-10 max-w-3xl">
            <div className="text-center mb-12">
                <h2 className="text-3xl font-black mb-4">سوالات متداول</h2>
            </div>

            <div className="space-y-4">
                {faqs.map((f, i) => (
                    <div key={i} className="glass-card p-6 rounded-xl cursor-pointer hover:bg-slate-800/50 transition-colors">
                        <div className="flex justify-between items-center font-bold text-lg mb-2">
                            {f.q}
                            <ChevronDown className="w-5 h-5 text-slate-500" />
                        </div>
                        <p className="text-slate-400 text-sm">{f.a}</p>
                    </div>
                ))}
            </div>
        </section>
    );
}
