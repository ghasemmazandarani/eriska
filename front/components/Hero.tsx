import { Download, Github, Shield, Activity } from 'lucide-react';
import Link from 'next/link';
import TerminalDemo from './TerminalDemo';

export default function Hero() {
    return (
        <section className="container mx-auto px-4 py-24 flex flex-col md:flex-row items-center gap-16 relative z-10">
            {/* Text Content */}
            <div className="flex-1 text-center md:text-right space-y-8">
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-medium animate-fade-in-up">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    نسل جدید امنیت سایبری
                </div>

                <h1 className="text-4xl md:text-6xl font-black leading-tight tracking-tight">
                    اریسکا: نگهبان هوشمند<br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-400 to-blue-500">
                        دنیای اینترنت اشیاء
                    </span>
                </h1>

                <p className="text-lg text-slate-400 leading-relaxed max-w-2xl mx-auto md:mx-0 font-light">
                    با قدرت هوش مصنوعی، تمام دستگاه‌های متصل به شبکه خود را شناسایی کنید، آسیب‌پذیری‌ها را قبل از وقوع حادثه بیابید و امنیت خانه یا محل کار خود را تضمین کنید.
                </p>

                <div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start pt-4">
                    <Link href="/login" className="group bg-gradient-to-r from-emerald-500 to-teal-600 text-white px-8 py-3 rounded-2xl font-bold text-lg shadow-xl shadow-emerald-500/20 hover:shadow-emerald-500/40 transition-all transform hover:-translate-y-1 hover:scale-105 flex items-center justify-center gap-3">
                        <Activity className="w-5 h-5 group-hover:animate-pulse" />
                        شروع کنید
                    </Link>
                    <a href="https://github.com/ghasemmazandarani/eriska" target="_blank" rel="noopener noreferrer" className="glass-card hover:bg-slate-800/80 text-white px-8 py-3 rounded-2xl font-bold text-lg transition-all flex items-center justify-center gap-3 border border-slate-700 hover:border-emerald-500/50">
                        <Github className="w-5 h-5" />
                        مستندات گیت‌هاب
                    </a>
                </div>
            </div>

            {/* Visual/Terminal Demo */}
            <div className="flex-1 w-full max-w-lg relative">
                <div className="absolute -inset-1 bg-gradient-to-r from-emerald-500 to-blue-600 rounded-[2rem] blur opacity-30 animate-pulse"></div>
                <div className="relative">
                    <TerminalDemo />
                </div>
            </div>
        </section>
    );
}
