import re
import json

# 读取index.html中的数据
with open('index.html', 'r', encoding='utf-8') as f:
    index_content = f.read()

match = re.search(r'<script id="benchmark-data" type="application/json">([\s\S]*?)</script>', index_content)
if not match:
    print('未找到数据')
    exit(1)

data = match.group(1)
print(f'提取到{len(data)}字符数据')

# 读取dashboard.html
with open('dashboard.html', 'r', encoding='utf-8') as f:
    dash_content = f.read()

# 替换空的script标签
old_script = '<script id="benchmark-data" type="application/json">[]</script>'
new_script = f'<script id="benchmark-data" type="application/json">{data}</script>'

if old_script in dash_content:
    dash_content = dash_content.replace(old_script, new_script)
    print('已替换空数据标签')
else:
    print('未找到空数据标签，尝试其他方式')

# 替换fetch加载代码为直接读取
old_fetch = """    // 从index.html的script标签加载数据（这里需要手动加载或从本地读取）
      // 由于是独立页面，我们通过fetch加载数据
      fetch('index.html')
        .then(r => r.text())
        .then(html => {
          const match = html.match(/<script id="benchmark-data" type="application\\/json">([\\s\\S]*?)<\\/script>/);
          if (match) {
            allData = JSON.parse(match[1]);
            initDashboard();
          }
        })
        .catch(() => {
          // 如果fetch失败，使用空数据
          allData = [];
          initDashboard();
        });"""

new_fetch = """    // 直接从页面内嵌的script标签读取数据
      const dataScript = document.getElementById('benchmark-data');
      if (dataScript) {
        try {
          allData = JSON.parse(dataScript.textContent);
          console.log('加载数据成功，共' + allData.length + '条');
        } catch(e) {
          console.error('数据解析失败:', e);
          allData = [];
        }
      }
      initDashboard();"""

if old_fetch in dash_content:
    dash_content = dash_content.replace(old_fetch, new_fetch)
    print('已替换fetch加载代码')
else:
    print('未找到fetch加载代码')

# 保存
with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dash_content)

print('dashboard.html更新完成')
