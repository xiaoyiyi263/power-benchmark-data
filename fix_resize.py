with open('dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = """      document.getElementById('statusMsg').style.display = 'none';
      document.getElementById('dashboardContent').style.display = 'block';
      """

new = """      document.getElementById('statusMsg').style.display = 'none';
      document.getElementById('dashboardContent').style.display = 'block';
      
      // 延迟重绘所有图表，确保容器尺寸正确
      setTimeout(function() {
        Object.values(charts).forEach(c => { if (c && c.resize) c.resize(); });
      }, 100);
      """

if old in content:
    content = content.replace(old, new)
    with open('dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('已添加图表resize调用')
else:
    print('未找到目标代码')
    # 打印相关内容
    import re
    match = re.search(r"statusMsg.*?display.*?\n.*?dashboardContent.*?display.*?\n", content)
    if match:
        print('找到类似代码:')
        print(match.group(0))
