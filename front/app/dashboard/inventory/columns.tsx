"use client";

import { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown, MoreHorizontal, ShieldAlert, ShieldCheck, Shield } from "lucide-react";
import Link from "next/link";

// This type should be shared, but defining here for now
export type Device = {
    id: string;
    name: string;
    ip: string;
    mac: string;
    vendor: string;
    type: string;
    riskScore: number;
    status: "online" | "offline";
    lastSeen: string;
};

export const columns: ColumnDef<Device>[] = [
    {
        accessorKey: "name",
        header: ({ column }) => {
            return (
                <button
                    className="flex items-center gap-1 hover:text-white transition-colors"
                    onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                >
                    نام دستگاه
                    <ArrowUpDown className="mr-2 h-4 w-4" />
                </button>
            );
        },
        cell: ({ row }) => {
            return (
                <div className="flex flex-col">
                    <span className="font-medium text-white">{row.getValue("name")}</span>
                    <span className="text-xs text-slate-500 dir-ltr text-right">{row.original.mac}</span>
                </div>
            );
        },
    },
    {
        accessorKey: "ip",
        header: "آدرس IP",
        cell: ({ row }) => <span className="font-mono text-slate-300 dir-ltr">{row.getValue("ip")}</span>,
    },
    {
        accessorKey: "type",
        header: "نوع",
        cell: ({ row }) => (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
                {row.getValue("type")}
            </span>
        ),
    },
    {
        accessorKey: "vendor",
        header: "سازنده",
    },
    {
        accessorKey: "riskScore",
        header: ({ column }) => {
            return (
                <button
                    className="flex items-center gap-1 hover:text-white transition-colors"
                    onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                >
                    امتیاز ریسک
                    <ArrowUpDown className="mr-2 h-4 w-4" />
                </button>
            );
        },
        cell: ({ row }) => {
            const score = row.getValue("riskScore") as number;
            let colorClass = "bg-emerald-500/10 text-emerald-500 border-emerald-500/20";
            if (score >= 70) colorClass = "bg-red-500/10 text-red-500 border-red-500/20";
            else if (score >= 40) colorClass = "bg-amber-500/10 text-amber-500 border-amber-500/20";

            return (
                <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold border ${colorClass}`}>
                    {score}/100
                </div>
            );
        },
    },
    {
        accessorKey: "status",
        header: "وضعیت",
        cell: ({ row }) => {
            const status = row.getValue("status") as string;
            const statusText = status === 'online' ? 'آنلاین' : 'آفلاین';
            return (
                <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${status === 'online' ? 'bg-emerald-500' : 'bg-slate-600'}`} />
                    <span className="capitalize text-slate-300">{statusText}</span>
                </div>
            );
        },
    },
    {
        id: "actions",
        cell: ({ row }) => {
            return (
                <div className="flex items-center gap-2">
                    <Link
                        href={`/dashboard/device/${row.original.id}`}
                        className="text-xs bg-slate-800 hover:bg-slate-700 text-white px-3 py-1.5 rounded-md transition-colors"
                    >
                        مشاهده جزئیات
                    </Link>
                </div>
            );
        },
    },
];
