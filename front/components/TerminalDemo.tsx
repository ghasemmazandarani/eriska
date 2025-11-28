"use client";

import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Terminal, Shield, AlertTriangle, CheckCircle } from 'lucide-react';

export default function TerminalDemo() {
    const [lines, setLines] = useState<string[]>([]);
    const scrollRef = useRef<HTMLDivElement>(null);

    const commands = [
        { text: "eriska-agent --scan --network 192.168.1.0/24", type: "command", delay: 1000 },
        { text: "[*] Initializing Eriska Security Engine v2.4.0...", type: "info", delay: 500 },
        { text: "[+] Target network: 192.168.1.0/24", type: "success", delay: 300 },
        { text: "[*] Starting ARP discovery...", type: "info", delay: 800 },
        { text: "[+] Found device: 192.168.1.1 (Gateway/Router)", type: "success", delay: 400 },
        { text: "[+] Found device: 192.168.1.15 (Workstation-PC)", type: "success", delay: 400 },
        { text: "[!] Found device: 192.168.1.42 (Unknown IoT Device)", type: "warning", delay: 600 },
        { text: "[*] Fingerprinting device 192.168.1.42...", type: "info", delay: 1200 },
        { text: "    > OS: Linux (Embedded)", type: "detail", delay: 200 },
        { text: "    > Open Ports: 23 (Telnet), 80 (HTTP)", type: "detail", delay: 200 },
        { text: "[CRITICAL] CVE-2023-3824 detected on 192.168.1.42!", type: "error", delay: 800 },
        { text: "[*] Generating risk report...", type: "info", delay: 1000 },
        { text: "[+] Report uploaded to dashboard. Risk Score: 85/100", type: "success", delay: 500 },
        { text: "eriska-agent --monitor --background", type: "command", delay: 2000 },
        { text: "[*] Entering background monitoring mode...", type: "info", delay: 500 },
    ];

    useEffect(() => {
        let currentIndex = 0;
        let timeoutId: NodeJS.Timeout;

        const addLine = () => {
            if (currentIndex >= commands.length) {
                // Reset after a pause
                timeoutId = setTimeout(() => {
                    setLines([]);
                    currentIndex = 0;
                    addLine();
                }, 5000);
                return;
            }

            const cmd = commands[currentIndex];
            setLines(prev => [...prev, JSON.stringify(cmd)]); // Store full object as string to parse later
            currentIndex++;

            if (scrollRef.current) {
                scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
            }

            timeoutId = setTimeout(addLine, cmd.delay);
        };

        addLine();

        return () => clearTimeout(timeoutId);
    }, []);

    return (
        <div className="w-full max-w-2xl mx-auto perspective-1000">
            <motion.div
                initial={{ rotateX: 10, opacity: 0 }}
                animate={{ rotateX: 0, opacity: 1 }}
                transition={{ duration: 0.8 }}
                className="bg-[#0c0c0c] rounded-xl overflow-hidden shadow-2xl border border-slate-800 font-mono text-sm md:text-base relative group"
            >
                {/* Window Header */}
                <div className="bg-[#1a1a1a] px-4 py-3 flex items-center justify-between border-b border-slate-800">
                    <div className="flex gap-2">
                        <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
                        <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                        <div className="w-3 h-3 rounded-full bg-emerald-500/80"></div>
                    </div>
                    <div className="text-slate-500 text-xs flex items-center gap-2">
                        <Terminal className="w-3 h-3" />
                        root@eriska-agent:~
                    </div>
                    <div className="w-12"></div> {/* Spacer */}
                </div>

                {/* Terminal Content */}
                <div
                    ref={scrollRef}
                    className="p-6 h-[400px] overflow-y-auto custom-scrollbar space-y-2 font-mono"
                >
                    {lines.map((lineStr, i) => {
                        const line = JSON.parse(lineStr);
                        return (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="flex items-start gap-2 break-all"
                            >
                                {line.type === 'command' && (
                                    <span className="text-emerald-500 font-bold shrink-0">➜ ~</span>
                                )}
                                <span className={`
                                    ${line.type === 'command' ? 'text-white' : ''}
                                    ${line.type === 'info' ? 'text-blue-400' : ''}
                                    ${line.type === 'success' ? 'text-emerald-400' : ''}
                                    ${line.type === 'warning' ? 'text-yellow-400' : ''}
                                    ${line.type === 'error' ? 'text-red-500 font-bold bg-red-500/10 px-2 rounded' : ''}
                                    ${line.type === 'detail' ? 'text-slate-500' : ''}
                                `}>
                                    {line.text}
                                </span>
                            </motion.div>
                        );
                    })}
                    <motion.div
                        animate={{ opacity: [0, 1, 0] }}
                        transition={{ repeat: Infinity, duration: 0.8 }}
                        className="w-2 h-5 bg-emerald-500 inline-block align-middle ml-1"
                    />
                </div>

                {/* Glass Reflection Effect */}
                <div className="absolute inset-0 bg-gradient-to-tr from-white/5 to-transparent pointer-events-none"></div>
            </motion.div>
        </div>
    );
}
