with open('dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复四象限矩阵：手动设置Y轴范围，确保日本杰拉(ROE=59%)可见
old_matrix = """    charts.matrix.setOption({
      tooltip: {formatter: p => p.name+'<br/>'+INDICATOR_NAMES[xInd]+': '+p.value[0]+'<br/>'+INDICATOR_NAMES[yInd]+': '+p.value[1]},
      grid: {left:70, right:50, top:40, bottom:60},
      xAxis: {name: INDICATOR_NAMES[xInd], nameLocation:'middle', nameGap:35},
      yAxis: {name: INDICATOR_NAMES[yInd], nameLocation:'middle', nameGap:45},"""

new_matrix = """    charts.matrix.setOption({
      tooltip: {formatter: p => p.name+'<br/>'+INDICATOR_NAMES[xInd]+': '+p.value[0]+'<br/>'+INDICATOR_NAMES[yInd]+': '+p.value[1]},
      grid: {left:70, right:50, top:40, bottom:60},
      xAxis: {name: INDICATOR_NAMES[xInd], nameLocation:'middle', nameGap:35, scale: true},
      yAxis: {name: INDICATOR_NAMES[yInd], nameLocation:'middle', nameGap:45, min: 0, max: 65},"""

if old_matrix in content:
    content = content.replace(old_matrix, new_matrix)
    print('已修复四象限矩阵Y轴范围')
else:
    print('未找到四象限矩阵代码')

# 修复气泡图：同样设置Y轴范围
old_bubble = """    charts.bubble.setOption({
      tooltip: {formatter: p => p.name+'<br/>装机: '+p.value[0]+'万千瓦<br/>ROE: '+p.value[1]+'%<br/>非化石占比: '+p.value[2]+'%'},
      grid: {left:70, right:50, top:40, bottom:60},
      xAxis: {name:'装机(万千瓦)', nameLocation:'middle', nameGap:35},
      yAxis: {name:'ROE(%)', nameLocation:'middle', nameGap:45},"""

new_bubble = """    charts.bubble.setOption({
      tooltip: {formatter: p => p.name+'<br/>装机: '+p.value[0]+'万千瓦<br/>ROE: '+p.value[1]+'%<br/>非化石占比: '+p.value[2]+'%'},
      grid: {left:70, right:50, top:40, bottom:60},
      xAxis: {name:'装机(万千瓦)', nameLocation:'middle', nameGap:35, scale: true},
      yAxis: {name:'ROE(%)', nameLocation:'middle', nameGap:45, min: 0, max: 65},"""

if old_bubble in content:
    content = content.replace(old_bubble, new_bubble)
    print('已修复气泡图Y轴范围')
else:
    print('未找到气泡图代码')

with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('修复完成')
