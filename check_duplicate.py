import re
import json
from collections import defaultdict

# 读取index.html中的数据
with open('index.html', 'r', encoding='utf-8') as f:
    index_content = f.read()

match = re.search(r'<script id="benchmark-data" type="application/json">([\s\S]*?)</script>', index_content)
data = json.loads(match.group(1))

# 检查重复的company_id
company_ids = defaultdict(list)
for d in data:
    company_ids[d['company_id']].append(d['company_name'])

print("企业ID统计:")
for cid, names in sorted(company_ids.items()):
    unique_names = list(set(names))
    print(f"  {cid}: {len(names)}条数据, 名称: {unique_names}")

print(f"\n总企业数: {len(company_ids)}")
print(f"总数据条数: {len(data)}")

# 检查是否有同名但不同ID的企业
name_to_ids = defaultdict(list)
for cid, names in company_ids.items():
    for name in set(names):
        name_to_ids[name].append(cid)

print("\n同名不同ID的企业:")
for name, ids in name_to_ids.items():
    if len(ids) > 1:
        print(f"  {name}: {ids}")
