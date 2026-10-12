import re

with open('dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取JavaScript代码
match = re.search(r'<script>([\s\S]*?)</script>', content)
if match:
    js_code = match.group(1)
    with open('dashboard_check.js', 'w', encoding='utf-8') as f:
        f.write(js_code)
    print(f'已提取{len(js_code)}字符JavaScript代码到dashboard_check.js')
else:
    print('未找到JavaScript代码')
