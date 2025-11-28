import { Bot, Sparkles, BrainCircuit, MessageSquareCode, Cpu } from 'lucide-react';

export default function AISection() {
    return (
        <section className="container mx-auto px-4 py-32 relative z-10 overflow-hidden">
            {/* Background Glow */}
            <div className="absolute top-1/2 left-0 -translate-y-1/2 w-[500px] h-[500px] bg-indigo-600/20 rounded-full blur-[120px] -z-10"></div>

            <div className="flex flex-col lg:flex-row items-center gap-20">
                {/* Visual / Neural Network */}
                <div className="flex-1 relative w-full h-[500px] flex items-center justify-center">
                    <div className="absolute inset-0 bg-indigo-500/5 blur-3xl rounded-full animate-pulse"></div>

                    {/* Central Brain */}
                    <div className="relative z-10 bg-slate-900 p-8 rounded-full border border-indigo-500/30 shadow-[0_0_50px_rgba(99,102,241,0.3)]">
                        <BrainCircuit className="w-32 h-32 text-indigo-400" />
                    </div>

                    {/* Orbiting Nodes */}
                    <div className="absolute w-[300px] h-[300px] border border-indigo-500/20 rounded-full animate-spin-slow">
                        <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-slate-900 p-2 rounded-lg border border-indigo-500/50">
                            <Cpu className="w-6 h-6 text-indigo-400" />
                        </div>
                    </div>
                    <div className="absolute w-[450px] h-[450px] border border-indigo-500/10 rounded-full animate-spin-reverse-slow">
                        <div className="absolute bottom-1/4 right-0 bg-slate-900 p-2 rounded-lg border border-indigo-500/50">
                            <MessageSquareCode className="w-6 h-6 text-indigo-400" />
                        </div>
                    </div>

                    {/* Floating Tags */}
                    <div className="absolute top-20 right-10 bg-slate-800/80 backdrop-blur p-3 rounded-xl border border-indigo-500/30 text-xs text-indigo-200 shadow-lg animate-float">
                        Analysis Complete (99.9%)
                    </div>
                    <div className="absolute bottom-20 left-10 bg-slate-800/80 backdrop-blur p-3 rounded-xl border border-indigo-500/30 text-xs text-indigo-200 shadow-lg animate-float-delayed">
                        Pattern Detected: Mirai
                    </div>
                </div>

                {/* Text Content */}
                <div className="flex-1 space-y-10 text-right">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-sm font-medium">
                        <Sparkles className="w-4 h-4" />
                        <span>قدرت گرفته از هوش مصنوعی اریسکا</span>
                    </div>

                    <h2 className="text-4xl md:text-6xl font-black leading-tight">
                        تحلیل امنیتی با <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-l from-indigo-400 via-purple-400 to-pink-500">
                            سرعت نور
                        </span>
                    </h2>

                    <p className="text-slate-400 text-lg leading-relaxed font-light">
                        هوش مصنوعی اریسکا الگوهای پیچیده را درک می‌کند، دستگاه‌های ناشناخته را طبقه‌بندی می‌کند و راهکارهای امنیتی را به زبان ساده توضیح می‌دهد. دیگر نیازی به تحلیل دستی لاگ‌های پیچیده نیست.
                    </p>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                        <div className="bg-slate-800/40 p-6 rounded-2xl border border-slate-700 hover:border-indigo-500/50 transition-all hover:bg-slate-800/60 group">
                            <Bot className="w-10 h-10 text-indigo-400 mb-4 group-hover:scale-110 transition-transform" />
                            <h4 className="font-bold text-lg mb-2 text-slate-200">طبقه‌بندی هوشمند</h4>
                            <p className="text-sm text-slate-400">تشخیص نوع دستگاه با استفاده از مدل‌های زبانی بزرگ (LLM)</p>
                        </div>
                        <div className="bg-slate-800/40 p-6 rounded-2xl border border-slate-700 hover:border-purple-500/50 transition-all hover:bg-slate-800/60 group">
                            <MessageSquareCode className="w-10 h-10 text-purple-400 mb-4 group-hover:scale-110 transition-transform" />
                            <h4 className="font-bold text-lg mb-2 text-slate-200">توضیح ریسک</h4>
                            <p className="text-sm text-slate-400">ترجمه لاگ‌های فنی و پیچیده به زبان ساده انسانی</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
