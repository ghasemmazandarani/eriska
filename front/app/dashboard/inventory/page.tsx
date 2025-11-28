"use client";

import { useEffect, useState } from "react";
import { DataTable } from "@/components/dashboard/DataTable";
import { columns } from "./columns";
import api from "@/lib/api";

export default function InventoryPage() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDevices = async () => {
            try {
                const response = await api.get("/devices/");
                // Map backend data to frontend model if needed
                const mappedData = response.data.map((device: any) => ({
                    id: device.id,
                    name: device.hostname || "Unknown",
                    ip: device.ip_address,
                    type: device.device_type,
                    vendor: device.vendor || "Unknown",
                    riskScore: device.risk_score,
                    status: "online", // Mock status for now
                    lastSeen: device.last_seen
                }));
                setData(mappedData);
            } catch (error) {
                console.error("Failed to fetch devices", error);
            } finally {
                setLoading(false);
            }
        };

        fetchDevices();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full min-h-[400px]">
                <div className="text-emerald-500 animate-pulse">در حال بارگذاری دستگاه‌ها...</div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-white">لیست دستگاه‌ها</h1>
                    <p className="text-slate-400 mt-1">مدیریت و مشاهده تمام دستگاه‌های شناسایی شده در شبکه.</p>
                </div>
                <div className="flex gap-3">
                    <button className="bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-lg font-medium transition-colors">
                        خروجی اکسل
                    </button>
                </div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                <DataTable columns={columns} data={data} />
            </div>
        </div>
    );
}
