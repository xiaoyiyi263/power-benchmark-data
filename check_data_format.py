import re
import json

with open('dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取ALL_DATA
match = re.search(r'const ALL_DATA = (\[.*?\]);\s*\n', content, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    print(f"总数据条数: {len(data)}")
    
    # 检查2025年装机容量数据
    print("\n2025年装机容量数据:")
    cap_data = []
    for d in data:
        if d['indicator_id'] == 'installed_capacity':
            year = str(d.get('year', ''))
            print(f"  {d['company_name']}: year={year}, value={d['standard_value']}, year类型={type(d.get('year')).__name__}")
            if year == '2025':
                cap_data.append((d['company_name'], float(d['standard_value'])))
    
    print(f"\n2025年装机容量数据条数: {len(cap_data)}")
    
    # 检查日本杰拉的ROE
    print("\n日本杰拉公司的所有数据:")
    for d in data:
        if '杰拉' in d.get('company_name', ''):
            print(f"  {d['indicator_id']}: year={d['year']}, value={d['standard_value']}")
else:
    print("未找到ALL_DATA")
