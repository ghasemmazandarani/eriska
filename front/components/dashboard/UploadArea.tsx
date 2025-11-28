import { UploadCloud, FileJson } from 'lucide-react';
import { useCallback } from 'react';

interface UploadAreaProps {
    onUpload: (data: any) => void;
}

export default function UploadArea({ onUpload }: UploadAreaProps) {
    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const json = JSON.parse(e.target?.result as string);
                onUpload(json);
            } catch (error) {
                alert('فایل JSON نامعتبر است.');
            }
        };
        reader.readAsText(file);
    };

    return (
        <div className="flex flex-col items-center justify-center h-[60vh]">
            <div className="glass-card p-12 rounded-3xl border-2 border-dashed border-slate-700 hover:border-emerald-500/50 transition-all text-center max-w-2xl w-full group">
                <div className="w-24 h-24 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                    <UploadCloud className="w-12 h-12 text-emerald-500" />
                </div>
                <h2 className="text-3xl font-bold mb-4">آپلود گزارش امنیتی</h2>
                <p className="text-slate-400 mb-8">
                    فایل <code className="bg-slate-800 px-2 py-1 rounded text-emerald-400 font-mono">eriska_report.json</code> خود را اینجا رها کنید یا انتخاب کنید.
                </p>

                <label className="cursor-pointer bg-emerald-500 hover:bg-emerald-600 text-white px-8 py-3 rounded-xl font-bold transition-colors inline-flex items-center gap-2">
                    <FileJson className="w-5 h-5" />
                    انتخاب فایل JSON
                    <input type="file" accept=".json" onChange={handleFileChange} className="hidden" />
                </label>

                <p className="text-xs text-slate-500 mt-6">
                    پردازش به صورت Local انجام می‌شود. هیچ داده‌ای به سرور ارسال نمی‌شود.
                </p>
            </div>
        </div>
    );
}
