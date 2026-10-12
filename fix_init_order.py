with open('dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到init函数中的初始化部分，调整顺序：先显示内容，再初始化图表
old_init = """      // 初始化所有图表
      updateRanking();
      updateMatrix();
      initBubbleChart();
      initHeatmap('all');
      initSlopeChart();
      updateTrend();
      updateComparison();
      
      document.getElementById('statusMsg').style.display = 'none';
      document.getElementById('dashboardContent').style.display = 'block';
      
      // 延迟重绘所有图表，确保容器尺寸正确
      setTimeout(function() {
        Object.values(charts).forEach(c => { if (c && c.resize) c.resize(); });
      }, 100);"""

new_init = """      // 先显示内容，确保容器有正确尺寸
      document.getElementById('statusMsg').style.display = 'none';
      document.getElementById('dashboardContent').style.display = 'block';
      
      // 延迟初始化图表，确保DOM渲染完成
      setTimeout(function() {
        updateRanking();
        updateMatrix();
        initBubbleChart();
        initHeatmap('all');
        initSlopeChart();
        updateTrend();
        updateComparison();
        
        // 再次延迟重绘，确保尺寸正确
        setTimeout(function() {
          Object.values(charts).forEach(c => { if (c && c.resize) c.resize(); });
        }, 200);
      }, 100);"""

if old_init in content:
    content = content.replace(old_init, new_init)
    with open('dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('已修改初始化顺序')
else:
    print('未找到目标代码，尝试查找类似内容')
    import re
    match = re.search(r'初始化所有图表.*?setTimeout.*?\}, 100\);', content, re.DOTALL)
    if match:
        print('找到类似代码:')
        print(match.group(0)[:200])
