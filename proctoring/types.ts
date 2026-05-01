export type ViolationType = 'TAB_SWITCH' | 'NO_FACE_DETECTED' | 'MULTIPLE_FACES' | 'LOOKING_AWAY' | 'GAZE_AVERSION' | 'DEVICE_DETECTED' | 'WINDOW_BLUR';

export interface ProctoringEvent {
  timestamp: string;
  type: ViolationType;
  snapshot?: string; // base64 webp grayscale
  confidence?: number;
}

export interface WorkerMessage {
  type: 'INIT' | 'PROCESS_FRAME';
  imageData?: ImageData;
  width?: number;
  height?: number;
}

export interface WorkerResponse {
  type: 'FACES_DETECTED' | 'ERROR' | 'INIT_SUCCESS';
  faceCount?: number;
  lookingAway?: boolean;
  gazeDeviation?: number;
  leftEyeCoords?: { x: number, y: number } | null;
  rightEyeCoords?: { x: number, y: number } | null;
  prohibitedObjects?: any[];
  maxConfidence?: number;
  error?: string;
}
