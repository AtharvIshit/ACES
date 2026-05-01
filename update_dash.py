import os

dash_c_path = r"d:\CodexPages\Finale\hiring\templates\hiring\dashboard_candidate.html"
with open(dash_c_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Apply bento box to dashboard
content = content.replace('class="card"', 'class="card brutalist-border brutalist-corners" style="padding: 2rem; background: #FFFFFF; border-radius: 0px !important; box-shadow: none !important;"')

with open(dash_c_path, 'w', encoding='utf-8') as f:
    f.write(content)


dash_r_path = r"d:\CodexPages\Finale\hiring\templates\hiring\dashboard_recruiter.html"
with open(dash_r_path, 'r', encoding='utf-8') as f:
    content_r = f.read()

# Apply bento box to dashboard
content_r = content_r.replace('class="card"', 'class="card brutalist-border brutalist-corners" style="padding: 2rem; background: #FFFFFF; border-radius: 0px !important; box-shadow: none !important;"')

with open(dash_r_path, 'w', encoding='utf-8') as f:
    f.write(content_r)

print("Updated Dashboards")
