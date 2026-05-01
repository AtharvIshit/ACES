import * as tf from '@tensorflow/tfjs-core';
import '@tensorflow/tfjs-backend-webgl';
import '@tensorflow/tfjs-backend-cpu';
import * as blazeface from '@tensorflow-models/blazeface';
import * as faceLandmarksDetection from '@tensorflow-models/face-landmarks-detection';
import { ObjectDetector, FilesetResolver } from '@mediapipe/tasks-vision';

let blazefaceModel: blazeface.BlazeFaceModel | null = null;
let landmarksModel: faceLandmarksDetection.FaceLandmarksDetector | null = null;
let objectModel: ObjectDetector | null = null;

let frameCount = 0;

self.onmessage = async (e: MessageEvent) => {
    const { type, bitmap } = e.data;

    if (type === 'INIT') {
        try {
            await tf.setBackend('webgl');
            await tf.ready();

            // Load BlazeFace
            blazefaceModel = await blazeface.load();

            // Load Face Landmarks (MediaPipe Face Mesh)
            const model = faceLandmarksDetection.SupportedModels.MediaPipeFaceMesh;
            const detectorConfig = { runtime: 'tfjs' };
            landmarksModel = await faceLandmarksDetection.createDetector(model, detectorConfig as any).catch(e => {
                console.warn("Failed to load landmarks model, using fallback", e);
                return null;
            });

            // Load MediaPipe Object Detector for Device Sniffing
            const vision = await FilesetResolver.forVisionTasks(
                "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.x/wasm"
            );
            objectModel = await ObjectDetector.createFromOptions(vision, {
                baseOptions: {
                    modelAssetPath: "https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/float16/1/efficientdet_lite0.tflite",
                    delegate: "CPU"
                },
                scoreThreshold: 0.35,
                runningMode: "IMAGE"
            });

            self.postMessage({ type: 'INIT_SUCCESS' });
        } catch (error: any) {
            console.error('Worker init error:', error);
            self.postMessage({ type: 'ERROR', error: error.message });
        }
    }

    if (type === 'PROCESS_FRAME' && blazefaceModel && bitmap) {
        try {
            frameCount++;
            if (frameCount % 60 === 0) console.log(`[Worker] Processing frame ${frameCount}`);

            // 1. Blazeface (Every frame)
            const predictions = await blazefaceModel.estimateFaces(bitmap as any, false);
            const faceCount = predictions.length;
            let lookingAway = false;
            if (faceCount === 1) {
                const prob = (predictions[0] as any).probability?.[0] || 1;
                if (prob < 0.8) lookingAway = true;
            }

            // 2. Gaze Tracking (Every 3 frames)
            let gazeDeviation = 0;
            let leftEyeCoords = null;
            let rightEyeCoords = null;

            if (frameCount % 3 === 0 && faceCount === 1 && landmarksModel) {
                try {
                    const faces = await landmarksModel.estimateFaces(bitmap as any);
                    if (faces.length > 0) {
                        const face = faces[0];
                        const keypoints = face.keypoints;

                        if (keypoints && keypoints.length > 0) {
                            // Find eye anchors (using basic approx if specific iris bounds are unavailable)
                            const leftEye = keypoints.find(k => k.name === 'leftEye') || keypoints[159] || keypoints[0];
                            const rightEye = keypoints.find(k => k.name === 'rightEye') || keypoints[386] || keypoints[1];

                            if (leftEye && rightEye) {
                                leftEyeCoords = { x: leftEye.x, y: leftEye.y };
                                rightEyeCoords = { x: rightEye.x, y: rightEye.y };

                                const nose = keypoints.find(k => k.name === 'noseTip') || keypoints[1] || keypoints[2];
                                if (nose) {
                                    const faceCenter = (leftEye.x + rightEye.x) / 2;
                                    const eyeDistance = Math.abs(rightEye.x - leftEye.x) || 1;
                                    const deviation = (nose.x - faceCenter) / eyeDistance;
                                    gazeDeviation = deviation * 100; // Return as percentage +/-
                                }
                            }
                        }
                    }
                } catch (e) {
                    console.warn("Gaze tracking error", e);
                }
            }

            // 3. Object Detection (Device Sniffing) (Every 10 frames)
            let prohibitedObjects: any[] = [];
            let maxConfidence = 0;

            if (frameCount % 10 === 0 && objectModel) {
                if (frameCount % 60 === 0) console.log("[Worker] Running Object Detection...");
                const detections = objectModel.detect(bitmap);

                // Diagnostic logging
                if (detections.detections.length > 0) {
                    console.log("[Worker] MediaPipe Detections:", detections.detections.map((d: any) => `${d.categories[0].categoryName} (${Math.round(d.categories[0].score * 100)}%)`));
                }

                const prohibitedLabels = ['cell phone', 'book', 'laptop'];
                prohibitedObjects = detections.detections.filter((d: any) =>
                    prohibitedLabels.includes(d.categories[0].categoryName) && d.categories[0].score > 0.45
                ).map((d: any) => ({
                    class: d.categories[0].categoryName,
                    score: d.categories[0].score,
                    bbox: [
                        d.boundingBox.originX,
                        d.boundingBox.originY,
                        d.boundingBox.width,
                        d.boundingBox.height
                    ]
                }));

                if (prohibitedObjects.length > 0) {
                    maxConfidence = Math.max(...prohibitedObjects.map(o => o.score));
                }
            }

            // Close bitmap to prevent memory leaks in the worker when transferring
            if (bitmap && bitmap.close) bitmap.close();

            self.postMessage({
                type: 'FACES_DETECTED',
                faceCount,
                lookingAway,
                gazeDeviation,
                leftEyeCoords,
                rightEyeCoords,
                prohibitedObjects,
                maxConfidence
            });

        } catch (err: any) {
            self.postMessage({ type: 'ERROR', error: err.message });
        }
    }
};
