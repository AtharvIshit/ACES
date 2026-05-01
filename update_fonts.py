import os

base_path = r"d:\CodexPages\Finale\hiring\templates\base.html"

with open(base_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace fonts
old_fonts = """    <link
        href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Mono:wght@400;700&family=DotGothic16&display=swap"
        rel="stylesheet">"""
new_fonts = """    <link
        href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap"
        rel="stylesheet">"""
content = content.replace(old_fonts, new_fonts)

# Replace variable declarations
content = content.replace('--font-label: "Space Mono", monospace;', '--font-label: "JetBrains Mono", monospace;')
content = content.replace('--font-display: "DotGothic16", monospace;', '--font-display: "Space Grotesk", sans-serif;')

# Fix labels
content = content.replace("font-family: 'Space Mono', monospace !important;", "font-family: 'JetBrains Mono', monospace !important;")

# Enforce 0 margin on headers
content = content.replace('''        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-display) !important;
            font-weight: normal;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            color: #000000 !important;
            margin-bottom: 0.5rem;
        }''', '''        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-display) !important;
            font-weight: 700;
            letter-spacing: -0.02em;
            text-transform: uppercase;
            color: #000000 !important;
            margin: 0px !important;
        }''')

with open(base_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated base.html fonts")
