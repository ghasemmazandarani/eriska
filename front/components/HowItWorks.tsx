import { Scan, Database, Lock } from 'lucide-react';

export default function HowItWorks() {
    return (
        <section className="container mx-auto px-4 py-20 relative z-10">
            <div className="text-center mb-16">
                <h2 className="text-3xl md:text-5xl font-black mb-4">چگونه کار می‌کند؟</h2>
                <p className="text-slate-400">سه گام ساده برای امنیت کامل شبکه IoT شما</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
                {/* Connecting Line (Desktop) */}
                <div className="hidden md:block absolute top-1/2 left-0 right-0 h-1 bg-slate-800 -z-10 transform -translate-y-1/2"></div>

                {/* Step 1 */}
                <div className="glass-card p-8 rounded-2xl text-center relative bg-slate-900/80">
                    <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-6 border-4 border-slate-900 text-blue-400 text-2xl font-bold">1</div>
                    <h3 className="text-xl font-bold mb-3">اسکن شبکه</h3>
                    <p className="text-slate-400 text-sm">
                        استفاده از ARP, ONVIF, UPnP و پروب‌های HTTP برای کشف تمام دستگاه‌های متصل.
                    </p>
                </div>

                {/* Step 2 */}
                <div className="glass-card p-8 rounded-2xl text-center relative bg-slate-900/80 border-emerald-500/30">
                    <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-6 border-4 border-slate-900 text-emerald-500 text-2xl font-bold">2</div>
                    <h3 className="text-xl font-bold mb-3">شناسایی هوشمند</h3>
                    <p className="text-slate-400 text-sm">
                        ترکیب فینگرپرینت پروتکل‌ها، مک آدرس و مدل‌های یادگیری ماشین برای تشخیص دقیق دستگاه.
                    </p>
                </div>

                {/* Step 3 */}
                <div className="glass-card p-8 rounded-2xl text-center relative bg-slate-900/80">
                    <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-6 border-4 border-slate-900 text-purple-400 text-2xl font-bold">3</div>
                    <h3 className="text-xl font-bold mb-3">ارزیابی ریسک</h3>
                    <p className="text-slate-400 text-sm">
                        تطبیق با دیتابیس CVE، تشخیص پیکربندی غلط و محاسبه امتیاز نفوذپذیری.
                    </p>
                </div>
            </div>
        </section>
    );
}
