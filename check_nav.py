import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找导航栏
nav_match = re.search(r'<nav class="main-nav">([\s\S]*?)</nav>', content)
if nav_match:
    print('导航栏内容:')
    print(nav_match.group(1))
else:
    print('未找到导航栏')

# 检查dashboard链接
if 'dashboard.html' in content:
    print('\n✓ index.html包含dashboard链接')
else:
    print('\n✗ index.html不包含dashboard链接')
