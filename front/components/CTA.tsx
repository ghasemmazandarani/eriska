import { Download } from 'lucide-react';
import Link from 'next/link';

export default function CTA() {
    return (
        <section className="container mx-auto px-4 py-32 relative z-10">
            <div className="glass-card p-12 md:p-20 rounded-[3rem] text-center bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-900/20 border border-slate-700 relative overflow-hidden group">

                {/* Animated Background */}
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>
                <div className="absolute -top-24 -left-24 w-96 h-96 bg-emerald-500/20 rounded-full blur-[100px] group-hover:bg-emerald-500/30 transition-colors duration-700"></div>
                <div className="absolute -bottom-24 -right-24 w-96 h-96 bg-blue-500/20 rounded-full blur-[100px] group-hover:bg-blue-500/30 transition-colors duration-700"></div>

                <div className="relative z-10 max-w-4xl mx-auto space-y-8">
                    <h2 className="text-4xl md:text-6xl font-black leading-tight">
                        امنیت تمام دستگاه‌ها. <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-blue-500">همین حالا.</span>
                    </h2>

                    <p className="text-slate-300 text-xl leading-relaxed max-w-2xl mx-auto">
                        بدون نیاز به سخت‌افزار اضافه. فقط دانلود کنید و شبکه خود را در برابر تهدیدات مدرن ایمن کنید. اولین اسکن شما کاملاً رایگان است.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-6 justify-center pt-4">
                        <Link href="/login" className="bg-emerald-500 hover:bg-emerald-600 text-white px-12 py-5 rounded-2xl font-bold text-xl shadow-2xl shadow-emerald-500/40 transition-all transform hover:-translate-y-1 hover:scale-105 flex items-center justify-center gap-3">
                            <Download className="w-6 h-6" />
                            شروع رایگان
                        </Link>
                    </div>

                    <p className="text-slate-500 text-sm pt-4">
                        بدون نیاز به کارت اعتباری • نصب آسان در ۳ دقیقه • لغو در هر زمان
                    </p>
                </div>
            </div>
        </section>
    );
}
