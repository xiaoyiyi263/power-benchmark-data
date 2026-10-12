import re
import json

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 检查数据script标签
match = re.search(r'<script id="benchmark-data" type="application/json">([\s\S]*?)</script>', content)
if match:
    data = match.group(1)
    print(f'数据长度: {len(data)}')
    print(f'数据前200字符: {data[:200]}')
    try:
        parsed = json.loads(data)
        print(f'JSON解析成功，共{len(parsed)}条数据')
    except Exception as e:
        print(f'JSON解析失败: {e}')
else:
    print('未找到benchmark-data script标签')

# 检查dashboard.html中的数据加载代码
with open('dashboard.html', 'r', encoding='utf-8') as f:
    dash = f.read()

if "fetch('index.html')" in dash:
    print('\ndashboard.html使用fetch加载数据')
else:
    print('\ndashboard.html未使用fetch加载数据')
