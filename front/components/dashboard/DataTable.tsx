"use client";

import {
    ColumnDef,
    flexRender,
    getCoreRowModel,
    getPaginationRowModel,
    getSortedRowModel,
    getFilteredRowModel,
    SortingState,
    ColumnFiltersState,
    useReactTable,
} from "@tanstack/react-table";
import { useState } from "react";
import { ChevronLeft, ChevronRight, Search } from "lucide-react";

interface DataTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[];
    data: TData[];
}

export function DataTable<TData, TValue>({
    columns,
    data,
}: DataTableProps<TData, TValue>) {
    const [sorting, setSorting] = useState<SortingState>([]);
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
    const [rowSelection, setRowSelection] = useState({});

    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        onSortingChange: setSorting,
        getSortedRowModel: getSortedRowModel(),
        onColumnFiltersChange: setColumnFilters,
        getFilteredRowModel: getFilteredRowModel(),
        onRowSelectionChange: setRowSelection,
        state: {
            sorting,
            columnFilters,
            rowSelection,
        },
    });

    return (
        <div className="space-y-4">
            {/* Toolbar */}
            <div className="flex items-center justify-between">
                <div className="relative max-w-sm w-full">
                    <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <input
                        placeholder="فیلتر دستگاه‌ها..."
                        value={(table.getColumn("name")?.getFilterValue() as string) ?? ""}
                        onChange={(event) =>
                            table.getColumn("name")?.setFilterValue(event.target.value)
                        }
                        className="w-full bg-slate-900 border border-slate-800 rounded-lg pr-10 pl-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/50 text-right"
                    />
                </div>
                <div className="flex items-center gap-2">
                    <button className="px-3 py-2 bg-slate-800 text-slate-300 rounded-lg text-sm hover:bg-slate-700 transition-colors">
                        ستون‌ها
                    </button>
                    <button className="px-3 py-2 bg-slate-800 text-slate-300 rounded-lg text-sm hover:bg-slate-700 transition-colors">
                        خروجی
                    </button>
                </div>
            </div>

            {/* Table */}
            <div className="rounded-xl border border-slate-800 overflow-hidden bg-slate-900/50">
                <table className="w-full text-sm text-right">
                    <thead className="bg-slate-900 text-slate-400 uppercase font-medium border-b border-slate-800">
                        {table.getHeaderGroups().map((headerGroup) => (
                            <tr key={headerGroup.id}>
                                {headerGroup.headers.map((header) => {
                                    return (
                                        <th key={header.id} className="px-6 py-4 text-right">
                                            {header.isPlaceholder
                                                ? null
                                                : flexRender(
                                                    header.column.columnDef.header,
                                                    header.getContext()
                                                )}
                                        </th>
                                    );
                                })}
                            </tr>
                        ))}
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                        {table.getRowModel().rows?.length ? (
                            table.getRowModel().rows.map((row) => (
                                <tr
                                    key={row.id}
                                    data-state={row.getIsSelected() && "selected"}
                                    className="hover:bg-slate-800/50 transition-colors"
                                >
                                    {row.getVisibleCells().map((cell) => (
                                        <td key={cell.id} className="px-6 py-4">
                                            {flexRender(
                                                cell.column.columnDef.cell,
                                                cell.getContext()
                                            )}
                                        </td>
                                    ))}
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan={columns.length} className="h-24 text-center text-slate-500">
                                    نتیجه‌ای یافت نشد.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between px-2">
                <div className="text-sm text-slate-500">
                    {table.getFilteredSelectedRowModel().rows.length} از{" "}
                    {table.getFilteredRowModel().rows.length} ردیف انتخاب شده.
                </div>
                <div className="flex items-center space-x-2">
                    <button
                        className="p-2 border border-slate-800 rounded-lg disabled:opacity-50 hover:bg-slate-800 text-slate-300"
                        onClick={() => table.previousPage()}
                        disabled={!table.getCanPreviousPage()}
                    >
                        <ChevronRight className="w-4 h-4" />
                    </button>
                    <button
                        className="p-2 border border-slate-800 rounded-lg disabled:opacity-50 hover:bg-slate-800 text-slate-300"
                        onClick={() => table.nextPage()}
                        disabled={!table.getCanNextPage()}
                    >
                        <ChevronLeft className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </div>
    );
}
