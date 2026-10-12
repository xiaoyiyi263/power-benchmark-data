with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

if 'dashboard.html' in content:
    print('index.html已有dashboard链接')
else:
    old = '<a href="charts.html" class="nav-link">图表中心</a>'
    new = '<a href="charts.html" class="nav-link">图表中心</a>\n      <a href="dashboard.html" class="nav-link">高级仪表盘</a>'
    content = content.replace(old, new)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('已在index.html添加dashboard链接')
