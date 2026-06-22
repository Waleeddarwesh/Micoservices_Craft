import re

with open('sysadmin_dashboard/app.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(
    r'(src="/sysadmin/js/[^"]+?)\?v=(\d+)"',
    lambda m: f'{m.group(1)}?v={int(m.group(2)) + 1}"',
    content
)

with open('sysadmin_dashboard/app.html', 'w', encoding='utf-8') as f:
    f.write(content)
