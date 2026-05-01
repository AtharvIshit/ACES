// We will rely on window.initSqlJs loaded via CDN in the HTML
let db: any = null;
export let isDbReady = false;

export const initDB = async () => {
    if (isDbReady) return;
    try {
        const initFn = (window as any).initSqlJs;
        if (!initFn) {
            console.warn("initSqlJs not found on window. Ensure CDN script is loaded.");
            return;
        }

        const SQL = await initFn({
            // Load standard sql-wasm file from CDNs for client-side evaluation
            locateFile: (file: string) => {
                if (file.includes('wasm')) {
                    return `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/sql-wasm.wasm`;
                }
                return `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/${file}`;
            }
        });
        db = new SQL.Database();

        db.run(`
         CREATE TABLE IF NOT EXISTS SESSION_AUDIT (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           session_id TEXT NOT NULL,
           candidate_id TEXT,
           violation_type TEXT CHECK(violation_type IN ('GAZE_AVERSION', 'DEVICE_DETECTED', 'WINDOW_BLUR', 'TAB_SWITCH', 'NO_FACE_DETECTED', 'MULTIPLE_FACES', 'LOOKING_AWAY')),
           confidence_score REAL,
           snapshot_blob TEXT,
           system_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
         )
       `);
        isDbReady = true;
        console.log("SQLite (sql.js) DB Initialized successfully.");
    } catch (e) {
        console.error("Failed to init SQLite DB. Skipping Database storage. Error:", e);
        isDbReady = false;
        // We will purposely not throw here so the Proctoring UI can still load 
        // without DB logging feature.
    }
};

export const COMMIT_TO_DISK = (
    sessionId: string,
    candidateId: string,
    violationType: string,
    confidenceScore: number,
    snapshotBlob: string | null
): number | null => {
    if (!db || !isDbReady) return null;

    try {
        db.run(
            `INSERT INTO SESSION_AUDIT (session_id, candidate_id, violation_type, confidence_score, snapshot_blob) 
          VALUES (?, ?, ?, ?, ?)`,
            [sessionId, candidateId, violationType, confidenceScore, snapshotBlob || '']
        );

        const res = db.exec("SELECT last_insert_rowid() as id")[0];
        return res.values[0][0] as number;
    } catch (e) {
        console.error("SQLite insert failed", e);
        return null;
    }
};

export const VACUUM = () => {
    if (db && isDbReady) {
        try {
            db.run("VACUUM");
            console.log("Database VACUUM completed.");
        } catch (e) {
            console.error("VACUUM failed", e);
        }
    }
};

export const getAllLogs = () => {
    if (!db || !isDbReady) return [];
    try {
        const res = db.exec("SELECT * FROM SESSION_AUDIT ORDER BY id DESC");
        if (res.length === 0) return [];

        const cols = res[0].columns;
        return res[0].values.map((row: any[]) => {
            const obj: any = {};
            cols.forEach((col: string, i: number) => {
                obj[col] = row[i];
            });
            return obj;
        });
    } catch (e) {
        return [];
    }
};
