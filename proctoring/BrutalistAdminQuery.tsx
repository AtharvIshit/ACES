import React, { useEffect, useState } from 'react';
import { getAllLogs, VACUUM } from './db';

export const BrutalistAdminQuery = () => {
    const [logs, setLogs] = useState<any[]>([]);
    const [isRefreshing, setIsRefreshing] = useState(false);

    const refreshLogs = () => {
        setIsRefreshing(true);
        const data = getAllLogs();
        setLogs(data);
        setTimeout(() => setIsRefreshing(false), 300);
    };

    useEffect(() => {
        refreshLogs();
        const interval = setInterval(refreshLogs, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleVacuum = () => {
        VACUUM();
        alert("VACUUM command executed.");
    };

    return (
        <div className="w-full min-h-screen bg-[#F5F5F5] font-['JetBrains_Mono'] p-12 text-[#000000]" style={{ backgroundImage: 'radial-gradient(#D1D1D1 1px, transparent 1px)', backgroundSize: '16px 16px' }}>
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-end mb-8 bg-[#FFFFFF] p-6 border-[1px] border-[#000000] shadow-[8px_8px_0px_0px_#000000]">
                    <div>
                        <h1 className="text-3xl font-black tracking-widest uppercase border-b-2 border-[#000000] pb-2 inline-block">
                            EVIDENCE_TAPE.LOG //
                        </h1>
                        <p className="mt-2 text-[10px] uppercase tracking-[2px] font-bold">SYSTEM BUILD: v3.14.ACTUAL</p>
                    </div>
                    <div className="space-x-4">
                        <button onClick={handleVacuum} className="px-6 py-2 border-[1px] border-[#000000] bg-[#FFFFFF] hover:bg-[#000000] hover:text-[#FFFFFF] font-bold text-xs transition-colors uppercase tracking-[2px]">
                            [VACUUM_DB]
                        </button>
                        <button onClick={refreshLogs} className="px-6 py-2 bg-[#000000] text-[#FFFFFF] hover:bg-[#FF0037] font-bold text-xs transition-colors uppercase tracking-[2px] shadow-[4px_4px_0px_0px_rgba(0,0,0,0.5)]">
                            {isRefreshing ? "SYNCING..." : "[SYNC_NOW]"}
                        </button>
                    </div>
                </div>

                <div className="bg-[#FFFFFF] border-[1px] border-[#000000] shadow-[8px_8px_0px_0px_#000000] overflow-hidden">
                    <table className="w-full text-left text-[10px] tracking-[1px] uppercase border-collapse">
                        <thead className="bg-[#000000] text-[#FFFFFF] font-bold">
                            <tr>
                                <th className="p-4 border-b-[1px] border-[#000000] w-24">[TIMESTAMP]</th>
                                <th className="p-4 border-b-[1px] border-l-[1px] border-[#FFFFFF]">[TYPE]</th>
                                <th className="p-4 border-b-[1px] border-l-[1px] border-[#FFFFFF] w-32">[CONFIDENCE]</th>
                                <th className="p-4 border-b-[1px] border-l-[1px] border-[#FFFFFF] w-48">[ACTION]</th>
                            </tr>
                        </thead>
                        <tbody>
                            {logs.length === 0 ? (
                                <tr>
                                    <td colSpan={4} className="p-12 text-center bg-[#F5F5F5] font-bold border-b border-[#000000] uppercase text-[#000000]">
                                        [NO_ANOMALIES_DETECTED]
                                    </td>
                                </tr>
                            ) : logs.map((log, idx) => (
                                <tr
                                    key={log.id}
                                    className={`
                                        ${idx % 2 === 0 ? 'bg-[#FFFFFF]' : 'bg-[#F5F5F5]'} 
                                        border-b-[1px] border-[#000000] 
                                        hover:border-[#FF0037] hover:border-b-[2px] hover:-translate-y-[1px]
                                        transition-all duration-75
                                    `}
                                >
                                    <td className="p-4 border-r-[1px] border-[#000000] font-bold font-mono align-top text-[9px] text-[#000000]">
                                        {new Date(log.system_timestamp).toISOString().replace('T', '\n').replace('Z', '')}
                                    </td>
                                    <td className="p-4 border-r-[1px] border-[#000000] font-bold text-[#FF0037] align-top">
                                        <div className="mb-2">{">>"} {log.violation_type}</div>
                                        <div className="text-[8px] text-[#000000] opacity-60">ID: {log.candidate_id}</div>
                                        <div className="text-[8px] text-[#000000] opacity-60 truncate max-w-[120px]" title={log.session_id}>UUID: {log.session_id}</div>
                                    </td>
                                    <td className="p-4 border-r-[1px] border-[#000000] font-mono font-bold align-top">
                                        [{(log.confidence_score * 100).toFixed(2)}%]
                                    </td>
                                    <td className="p-4 align-top w-64 text-center">
                                        <div className="flex flex-col items-center gap-2">
                                            {log.snapshot_blob ? (
                                                <div className="w-24 border border-[#000000] bg-[#000000] p-[1px]">
                                                    <img
                                                        src={log.snapshot_blob}
                                                        alt="evidence"
                                                        className="w-full h-auto filter grayscale contrast-125 hover:scale-[2.5] hover:z-50 transform transition-transform cursor-crosshair origin-right"
                                                    />
                                                </div>
                                            ) : <span className="text-[8px]">[AWAITING_BLOB]</span>}
                                            <button className="rounded-full px-6 py-1.5 bg-[#000000] text-[#FFFFFF] font-bold hover:bg-[#FF0037] transition-colors border border-[#000000]">
                                                [REVIEW]
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};
