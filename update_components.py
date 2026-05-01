import os

# 1. Update attempt_list.html
attempt_list_path = r"d:\CodexPages\Finale\hiring\templates\hiring\attempt_list.html"
with open(attempt_list_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace .data-cell styles
content = content.replace('''    .data-cell {
        background: rgba(22, 22, 22, 0.4);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid var(--border);
        border-radius: 24px 4px 24px 4px;
        padding: 1.5rem 2rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }

    .data-cell:hover {
        border-color: var(--rosso);
        background: rgba(22, 22, 22, 0.6);
        box-shadow: 0 0 20px rgba(255, 0, 55, 0.05);
    }''', '''    .data-cell {
        background: #FFFFFF !important;
        border: 1px solid #000000 !important;
        border-radius: 0px !important;
        padding: 1.5rem 2rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }

    .data-cell:hover {
        border-color: #FF0037 !important;
        background: #F5F5F5 !important;
        box-shadow: none !important;
    }''')

# Replace Overlay styles
content = content.replace('''    #deep-dive-overlay {
        position: fixed;
        top: 0;
        right: -100%;
        width: 75%;
        height: 100vh;
        background: rgba(11, 11, 11, 0.95);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-left: 1px solid var(--border);
        box-shadow: -10px 0 30px rgba(0, 0, 0, 0.5);
        z-index: 100;
        transition: right 0.4s cubic-bezier(0.19, 1, 0.22, 1);
        display: flex;
        flex-direction: column;
        overflow-y: auto;
    }''', '''    #deep-dive-overlay {
        position: fixed;
        top: 0;
        right: -100%;
        width: 75%;
        height: 100vh;
        background: #FFFFFF !important;
        border-left: 1px solid #000000 !important;
        box-shadow: -10px 0 0px rgba(0, 0, 0, 1) !important;
        z-index: 100;
        transition: right 0.4s cubic-bezier(0.19, 1, 0.22, 1);
        display: flex;
        flex-direction: column;
        overflow-y: auto;
    }''')

# Replace chart-container styles
content = content.replace('''    .chart-container {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 24px 4px 24px 4px;
        padding: 2rem;
        position: relative;
    }''', '''    .chart-container {
        background: #FFFFFF !important;
        border: 1px solid #000000 !important;
        border-radius: 0px !important;
        padding: 2rem;
        position: relative;
    }''')

# Replace JS chart logic
content = content.replace("Chart.defaults.color = '#86868B';", "Chart.defaults.color = '#000000';")
content = content.replace("Chart.defaults.font.family = '\"Space Grotesk\", sans-serif';", "Chart.defaults.font.family = '\"Space Mono\", monospace';")

content = content.replace("backgroundColor: 'rgba(255, 0, 55, 0.1)',", "backgroundColor: 'rgba(255, 0, 55, 0.1)',")
content = content.replace("angleLines: { color: '#2A2A2A' },", "angleLines: { color: '#000000' },")
content = content.replace("grid: { color: '#2A2A2A' },", "grid: { color: '#000000' },")
content = content.replace("font: { family: '\"VT323\", monospace', size: 16 },", "font: { family: '\"DotGothic16\", monospace', size: 16 },")
content = content.replace("color: '#FFFFFF'", "color: '#000000'")

content = content.replace("backgroundColor: timeData.map(v => v > 80 ? '#FF0037' : '#2A2A2A'),", "backgroundColor: timeData.map(v => v > 80 ? '#FF0037' : '#000000'),")
content = content.replace("font: { family: '\"VT323\", monospace' }", "font: { family: '\"DotGothic16\", monospace' }")
content = content.replace("grid: { color: '#2A2A2A' },", "grid: { color: '#000000' },")

# Replace empty state inline style
content = content.replace("border: 1px dashed var(--border); border-radius: 24px 4px 24px 4px; background: rgba(22,22,22,0.2);", "border: 1px dashed #000000; border-radius: 0px; background: #FFFFFF;")

with open(attempt_list_path, 'w', encoding='utf-8') as f:
    f.write(content)

# 2. Update candidate_profile.html
c_profile_path = r"d:\CodexPages\Finale\hiring\templates\hiring\candidate_profile.html"
with open(c_profile_path, 'r', encoding='utf-8') as f:
    c_content = f.read()

# Make pictures square, borders solid
c_content = c_content.replace('border-radius: 50%; border: 2px solid var(--border); overflow: hidden; background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);', 'border-radius: 0px; border: 1px solid #000000; overflow: hidden; background: #FFFFFF;')

# Update assessment history card
c_content = c_content.replace('border-left: 4px solid {% if attempt.passed %}var(--success){% else %}var(--danger){% endif %};', 'border: 1px solid #000000; border-left: 4px solid {% if attempt.passed %}var(--success){% else %}var(--danger){% endif %}; border-radius: 0px;')
c_content = c_content.replace('background: var(--surface-alt); padding: 1.25rem; border-radius: 12px; margin-top: 1rem;', 'background: #F5F5F5; padding: 1.25rem; border-radius: 0px; margin-top: 1rem; border: 1px solid #000000;')

with open(c_profile_path, 'w', encoding='utf-8') as f:
    f.write(c_content)

print("Updated attempt_list and candidate_profile")
