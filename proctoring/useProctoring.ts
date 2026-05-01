import { useState, useEffect, useRef, useCallback } from 'react';
import { ViolationType, ProctoringEvent, WorkerResponse } from './types';
import { initDB, COMMIT_TO_DISK, isDbReady } from './db';
// @ts-ignore
import ProctoringWorker from './proctoringWorker.ts?worker&inline';

interface UseProctoringProps {
    onCriticalViolation: () => void;
    trustScoreThreshold?: number;
}

export const useProctoring = ({ onCriticalViolation, trustScoreThreshold = 40 }: UseProctoringProps) => {
    const [trustScore, setTrustScore] = useState(100);
    const [events, setEvents] = useState<ProctoringEvent[]>([]);
    const [isPreflightPassed, setIsPreflightPassed] = useState(false);
    const [preflightStatus, setPreflightStatus] = useState({
        camera: 'pending',
        mic: 'pending',
        worker: 'pending',
    });

    const [isViolationActive, setIsViolationActive] = useState(false);
    const violationClearTimerRef = useRef<number | null>(null);

    const [eyeCoords, setEyeCoords] = useState<{ left: any, right: any } | null>(null);
    // Track prohibited objects to draw bounding boxes
    const [detectedObjects, setDetectedObjects] = useState<any[]>([]);

    const [lastDbWriteId, setLastDbWriteId] = useState<number | null>(null);

    const videoRef = useRef<HTMLVideoElement>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const workerRef = useRef<Worker | null>(null);

    const audioContextRef = useRef<AudioContext | null>(null);

    const lookAwayTimerRef = useRef<number | null>(null);
    const gazeDevTimerRef = useRef<number | null>(null);
    const animationFrameIdRef = useRef<number | null>(null);
    const loopTimerRef = useRef<number | null>(null);

    const sessionId = useRef<string>(crypto.randomUUID());

    const generateGrayscaleSnapshot = useCallback((): string | null => {
        if (!videoRef.current) return null;
        try {
            const snapCanvas = document.createElement('canvas');
            snapCanvas.width = 320;
            snapCanvas.height = 240;
            const ctx = snapCanvas.getContext('2d');
            if (!ctx) return null;

            ctx.filter = 'grayscale(100%) contrast(120%)';
            ctx.drawImage(videoRef.current, 0, 0, 320, 240);
            return snapCanvas.toDataURL('image/webp', 0.5);
        } catch (e) {
            return null;
        }
    }, []);

    const triggerViolationBlurUI = useCallback(() => {
        setIsViolationActive(true);
        if (violationClearTimerRef.current) clearTimeout(violationClearTimerRef.current);
        violationClearTimerRef.current = window.setTimeout(() => {
            setIsViolationActive(false);
        }, 2000);
    }, []);

    const logEvent = useCallback((type: ViolationType, confidence: number = 1.0) => {
        let penalty = 0;
        if (type === 'TAB_SWITCH' || type === 'WINDOW_BLUR') penalty = 5;
        else if (type === 'NO_FACE_DETECTED') penalty = 10;
        else if (type === 'MULTIPLE_FACES') penalty = 20;
        else if (type === 'LOOKING_AWAY') penalty = 5;
        else if (type === 'GAZE_AVERSION') penalty = 12;
        else if (type === 'DEVICE_DETECTED') penalty = 25;

        if (penalty >= 10 || type === 'DEVICE_DETECTED') {
            triggerViolationBlurUI();
        }

        const snapshot = generateGrayscaleSnapshot();

        const eventLog: ProctoringEvent = { timestamp: new Date().toISOString(), type, snapshot: snapshot || undefined, confidence };
        setEvents(prev => [...prev, eventLog]);

        // UI HUD feedback
        setTrustScore(prev => Math.max(0, prev - penalty));

        if (confidence > 0.70 && isDbReady) {
            const rowId = COMMIT_TO_DISK(sessionId.current, 'CANDIDATE-X', type, parseFloat(confidence.toFixed(4)), snapshot);
            if (rowId) setLastDbWriteId(rowId);
        }
    }, [generateGrayscaleSnapshot, triggerViolationBlurUI]);

    useEffect(() => {
        if (trustScore < trustScoreThreshold) {
            onCriticalViolation();
        }
    }, [trustScore, trustScoreThreshold, onCriticalViolation]);

    useEffect(() => {
        const handleVisibilityChange = () => {
            if (document.hidden) logEvent('TAB_SWITCH');
        };
        const handleBlur = () => logEvent('WINDOW_BLUR');

        document.addEventListener('visibilitychange', handleVisibilityChange);
        window.addEventListener('blur', handleBlur);
        return () => {
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            window.removeEventListener('blur', handleBlur);
        };
    }, [logEvent]);

    useEffect(() => {
        const initPreflight = async () => {
            try {
                await initDB();

                const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
                streamRef.current = stream;

                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                }

                const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
                audioContextRef.current = audioContext;

                setPreflightStatus(prev => ({ ...prev, camera: 'success', mic: 'success' }));

                const canvas = document.createElement('canvas');
                canvas.width = 320;
                canvas.height = 240;
                workerRef.current = new ProctoringWorker();

                workerRef.current!.onmessage = (e: MessageEvent<WorkerResponse>) => {
                    if (e.data.type === 'INIT_SUCCESS') {
                        setPreflightStatus(prev => ({ ...prev, worker: 'success' }));
                        setIsPreflightPassed(true);
                        startProcessingLoop();
                    } else if (e.data.type === 'FACES_DETECTED') {
                        handleDetection(e.data);
                    } else if (e.data.type === 'ERROR') {
                        console.error('Proctoring Worker Error:', e.data.error);
                    }
                };

                workerRef.current!.postMessage({ type: 'INIT' });

            } catch (err) {
                console.error("Proctoring Preflight Camera/Mic Error:", err);
                setPreflightStatus(prev => ({ ...prev, camera: 'error', mic: 'error' }));
            }
        };

        console.log("Initializing Proctoring Preflight Checks...");
        initPreflight();

        return () => {
            if (streamRef.current) streamRef.current.getTracks().forEach(track => track.stop());
            if (workerRef.current) workerRef.current.terminate();
            if (audioContextRef.current && audioContextRef.current.state !== 'closed') audioContextRef.current.close().catch(() => { });
            if (lookAwayTimerRef.current) clearTimeout(lookAwayTimerRef.current);
            if (gazeDevTimerRef.current) clearTimeout(gazeDevTimerRef.current);
            if (violationClearTimerRef.current) clearTimeout(violationClearTimerRef.current);
            if (loopTimerRef.current) clearTimeout(loopTimerRef.current);
            if (animationFrameIdRef.current) cancelAnimationFrame(animationFrameIdRef.current);
        };
    }, []);

    const handleDetection = (data: WorkerResponse) => {
        const { faceCount = 0, lookingAway, gazeDeviation = 0, leftEyeCoords, rightEyeCoords, prohibitedObjects = [], maxConfidence = 0 } = data;

        if (faceCount === 0) {
            logEvent('NO_FACE_DETECTED', 0.9);
        } else if (faceCount > 1) {
            logEvent('MULTIPLE_FACES', 0.95);
        }

        if (lookingAway) {
            if (!lookAwayTimerRef.current) {
                lookAwayTimerRef.current = window.setTimeout(() => {
                    logEvent('LOOKING_AWAY', 0.85);
                    lookAwayTimerRef.current = null;
                }, 3000);
            }
        } else {
            if (lookAwayTimerRef.current) {
                clearTimeout(lookAwayTimerRef.current);
                lookAwayTimerRef.current = null;
            }
        }

        if (Math.abs(gazeDeviation) > 15) {
            if (!gazeDevTimerRef.current) {
                gazeDevTimerRef.current = window.setTimeout(() => {
                    logEvent('GAZE_AVERSION', 0.88);
                    gazeDevTimerRef.current = null;
                }, 2000);
            }
        } else {
            if (gazeDevTimerRef.current) {
                clearTimeout(gazeDevTimerRef.current);
                gazeDevTimerRef.current = null;
            }
        }

        if (leftEyeCoords && rightEyeCoords) {
            setEyeCoords({ left: leftEyeCoords, right: rightEyeCoords });
        } else {
            setEyeCoords(null);
        }

        // Store objects to draw rects on UI
        setDetectedObjects(prohibitedObjects);

        if (prohibitedObjects.length > 0 && maxConfidence > 0.65) {
            logEvent('DEVICE_DETECTED', maxConfidence);
        }
    };

    const startProcessingLoop = () => {
        const processFrame = async () => {
            if (!videoRef.current || !workerRef.current || videoRef.current.readyState < 2) {
                loopTimerRef.current = window.setTimeout(() => {
                    animationFrameIdRef.current = requestAnimationFrame(processFrame);
                }, 100);
                return;
            }

            try {
                // Use createImageBitmap which is off-main-thread and much faster than getImageData
                const bitmap = await createImageBitmap(videoRef.current, {
                    resizeWidth: 320,
                    resizeHeight: 240
                });
                workerRef.current.postMessage({ type: 'PROCESS_FRAME', bitmap }, [bitmap]);
            } catch (err) {
                console.warn("Failed to capture frame bitmap:", err);
            }

            loopTimerRef.current = window.setTimeout(() => {
                animationFrameIdRef.current = requestAnimationFrame(processFrame);
            }, 100);
        };

        processFrame();
    };

    useEffect(() => {
        const intervalId = setInterval(() => {
            setTrustScore(prev => Math.min(100, prev + 1));
        }, 10000);
        return () => clearInterval(intervalId);
    }, []);

    return {
        videoRef,
        trustScore,
        events,
        isPreflightPassed,
        preflightStatus,
        isViolationActive,
        eyeCoords,
        detectedObjects,
        lastDbWriteId
    };
};
