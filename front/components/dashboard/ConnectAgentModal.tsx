"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Copy, Check, Terminal, Loader2 } from "lucide-react";
import api from "@/lib/api";

interface ConnectAgentModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function ConnectAgentModal({ isOpen, onClose }: ConnectAgentModalProps) {
    const [token, setToken] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [copied, setCopied] = useState(false);

    const generateToken = async () => {
        setLoading(true);
        try {
            const response = await api.post("/agent/generate_token/");
            setToken(response.data.token);
        } catch (error) {
            console.error("Failed to generate token", error);
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = () => {
        if (token) {
            navigator.clipboard.writeText(`python main.py --connect ${token}`);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-lg shadow-2xl overflow-hidden"
                >
                    {/* Header */}
                    <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-800/50">
                        <h3 className="text-lg font-bold text-white flex items-center gap-2">
                            <Terminal className="w-5 h-5 text-emerald-500" />
                            اتصال ایجنت جدید
                        </h3>
                        <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Body */}
                    <div className="p-6 space-y-6">
                        {!token ? (
                            <div className="text-center space-y-4">
                                <div className="bg-emerald-500/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <Terminal className="w-8 h-8 text-emerald-500" />
                                </div>
                                <p className="text-slate-300">
                                    برای اتصال ایجنت به داشبورد، باید یک کد ارتباطی یکبار مصرف تولید کنید.
                                    این کد را در ترمینال ایجنت وارد کنید.
                                </p>
                                <button
                                    onClick={generateToken}
                                    disabled={loading}
                                    className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2.5 px-6 rounded-lg transition-all shadow-lg shadow-emerald-500/20 flex items-center gap-2 mx-auto"
                                >
                                    {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : "تولید کد ارتباطی"}
                                </button>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <div className="bg-slate-950 border border-slate-800 rounded-lg p-4">
                                    <p className="text-sm text-slate-400 mb-2">دستور زیر را در ترمینال ایجنت اجرا کنید:</p>
                                    <div className="flex items-center justify-between bg-black rounded p-3 font-mono text-emerald-400 text-sm">
                                        <span>python main.py --connect {token}</span>
                                        <button
                                            onClick={copyToClipboard}
                                            className="text-slate-500 hover:text-white transition-colors"
                                        >
                                            {copied ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
                                        </button>
                                    </div>
                                </div>
                                <div className="text-xs text-slate-500 text-center">
                                    این کد تا ۱ ساعت اعتبار دارد.
                                </div>
                            </div>
                        )}
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
}
