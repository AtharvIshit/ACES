import React, { useState, useEffect, useRef } from 'react';
import { Camera, Mic, Activity, ShieldAlert, CheckCircle2, AlertCircle } from 'lucide-react';
import { useProctoring } from './useProctoring';

interface ProctoringManagerProps {
    onCriticalViolation?: () => void;
}

const PreflightModal = ({ status, onContinue }: { status: any, onContinue: () => void }) => {
    const isReady = status.camera === 'success' && status.mic === 'success' && status.worker === 'success';

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-[#F5F5F5] font-['JetBrains_Mono']" style={{ backgroundImage: 'radial-gradient(#D1D1D1 1px, transparent 1px)', backgroundSize: '16px 16px' }}>
            <div className="bg-[#FFFFFF] border border-[#000000] p-8 max-w-md w-full text-[#000000] shadow-[8px_8px_0px_0px_#000000]">
                <h2 className="text-xl font-black mb-6 flex items-center gap-2 uppercase tracking-widest border-b-2 border-[#000000] pb-2">
                    <ShieldAlert className="text-[#000000] w-6 h-6 border border-[#000000]" /> SYSTEM_PREFLIGHT //
                </h2>

                <div className="space-y-4 mb-8 text-xs font-bold tracking-widest">
                    <div className="flex items-center justify-between p-3 bg-[#FFFFFF] border border-[#000000]">
                        <div className="flex items-center gap-3">
                            <Camera className="w-5 h-5" />
                            <span>[OPTICS_SENSOR]</span>
                        </div>
                        {status.camera === 'pending' ? <span className="text-yellow-600 animate-pulse">[WAIT]</span> :
                            status.camera === 'success' ? <span className="text-[#000000]">[OK]</span> :
                                <span className="text-[#FF0037]">[ERR]</span>}
                    </div>

                    <div className="flex items-center justify-between p-3 bg-[#FFFFFF] border border-[#000000]">
                        <div className="flex items-center gap-3">
                            <Mic className="w-5 h-5" />
                            <span>[AUDIO_ARRAY]</span>
                        </div>
                        {status.mic === 'pending' ? <span className="text-yellow-600 animate-pulse">[WAIT]</span> :
                            status.mic === 'success' ? <span className="text-[#000000]">[OK]</span> :
                                <span className="text-[#FF0037]">[ERR]</span>}
                    </div>

                    <div className="flex items-center justify-between p-3 bg-[#FFFFFF] border border-[#000000]">
                        <div className="flex items-center gap-3">
                            <Activity className="w-5 h-5" />
                            <span>[TFJS_PIXEL_ENGINE]</span>
                        </div>
                        {status.worker === 'pending' ? <span className="text-yellow-600 animate-pulse">[WAIT]</span> :
                            status.worker === 'success' ? <span className="text-[#000000]">[OK]</span> :
                                <span className="text-[#FF0037]">[ERR]</span>}
                    </div>
                </div>

                <button
                    disabled={!isReady}
                    onClick={onContinue}
                    className="w-full py-3 px-4 bg-[#000000] hover:bg-[#FF0037] disabled:opacity-50 disabled:cursor-not-allowed text-[#FFFFFF] font-bold tracking-[4px] uppercase border border-[#000000] transition-colors"
                >
                    {isReady ? 'INITIALIZE_HUD' : 'LOADING_SYSTEM...'}
                </button>
            </div>
        </div>
    );
};


