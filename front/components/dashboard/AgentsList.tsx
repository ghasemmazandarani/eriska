"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Server, Wifi, WifiOff, Clock } from "lucide-react";
import api from "@/lib/api";
import { formatDistanceToNow } from "date-fns";
import { faIR } from "date-fns/locale";

interface Agent {
    id: number;
    name: string;
    last_seen: string;
    is_online: boolean;
}

export default function AgentsList() {
    const [agents, setAgents] = useState<Agent[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAgents = async () => {
            try {
                const response = await api.get("/agents/");
                const mappedAgents = response.data.map((agent: any) => ({
                    id: agent.id,
                    name: agent.name,
                    last_seen: agent.last_seen,
                    is_online: new Date(agent.last_seen).getTime() > Date.now() - 5 * 60 * 1000 // 5 mins timeout
                }));
                setAgents(mappedAgents);
            } catch (error) {
                console.error("Failed to fetch agents", error);
            } finally {
                setLoading(false);
            }
        };

        fetchAgents();
    }, []);

    if (loading) {
        return <div className="animate-pulse h-20 bg-slate-800/50 rounded-lg"></div>;
    }

    if (agents.length === 0) {
        return (
            <div className="text-center p-6 border border-dashed border-slate-700 rounded-lg bg-slate-800/30">
                <Server className="w-8 h-8 text-slate-500 mx-auto mb-2" />
                <p className="text-slate-400 text-sm">هیچ ایجنتی متصل نیست.</p>
            </div>
        );
    }

    return (
        <div className="space-y-3">
            {agents.map((agent) => (
                <motion.div
                    key={agent.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="flex items-center justify-between p-3 bg-slate-800/50 border border-slate-700/50 rounded-lg hover:border-slate-600 transition-colors"
                >
                    <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${agent.is_online ? "bg-emerald-500 animate-pulse" : "bg-slate-500"}`} />
                        <div>
                            <h4 className="text-sm font-medium text-white">{agent.name}</h4>
                            <div className="flex items-center gap-1 text-xs text-slate-400">
                                <Clock className="w-3 h-3" />
                                <span dir="ltr">
                                    {agent.last_seen
                                        ? formatDistanceToNow(new Date(agent.last_seen), { addSuffix: true, locale: faIR })
                                        : "هنوز متصل نشده"
                                    }
                                </span>
                            </div>
                        </div>
                    </div>
                    {
                        agent.is_online ? (
                            <Wifi className="w-4 h-4 text-emerald-500" />
                        ) : (
                            <WifiOff className="w-4 h-4 text-slate-500" />
                        )
                    }
                </motion.div>
            ))
            }
        </div >
    );
}
