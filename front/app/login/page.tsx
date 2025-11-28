"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import { ShieldCheck, User, Lock, Mail, ArrowRight, Loader2, Eye, EyeOff, Check, X, AlertTriangle } from "lucide-react";
import { useAuthStore } from "@/services/auth";
import { cn } from "@/lib/utils";

export default function LoginPage() {
    const router = useRouter();
    const { login, register, isLoading } = useAuthStore();
    const [activeTab, setActiveTab] = useState<"login" | "register">("login");
    const [error, setError] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [passwordStrength, setPasswordStrength] = useState(0);

    const [formData, setFormData] = useState({
        username: "",
        email: "",
        password: "",
        confirmPassword: "",
        first_name: "",
        last_name: "",
    });

    // Password Strength Calculation
    useEffect(() => {
        if (!formData.password) {
            setPasswordStrength(0);
            return;
        }
        let strength = 0;
        if (formData.password.length >= 8) strength += 25;
        if (/[A-Z]/.test(formData.password)) strength += 25;
        if (/[0-9]/.test(formData.password)) strength += 25;
        if (/[^A-Za-z0-9]/.test(formData.password)) strength += 25;
        setPasswordStrength(strength);
    }, [formData.password]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        if (activeTab === "register") {
            if (formData.password !== formData.confirmPassword) {
                setError("رمز عبور و تکرار آن مطابقت ندارند.");
                return;
            }
            if (passwordStrength < 50) {
                setError("رمز عبور باید قوی‌تر باشد (حداقل ۸ کاراکتر، شامل حروف بزرگ و عدد).");
                return;
            }
        }

        try {
            if (activeTab === "login") {
                await login({ username: formData.username, password: formData.password });
            } else {
                await register({
                    username: formData.username,
                    email: formData.email,
                    password: formData.password,
                    first_name: formData.first_name,
                    last_name: formData.last_name
                });
            }
            router.push("/dashboard");
        } catch (err: any) {
            setError(err.response?.data?.detail || "خطایی رخ داد. لطفا دوباره تلاش کنید.");
        }
    };

    const getStrengthColor = (score: number) => {
        if (score <= 25) return "bg-red-500";
        if (score <= 50) return "bg-orange-500";
        if (score <= 75) return "bg-yellow-500";
        return "bg-emerald-500";
    };

    const getStrengthText = (score: number) => {
        if (score <= 25) return "ضعیف";
        if (score <= 50) return "متوسط";
        if (score <= 75) return "خوب";
        return "عالی";
    };

    return (
        <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black flex items-center justify-center p-4 font-sans overflow-hidden relative" dir="rtl">

            {/* Background Elements */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[120px] animate-pulse"></div>
                <div className="absolute bottom-[-10%] left-[-5%] w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[120px] animate-pulse delay-1000"></div>
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-lg relative z-10"
            >
                {/* Logo Section */}
                <div className="flex flex-col items-center mb-8">
                    <motion.div
                        whileHover={{ scale: 1.05 }}
                        className="relative w-20 h-20 mb-4"
                    >
                        <div className="absolute inset-0 bg-emerald-500 rounded-2xl blur-lg opacity-50 animate-pulse"></div>
                        <div className="relative w-full h-full bg-slate-900 rounded-2xl border border-emerald-500/30 flex items-center justify-center overflow-hidden shadow-2xl">
                            <Image src="/eriskalogo.png" alt="Eriska Logo" width={80} height={80} className="w-full h-full object-cover" />
                        </div>
                    </motion.div>
                    <h1 className="text-4xl font-black text-white tracking-tight mb-2">Eriska</h1>
                    <p className="text-slate-400 text-sm">امنیت هوشمند برای دنیای متصل</p>
                </div>

                <div className="backdrop-blur-xl bg-slate-900/60 border border-slate-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
                    {/* Top Highlight Line */}
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-emerald-500 to-transparent opacity-50"></div>

                    {/* Tabs */}
                    <div className="flex mb-8 bg-slate-950/50 p-1.5 rounded-xl border border-slate-800/50 relative">
                        <button
                            onClick={() => { setActiveTab("login"); setError(""); }}
                            className={cn(
                                "flex-1 py-2.5 text-sm font-bold rounded-lg transition-all relative z-10",
                                activeTab === "login" ? "text-white" : "text-slate-400 hover:text-slate-200"
                            )}
                        >
                            ورود
                            {activeTab === "login" && (
                                <motion.div
                                    layoutId="tab-bg"
                                    className="absolute inset-0 bg-slate-800 rounded-lg -z-10 shadow-sm"
                                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                                />
                            )}
                        </button>
                        <button
                            onClick={() => { setActiveTab("register"); setError(""); }}
                            className={cn(
                                "flex-1 py-2.5 text-sm font-bold rounded-lg transition-all relative z-10",
                                activeTab === "register" ? "text-white" : "text-slate-400 hover:text-slate-200"
                            )}
                        >
                            ثبت‌نام
                            {activeTab === "register" && (
                                <motion.div
                                    layoutId="tab-bg"
                                    className="absolute inset-0 bg-slate-800 rounded-lg -z-10 shadow-sm"
                                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                                />
                            )}
                        </button>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <AnimatePresence mode="wait">
                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: "auto" }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start gap-3"
                                >
                                    <AlertTriangle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                                    <p className="text-red-400 text-sm font-medium leading-relaxed">{error}</p>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <div className="space-y-2">
                            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mr-1">نام کاربری</label>
                            <div className="relative group">
                                <User className="absolute right-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-emerald-500 transition-colors" />
                                <input
                                    type="text"
                                    required
                                    className="w-full bg-slate-950/50 border border-slate-800 rounded-xl py-3.5 pr-11 pl-4 text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all"
                                    placeholder="نام کاربری خود را وارد کنید"
                                    value={formData.username}
                                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                />
                            </div>
                        </div>

                        <AnimatePresence>
                            {activeTab === "register" && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: "auto" }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="space-y-5 overflow-hidden"
                                >
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mr-1">نام</label>
                                            <input
                                                type="text"
                                                className="w-full bg-slate-950/50 border border-slate-800 rounded-xl py-3.5 px-4 text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all"
                                                value={formData.first_name}
                                                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mr-1">نام خانوادگی</label>
                                            <input
                                                type="text"
                                                className="w-full bg-slate-950/50 border border-slate-800 rounded-xl py-3.5 px-4 text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all"
                                                value={formData.last_name}
                                                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                                            />
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mr-1">ایمیل</label>
                                        <div className="relative group">
                                            <Mail className="absolute right-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-emerald-500 transition-colors" />
                                            <input
                                                type="email"
                                                className="w-full bg-slate-950/50 border border-slate-800 rounded-xl py-3.5 pr-11 pl-4 text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all"
                                                placeholder="example@eriska.com"
                                                value={formData.email}
                                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                            />
                                        </div>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <div className="space-y-2">
                            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mr-1">رمز عبور</label>
                            <div className="relative group">
                                <Lock className="absolute right-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-emerald-500 transition-colors" />
                                <input
                                    type={showPassword ? "text" : "password"}
                                    required
                                    className="w-full bg-slate-950/50 border border-slate-800 rounded-xl py-3.5 pr-11 pl-11 text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all"
                                    placeholder="••••••••"
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                                >
                                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>

                            {/* Password Strength Meter (Register Only) */}
                            <AnimatePresence>
                                {activeTab === "register" && formData.password && (
                                    <motion.div
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: "auto" }}
                                        exit={{ opacity: 0, height: 0 }}
                                        className="pt-2 space-y-1"
                                    >
                                        <div className="flex justify-between text-xs text-slate-400">
                                            <span>قدرت رمز عبور: <span className={cn("font-bold",
                                                passwordStrength <= 25 ? "text-red-500" :
                                                    passwordStrength <= 50 ? "text-orange-500" :
                                                        passwordStrength <= 75 ? "text-yellow-500" : "text-emerald-500"
                                            )}>{getStrengthText(passwordStrength)}</span></span>
                                            <span>{passwordStrength}%</span>
                                        </div>
                                        <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                                            <motion.div
                                                className={cn("h-full rounded-full transition-all duration-300", getStrengthColor(passwordStrength))}
                                                initial={{ width: 0 }}
                                                animate={{ width: `${passwordStrength}%` }}
                                            />
                                        </div>
                                        <ul className="text-[10px] text-slate-500 space-y-0.5 pt-1 list-disc list-inside">
                                            <li className={cn(formData.password.length >= 8 ? "text-emerald-500" : "")}>حداقل ۸ کاراکتر</li>
                                            <li className={cn(/[A-Z]/.test(formData.password) ? "text-emerald-500" : "")}>حروف بزرگ انگلیسی</li>
                                            <li className={cn(/[0-9]/.test(formData.password) ? "text-emerald-500" : "")}>اعداد</li>
                                        </ul>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>

                        <AnimatePresence>
                            {activeTab === "register" && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: "auto" }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="space-y-2"
                                >
                                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mr-1">تکرار رمز عبور</label>
                                    <div className="relative group">
                                        <Lock className="absolute right-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-emerald-500 transition-colors" />
                                        <input
                                            type="password"
                                            required
                                            className={cn(
                                                "w-full bg-slate-950/50 border rounded-xl py-3.5 pr-11 pl-4 text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 transition-all",
                                                formData.confirmPassword && formData.password !== formData.confirmPassword
                                                    ? "border-red-500/50 focus:ring-red-500/50"
                                                    : "border-slate-800 focus:ring-emerald-500/50 focus:border-emerald-500/50"
                                            )}
                                            placeholder="تکرار رمز عبور"
                                            value={formData.confirmPassword}
                                            onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                                        />
                                        {formData.confirmPassword && (
                                            <div className="absolute left-3.5 top-1/2 -translate-y-1/2">
                                                {formData.password === formData.confirmPassword ? (
                                                    <Check className="w-5 h-5 text-emerald-500" />
                                                ) : (
                                                    <X className="w-5 h-5 text-red-500" />
                                                )}
                                            </div>
                                        )}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/40 flex items-center justify-center gap-2 mt-8 disabled:opacity-50 disabled:cursor-not-allowed group relative overflow-hidden"
                        >
                            <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
                            <span className="relative flex items-center gap-2">
                                {isLoading ? (
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                ) : (
                                    <>
                                        {activeTab === "login" ? "ورود به حساب کاربری" : "ایجاد حساب کاربری"}
                                        <ArrowRight className="w-5 h-5 group-hover:translate-x-[-4px] transition-transform" />
                                    </>
                                )}
                            </span>
                        </button>
                    </form>
                </div>


            </motion.div>
        </div>
    );
}