export const ProctoringManager: React.FC<ProctoringManagerProps> = ({
    onCriticalViolation = () => console.log('Critical violation reached! (Trust Score < 40%)')
}) => {
    const { videoRef, trustScore, isPreflightPassed, preflightStatus, isViolationActive, eyeCoords, detectedObjects } = useProctoring({ onCriticalViolation });
    const [sessionStarted, setSessionStarted] = useState(false);
    const overlayCanvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        if (!overlayCanvasRef.current || !videoRef.current) return;
        const ctx = overlayCanvasRef.current.getContext('2d');
        if (!ctx) return;

        ctx.clearRect(0, 0, overlayCanvasRef.current.width, overlayCanvasRef.current.height);

        // Note: we are drawing on a canvas that is physically mirrored over the mirrored video. 
        // x values coming from the TFJS model assume unmirrored image data (read from original video stream).
        // When we overlay over the mirrored canvas (-scale-x-100), drawing at x visually maps to width - x in actual screen pixels.

        ctx.fillStyle = '#000000';
        ctx.strokeStyle = '#000000';
        ctx.lineWidth = 1;

        // 1. Draw 1px crosshair anchors on eyes
        const drawCrosshair = (x: number, y: number) => {
            ctx.beginPath();
            // Horizontal line
            ctx.moveTo(x - 6, y);
            ctx.lineTo(x + 6, y);
            // Vertical line
            ctx.moveTo(x, y - 6);
            ctx.lineTo(x, y + 6);
            ctx.stroke();

            // Center dot
            ctx.fillRect(x - 1, y - 1, 2, 2);
        };

        if (eyeCoords) {
            drawCrosshair(eyeCoords.left.x, eyeCoords.left.y);
            drawCrosshair(eyeCoords.right.x, eyeCoords.right.y);
        }

        // 2. Draw Object Bounding Boxes ([OBJECT_ID: MOBILE_DEVICE_01])
        if (detectedObjects && detectedObjects.length > 0) {
            detectedObjects.forEach((obj, idx) => {
                if (!obj.bbox) return;
                // bbox: [x, y, width, height]
                const [bx, by, bw, bh] = obj.bbox;

                ctx.strokeStyle = '#FF0037';
                ctx.lineWidth = 1;
                ctx.strokeRect(bx, by, bw, bh);

                // Draw Technical Label above bounding box
                const label = `[OBJECT_ID: ${obj.class.replace(' ', '_').toUpperCase()}_0${idx + 1}]`;
                ctx.fillStyle = '#FF0037';
                ctx.font = '8px "JetBrains Mono", monospace';
                ctx.fillText(label, bx, by > 10 ? by - 4 : by + 10);
            });
        }

    }, [eyeCoords, detectedObjects]);

    return (
        <>
            {(!isPreflightPassed || !sessionStarted) && (
                <PreflightModal status={preflightStatus} onContinue={() => setSessionStarted(true)} />
            )}

            {/* 1px Black Rule HUD Container */}
            <div className={`relative w-full h-full z-40 bg-[#FFFFFF] flex flex-col overflow-hidden transition-all duration-300 font-['JetBrains_Mono']
         ${sessionStarted ? 'translate-y-0 opacity-100' : 'translate-y-2 opacity-0 pointer-events-none'}
      `}>
                {/* Active Metadata Header */}
                <div className="px-2 py-1.5 bg-[#FFFFFF] border-b-[1px] border-[#000000] flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <span className={`text-[10px] font-bold tracking-[2px] uppercase ${isViolationActive ? 'text-[#FF0037] animate-pulse' : 'text-[#000000]'}`}>
                            {isViolationActive ? '[BREACH_DETECTED]' : '[REC_SIGNAL]'}
                        </span>
                    </div>
                    <span className="text-[10px] font-bold tracking-[2px] text-[#000000]">
                        [TRUST_INDEX: {Math.round(trustScore)}%]
                    </span>
                </div>

                {/* Camera Feed Container */}
                <div className={`relative aspect-video bg-[#F5F5F5] flex items-center justify-center overflow-hidden transition-colors duration-200 ${isViolationActive ? 'bg-[#FF0037]' : ''}`}>

                    <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        muted
                        className={`w-full h-full object-cover -scale-x-100  
               ${isViolationActive ? 'opacity-20 grayscale' : 'opacity-100'}
            `}
                    />

                    {/* UI Element Overlay Canvas */}
                    <canvas
                        ref={overlayCanvasRef}
                        width={320}
                        height={240}
                        className={`absolute inset-0 w-full h-full object-cover -scale-x-100 pointer-events-none z-20 
                 ${isViolationActive ? 'opacity-0' : 'opacity-100'}`}
                    />

                    {isViolationActive && (
                        <div className="absolute inset-0 flex items-center justify-center z-30 pointer-events-none">
                            <span className="text-[#FF0037] font-bold bg-[#000000] font-['Space_Grotesk'] px-4 py-2 text-sm tracking-widest uppercase border border-[#FF0037]">
                                INTEGRITY_COMPROMISED
                            </span>
                        </div>
                    )}
                </div>

                {/* Sensor Status Footer Overlay */}
                <div className="p-2 bg-[#FFFFFF] border-t-[1px] border-[#000000] text-[#000000]">
                    <div className="flex justify-between items-center text-[8px] uppercase font-bold tracking-[1px]">
                        <span>[SENSOR_STATUS: ACTIVE]</span>
                        <span>[LATENCY: 24MS]</span>
                    </div>
                </div>
            </div>

        </>
    );
};
