import { Github, Twitter, Linkedin, ShieldCheck, Mail, MapPin } from 'lucide-react';

export default function Footer() {
    return (
        <footer className="border-t border-slate-800 mt-auto bg-slate-950 pt-20 pb-10 relative overflow-hidden">
            {/* Background Pattern */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>

            <div className="container mx-auto px-4 relative z-10">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
                    <div className="space-y-6">
                        <div className="flex items-center gap-3">
                            <div className="bg-emerald-500/10 p-2 rounded-lg border border-emerald-500/20">
                                <ShieldCheck className="text-emerald-500 w-8 h-8" />
                            </div>
                            <span className="text-2xl font-bold text-slate-100">Eriska</span>
                        </div>
                        <p className="text-slate-400 text-sm leading-relaxed">
                            امنیت هوشمند برای دنیای متصل. ما با استفاده از تکنولوژی‌های پیشرفته، امنیت شبکه IoT شما را تضمین می‌کنیم.
                        </p>
                        <div className="flex gap-4">
                            <a href="#" className="bg-slate-900 p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-all"><Github className="w-5 h-5" /></a>
                            <a href="#" className="bg-slate-900 p-2 rounded-lg text-slate-400 hover:text-blue-400 hover:bg-slate-800 transition-all"><Twitter className="w-5 h-5" /></a>
                            <a href="#" className="bg-slate-900 p-2 rounded-lg text-slate-400 hover:text-blue-600 hover:bg-slate-800 transition-all"><Linkedin className="w-5 h-5" /></a>
                        </div>
                    </div>

                    <div>
                        <h4 className="font-bold text-white mb-6">محصول</h4>
                        <ul className="space-y-3 text-sm text-slate-400">
                            <li><a href="#" className="hover:text-emerald-400 transition-colors">ویژگی‌ها</a></li>
                            <li><a href="#" className="hover:text-emerald-400 transition-colors">قیمت‌گذاری</a></li>
                            <li><a href="#" className="hover:text-emerald-400 transition-colors">دانلود نسخه ویندوز</a></li>
                            <li><a href="#" className="hover:text-emerald-400 transition-colors">داشبورد آنلاین</a></li>
                            <li><a href="#" className="hover:text-emerald-400 transition-colors">مستندات API</a></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-bold text-white mb-6">شرکت</h4>
                        <ul className="space-y-3 text-sm text-slate-400">
                            <li><a href="#" className="hover:text-emerald-400 transition-colors">درباره ما</a></li>
                            <li><a href="#" className="hover:text-emerald-400 transition-colors">وبلاگ امنیتی</a></li>
                            <li><a href="#" className="hover:text-emerald-400 transition-colors">فرصت‌های شغلی</a></li>
                            <li><a href="#" className="hover:text-emerald-400 transition-colors">شرکای تجاری</a></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-bold text-white mb-6">تماس</h4>
                        <ul className="space-y-4 text-sm text-slate-400">
                            <li className="flex items-center gap-3"><Mail className="w-4 h-4 text-emerald-500" /> support@eriska.security</li>
                            <li className="flex items-center gap-3"><MapPin className="w-4 h-4 text-emerald-500" /> تهران، پارک فناوری پردیس</li>
                        </ul>
                    </div>
                </div>

                <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-slate-500">
                    <div>
                        © ۲۰۲۵ پروژه اریسکا. تمامی حقوق محفوظ است.
                    </div>
                    <div className="flex gap-6">
                        <a href="#" className="hover:text-slate-300 transition-colors">حریم خصوصی</a>
                        <a href="#" className="hover:text-slate-300 transition-colors">شرایط استفاده</a>
                        <a href="#" className="hover:text-slate-300 transition-colors">امنیت</a>
                    </div>
                </div>
            </div>
        </footer>
    );
}
