import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
    plugins: [react()],
    define: {
        'process.env.NODE_ENV': JSON.stringify('production'),
        'process.env': JSON.stringify({})
    },
    build: {
        outDir: '../hiring/static/hiring/js/proctoring',
        emptyOutDir: true,
        lib: {
            entry: 'index.tsx',
            name: 'ProctoringSystem',
            formats: ['iife'],
            fileName: () => 'proctoring.bundle.js',
        },
        rollupOptions: {
            // By default Vite might want to externalize react, but we want it bundled for Django
        }
    }
});
