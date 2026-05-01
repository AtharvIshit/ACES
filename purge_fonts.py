import os

# Function to read, replace, write
def swap_fonts(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replacing any lingering Space Mono and DotGothic16
    content = content.replace("'Space Mono'", "'JetBrains Mono'")
    content = content.replace('"Space Mono"', '"JetBrains Mono"')
    content = content.replace('Space Mono', 'JetBrains Mono')
    
    content = content.replace("'DotGothic16'", "'Space Grotesk'")
    content = content.replace('"DotGothic16"', '"Space Grotesk"')
    content = content.replace('DotGothic16', 'Space Grotesk')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

templates_dir = r"d:\CodexPages\Finale\hiring\templates\hiring"

for root, _, files in os.walk(templates_dir):
    for fl in files:
        if fl.endswith(".html"):
            swap_fonts(os.path.join(root, fl))

print("Purged old fonts completely")
