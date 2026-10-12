import re
import json

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'<script id="benchmark-data" type="application/json">([\s\S]*?)</script>', content)
data = json.loads(match.group(1))

# 检查2025年装机容量数据
print("2025年装机容量数据:")
cap_data = []
for d in data:
    if d['indicator_id'] == 'installed_capacity' and str(d['year']) == '2025':
        cap_data.append((d['company_name'], float(d['standard_value'])))

cap_data.sort(key=lambda x: x[1], reverse=True)
for name, val in cap_data:
    print(f"  {name}: {val}万千瓦")

print(f"\n最大值: {cap_data[0][1]}")
print(f"最小值: {cap_data[-1][1]}")
print(f"中位数: {cap_data[len(cap_data)//2][1]}")
