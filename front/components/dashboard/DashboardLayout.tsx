import Sidebar from "./Sidebar";
import TopBar from "./TopBar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-emerald-500/30" dir="rtl">
            <Sidebar />
            <TopBar />
            <main className="md:pr-64 pt-16 min-h-screen">
                <div className="p-6 max-w-7xl mx-auto space-y-6">
                    {children}
                </div>
            </main>
        </div>
    );
}
