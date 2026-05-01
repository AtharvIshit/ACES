import os

home_path = r"d:\CodexPages\Finale\hiring\templates\hiring\home.html"
with open(home_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace border radius and surface styles
content = content.replace('border-radius: 16px; border: 1px dashed var(--border);', 'border-radius: 0px; border: 1px solid #000000; background: #FFFFFF;')
content = content.replace('background: var(--surface-alt);', 'background: #FFFFFF;')

# Fix progress bars container
content = content.replace('background: rgba(255,255,255,0.1); border-radius: 3px;', 'background: #F5F5F5; border: 1px solid #000000; border-radius: 0px;')
content = content.replace('background: rgba(255,255,255,0.1); border-radius: 2px;', 'background: #F5F5F5; border: 1px solid #000000; border-radius: 0px;')
content = content.replace('border-radius: 3px;', 'border-radius: 0px;')

# Fix Instant Feedback bar chart mock
content = content.replace('border-radius: 4px 4px 0 0', 'border-radius: 0px;')
content = content.replace('background: rgba(255,255,255,0.1)', 'background: #000000')

# Fix Seamless Integration diagram
content = content.replace('border-radius: 10px; background: rgba(212,0,0,0.1); border: 1px solid var(--rosso);', 'border-radius: 0px; background: #FFFFFF; border: 1px solid #000000; color: #000000;')
content = content.replace('color: var(--rosso);', 'color: #000000;')
content = content.replace('border-radius: 10px; background: var(--rosso); color: white; border: 1px solid var(--rosso); box-shadow: 0 0 16px var(--rosso-soft);', 'border-radius: 0px; background: #000000; color: #FFFFFF; border: 1px solid #000000;')
content = content.replace('border-radius: 10px; background: var(--rosso); color: white;', 'border-radius: 0px; background: #000000; color: #FFFFFF;')
content = content.replace('box-shadow: 0 0 16px var(--rosso-soft);', '')
content = content.replace('border-radius: 10px; background: rgba(255,255,255,0.05); border: 1px solid var(--border);', 'border-radius: 0px; background: #FFFFFF; border: 1px solid #000000; color: #000000;')

# Adjust dashed progress bar lines with solid red
content = content.replace('background: linear-gradient(90deg, var(--rosso) 50%, transparent 50%); background-size: 8px 100%; opacity: 0.5;', 'background: #000000;')

with open(home_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated home.html marketing page elements")
