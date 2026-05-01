import os

attempt_path = r"d:\CodexPages\Finale\hiring\templates\hiring\attempt_take.html"
with open(attempt_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Background and Body Styles
content = content.replace('''    body {
        background: #000;
        overflow: hidden;
    }''', '''    body {
        background: #F5F5F5 !important;
        overflow: hidden;
    }''')

content = content.replace('''    #fullscreen-gate {
        position: fixed;
        inset: 0;
        background: #000;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        gap: 2rem;
        background-image: radial-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px);
        background-size: 24px 24px;
    }''', '''    #fullscreen-gate {
        position: fixed;
        inset: 0;
        background: #F5F5F5;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        gap: 2rem;
    }''')

content = content.replace('''    .assessment-grid {
        display: grid;
        grid-template-columns: 65% 35%;
        height: 100vh;
        width: 100vw;
        background: #000;
        color: #fff;
    }''', '''    .assessment-grid {
        display: grid;
        grid-template-columns: 65% 35%;
        height: 100vh;
        width: 100vw;
        background: #FFFFFF;
        color: #000000;
    }''')

# Left Panel
content = content.replace('''    .left-panel {
        padding: 4rem;
        overflow-y: auto;
        border-right: 1px solid var(--border);
        position: relative;
    }

    .left-panel::-webkit-scrollbar {
        width: 8px;
    }

    .left-panel::-webkit-scrollbar-track {
        background: #000;
    }

    .left-panel::-webkit-scrollbar-thumb {
        background: #2A2A2A;
        border-radius: 4px;
    }''', '''    .left-panel {
        padding: 4rem;
        overflow-y: auto;
        border-right: 1px solid #000000;
        position: relative;
    }

    .left-panel::-webkit-scrollbar {
        width: 8px;
    }

    .left-panel::-webkit-scrollbar-track {
        background: #F5F5F5;
        border-left: 1px solid #000000;
    }

    .left-panel::-webkit-scrollbar-thumb {
        background: #000000;
        border-radius: 0px;
    }''')

# Right Panel
content = content.replace('''    .right-panel {
        position: relative;
        background: #050505;
        display: flex;
        flex-direction: column;
        height: 100vh;
    }''', '''    .right-panel {
        position: relative;
        background: #F5F5F5;
        display: flex;
        flex-direction: column;
        height: 100vh;
        border-left: 1px solid #000000;
    }''')

# Video Feed
content = content.replace('''    .video-feed-container {
        flex-grow: 1;
        position: relative;
        background: repeating-linear-gradient(0deg,
                #050505,
                #050505 2px,
                #0A0A0A 2px,
                #0A0A0A 4px);
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }''', '''    .video-feed-container {
        flex-grow: 1;
        position: relative;
        background: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border-bottom: 1px solid #000000;
    }''')

content = content.replace('''    .video-feed-container::after {
        content: " ";
        display: block;
        position: absolute;
        inset: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
        z-index: 2;
        background-size: 100% 2px, 3px 100%;
        pointer-events: none;
    }''', '''    .video-feed-container::after {
        content: " ";
        display: block;
        position: absolute;
        inset: 0;
        background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.05) 2px, rgba(0,0,0,0.05) 4px);
        z-index: 2;
        pointer-events: none;
    }''')

# Camera Placeholder & Scanline
content = content.replace('''    .camera-placeholder {
        border: 1px solid #2A2A2A;
        padding: 2rem;
        color: #4A4A4A;
        font-family: var(--font-display);
        letter-spacing: 0.1em;
        text-align: center;
        z-index: 5;
    }''', '''    .camera-placeholder {
        border: 1px solid #000000;
        padding: 2rem;
        color: #000000;
        font-family: var(--font-display);
        letter-spacing: 0.1em;
        text-align: center;
        z-index: 5;
        background: #FFFFFF;
    }''')

# Timer Panel
content = content.replace('''    .timer-panel {
        padding: 3rem;
        border-top: 1px solid var(--border);
        background: #0B0B0B;
        text-align: left;
    }

    .timer-display {
        font-family: var(--font-display);
        font-size: 5rem;
        color: var(--text);
        letter-spacing: 0.05em;
        line-height: 1;
        margin-top: 1rem;
        transition: color 0.3s;
    }''', '''    .timer-panel {
        padding: 3rem;
        background: #FFFFFF;
        text-align: left;
    }

    .timer-display {
        font-family: var(--font-display);
        font-size: 5rem;
        color: #000000;
        letter-spacing: 0.05em;
        line-height: 1;
        margin-top: 1rem;
        transition: color 0.3s;
    }''')

# Editor fonts
content = content.replace("color: var(--text);", "color: #000000;")
content = content.replace("color: #E0E0E0;", "color: #000000;")
content = content.replace("color: #4A4A4A;", "color: #000000;")
content = content.replace("border-bottom: 1px solid #2A2A2A;", "border-bottom: 1px solid #000000;")

content = content.replace('''    .brutal-radio-label {
        display: flex;
        align-items: center;
        padding: 1rem 1.25rem;
        background: rgba(22, 22, 22, 0.4);
        border: 1px solid var(--border);
        cursor: pointer;
        transition: all 0.2s;
        font-family: var(--font-label);
        font-size: 0.95rem;
    }

    .brutal-radio-label:hover {
        background: rgba(22, 22, 22, 0.8);
        border-color: #4A4A4A;
    }

    input[type="radio"]:checked+.brutal-radio-label {
        border-color: var(--rosso);
        background: rgba(255, 0, 55, 0.05);
        color: #fff;
    }''', '''    .brutal-radio-label {
        display: flex;
        align-items: center;
        padding: 1rem 1.25rem;
        background: #FFFFFF;
        border: 1px solid #000000;
        cursor: pointer;
        transition: all 0.2s;
        font-family: var(--font-label);
        font-size: 0.95rem;
        color: #000000;
    }

    .brutal-radio-label:hover {
        background: #F5F5F5;
        border-color: #FF0037;
    }

    input[type="radio"]:checked+.brutal-radio-label {
        border-color: #000000;
        background: #000000;
        color: #FFFFFF;
    }''')

content = content.replace('''    .brutal-radio-label::before {
        content: '[ ]';
        margin-right: 1rem;
        color: #4A4A4A;
        font-family: var(--font-display);
        font-size: 1.2rem;
    }

    input[type="radio"]:checked+.brutal-radio-label::before {
        content: '[X]';
        color: var(--rosso);
    }''', '''    .brutal-radio-label::before {
        content: '[ ]';
        margin-right: 1rem;
        color: #000000;
        font-family: var(--font-display);
        font-size: 1.2rem;
    }

    input[type="radio"]:checked+.brutal-radio-label::before {
        content: '[X]';
        color: #FFFFFF;
    }''')

content = content.replace('''    .btn-brutal-large {
        width: 100%;
        padding: 1.5rem;
        font-size: 1.2rem;
        border-radius: 0;
        background: var(--rosso);
        color: white;
        border: none;
        font-family: var(--font-display);
        letter-spacing: 0.1em;
        cursor: pointer;
        transition: background 0.2s;
        text-transform: uppercase;
    }''', '''    .btn-brutal-large {
        width: 100%;
        padding: 1.5rem;
        font-size: 1.2rem;
        border-radius: 0;
        background: #000000;
        color: #FFFFFF;
        border: 1px solid #000000;
        font-family: var(--font-display);
        letter-spacing: 0.1em;
        cursor: pointer;
        transition: background 0.2s;
        text-transform: uppercase;
    }

    .btn-brutal-large:hover {
        background: #FF0037;
        border-color: #FF0037;
        color: #FFFFFF;
    }''')

content = content.replace('''<div class="dot-matrix" style="font-size: 2rem; color: var(--text);">SECURE ENVIRONMENT REQUIRED</div>''', '''<div class="dot-matrix" style="font-size: 2rem; color: #000000;">SECURE ENVIRONMENT REQUIRED</div>''')

with open(attempt_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated attempt_take.html")
