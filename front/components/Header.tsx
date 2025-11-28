import { PlayCircle } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';

export default function Header() {
    return (
        <nav className="glass-card sticky top-4 mx-4 md:mx-12 rounded-2xl px-6 py-4 flex justify-between items-center z-50 mt-4">
            <div className="flex items-center gap-3">
                <div className="bg-emerald-500/20 p-2 rounded-lg">
                    <Image src="/eriskalogo.png" alt="Eriska Logo" width={32} height={32} className="w-8 h-8" />
                </div>
                <span className="text-2xl font-bold tracking-tight neon-text">Eriska</span>
            </div>
            <div className="hidden md:flex gap-8 text-slate-300 font-medium">
                <a href="/dashboard" className="hover:text-emerald-500 transition-colors">داشبورد</a>
                <a href="/#features" className="hover:text-emerald-500 transition-colors">ویژگی‌ها</a>
                <a href="/#use-cases" className="hover:text-emerald-500 transition-colors">کاربردها</a>
            </div>
            <div className="flex items-center gap-4">
                <Link href="/login" className="text-slate-300 hover:text-white font-medium transition-colors">
                    ورود
                </Link>
                <Link href="/login" className="bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-2 rounded-xl font-bold shadow-lg shadow-emerald-500/30 transition-all transform hover:scale-105 flex items-center gap-2">
                    ثبت‌نام
                </Link>
            </div>
        </nav>
    );
}
