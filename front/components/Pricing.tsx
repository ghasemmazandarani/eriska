import { Check } from 'lucide-react';

export default function Pricing() {
    return (
        <section id="pricing" className="container mx-auto px-4 py-24 relative z-10">
            <div className="text-center mb-20">
                <h2 className="text-3xl md:text-5xl font-black mb-6">پلن‌های قیمتی</h2>
                <p className="text-slate-400 text-lg">شروع رایگان، ارتقا برای حرفه‌ای‌ها</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto items-center">
                {/* Free */}
                <div className="glass-card p-8 rounded-3xl border border-slate-700 hover:border-slate-500 transition-all">
                    <h3 className="text-xl font-bold mb-2 text-slate-200">رایگان</h3>
                    <div className="text-4xl font-black mb-6 text-white">۰ <span className="text-sm font-normal text-slate-500">تومان</span></div>
                    <p className="text-slate-400 text-sm mb-6">برای تست و شبکه‌های خانگی کوچک.</p>
                    <ul className="space-y-4 mb-8 text-slate-300 text-sm">
                        <li className="flex gap-3"><Check className="w-5 h-5 text-emerald-500" /> اسکن ۱ شبکه</li>
                        <li className="flex gap-3"><Check className="w-5 h-5 text-emerald-500" /> تا ۵۰ دستگاه</li>
                        <li className="flex gap-3"><Check className="w-5 h-5 text-emerald-500" /> گزارش HTML ساده</li>
                    </ul>
                    <button className="w-full py-3 rounded-xl border border-slate-600 hover:bg-slate-800 text-white font-bold transition-colors">دانلود رایگان</button>
                </div>

                {/* Pro */}
                <div className="glass-card p-10 rounded-[2.5rem] border-2 border-emerald-500 relative transform md:-translate-y-4 bg-slate-900 shadow-2xl shadow-emerald-500/20 z-10">
                    <div className="absolute top-0 right-1/2 translate-x-1/2 -translate-y-1/2 bg-emerald-500 text-white text-sm px-4 py-1 rounded-full font-bold shadow-lg">پیشنهاد ویژه</div>
                    <h3 className="text-2xl font-bold mb-2 text-emerald-400">حرفه‌ای</h3>
                    <div className="text-5xl font-black mb-6 text-white">۹۹۰ <span className="text-sm font-normal text-slate-500">هزار تومان / ماه</span></div>
                    <p className="text-slate-400 text-sm mb-8">برای متخصصین امنیت و شرکت‌های کوچک.</p>
                    <ul className="space-y-5 mb-10 text-slate-200">
                        <li className="flex gap-3"><Check className="w-5 h-5 text-emerald-500" /> اسکن نامحدود</li>
                        <li className="flex gap-3"><Check className="w-5 h-5 text-emerald-500" /> دیتابیس CVE کامل</li>
                        <li className="flex gap-3"><Check className="w-5 h-5 text-emerald-500" /> گزارش PDF و اکسل</li>
                        <li className="flex gap-3"><Check className="w-5 h-5 text-emerald-500" /> پشتیبانی ایمیلی اولویت‌دار</li>
                    </ul>
                    <button className="w-full py-4 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-bold text-lg shadow-lg shadow-emerald-500/30 transition-all hover:scale-105">خرید اشتراک</button>
                </div>

                {/* Enterprise */}
                <div className="glass-card p-8 rounded-3xl border border-slate-700 hover:border-purple-500/50 transition-all">
                    <h3 className="text-xl font-bold mb-2 text-purple-400">سازمانی</h3>
                    <div className="text-4xl font-black mb-6 text-white">تماس <span className="text-sm font-normal text-slate-500">بگیرید</span></div>
                    <p className="text-slate-400 text-sm mb-6">برای سازمان‌های بزرگ با نیازهای خاص.</p>
                    <ul className="space-y-4 mb-8 text-slate-300 text-sm">
                        <li className="flex gap-3"><Check className="w-5 h-5 text-purple-500" /> لایسنس نامحدود</li>
                        <li className="flex gap-3"><Check className="w-5 h-5 text-purple-500" /> API اختصاصی</li>
                        <li className="flex gap-3"><Check className="w-5 h-5 text-purple-500" /> استقرار در محل (On-Premise)</li>
                        <li className="flex gap-3"><Check className="w-5 h-5 text-purple-500" /> پشتیبانی ۲۴/۷</li>
                    </ul>
                    <button className="w-full py-3 rounded-xl border border-slate-600 hover:bg-slate-800 text-white font-bold transition-colors">تماس با فروش</button>
                </div>
            </div>
        </section>
    );
}
