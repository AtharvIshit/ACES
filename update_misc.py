import os

# Profile
profile_path = r"d:\CodexPages\Finale\hiring\templates\hiring\profile.html"
with open(profile_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Profile picture adjustments
content = content.replace('border-radius: 50%; border: 2px solid var(--border); overflow: hidden; background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);', 'border-radius: 0px; border: 1px solid #000000; overflow: hidden; background: #FFFFFF;')
content = content.replace('style="background: #D40000; color: white; border-radius: 98px; padding: 0.5rem 1.5rem; cursor: pointer; display: inline-block; font-weight: 500;"', 'style="background: #000000; color: white; border-radius: 99px; border: 1px solid #000000; padding: 0.5rem 1.5rem; cursor: pointer; display: inline-block; font-weight: bold; font-family: \'Space Mono\', monospace; font-size: 12px; letter-spacing: 2px; text-transform: uppercase;"')

# Card fix
content = content.replace('class="card"', 'class="card brutalist-corners brutalist-border" style="border-radius: 0px !important; box-shadow: none !important; background: #FFFFFF;"')

with open(profile_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Job List
job_path = r"d:\CodexPages\Finale\hiring\templates\hiring\job_list.html"
with open(job_path, 'r', encoding='utf-8') as f:
    job_content = f.read()

job_content = job_content.replace('class="card"', 'class="card brutalist-corners brutalist-border" style="border-radius: 0px !important; box-shadow: none !important; background: #FFFFFF;"')

with open(job_path, 'w', encoding='utf-8') as f:
    f.write(job_content)

print("Updated Profile and Job List")
