import re
import json

# 读取index.html中的数据
with open('index.html', 'r', encoding='utf-8') as f:
    index_content = f.read()

match = re.search(r'<script id="benchmark-data" type="application/json">([\s\S]*?)</script>', index_content)
data = json.loads(match.group(1))

# 企业ID映射表（将重复ID映射到主ID）
id_mapping = {
    'chng': 'huaneng',           # 中国华能
    'cdt': 'datang',             # 中国大唐
    'chd': 'huadian',            # 中国华电
    'chnenergy': 'chn_energy_investment',  # 国家能源投资
    'cgnpc': 'cgn',              # 中国广核
    'gdidc': 'geg',              # 广东省能源
    'gdes': 'geg',               # 广东省能源
    'zjenergy': 'zje',           # 浙江省能源
    'zheneng': 'zje',            # 浙江省能源
    'jng': 'bjenergy',           # 北京能源
    'eletrobras': 'axia',        # 巴西电力
}

# 合并重复企业数据
merged_data = []
seen = {}  # (主ID, indicator_id, year) -> 数据索引

for d in data:
    cid = d['company_id']
    main_id = id_mapping.get(cid, cid)
    d['company_id'] = main_id
    
    key = (main_id, d['indicator_id'], str(d['year']))
    if key in seen:
        # 如果已存在，保留数据量多的那个（或者保留第一个）
        existing = merged_data[seen[key]]
        # 简单策略：保留第一个
        pass
    else:
        seen[key] = len(merged_data)
        merged_data.append(d)

print(f"原始数据: {len(data)}条")
print(f"合并后数据: {len(merged_data)}条")
print(f"移除重复: {len(data) - len(merged_data)}条")

# 统计合并后的企业
companies = {}
for d in merged_data:
    if d['company_id'] not in companies:
        companies[d['company_id']] = d['company_name']

print(f"\n合并后企业数: {len(companies)}")
for cid, name in sorted(companies.items()):
    count = len([d for d in merged_data if d['company_id'] == cid])
    print(f"  {cid}: {name} ({count}条)")

# 生成JSON数据
data_json = json.dumps(merged_data, ensure_ascii=False)

# 生成新的dashboard.html（单列布局，更宽的图表）
html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>高级可视化仪表盘 - 发电企业对标分析数据平台</title>
  <link rel="stylesheet" href="css/style.css">
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
  <style>
    .dashboard-card { background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 24px; }
    .dashboard-card h3 { margin: 0 0 16px 0; font-size: 18px; color: #1f5f8b; border-left: 4px solid #1f5f8b; padding-left: 12px; }
    .chart-container { width: 100%; height: 550px; }
    .chart-container-large { width: 100%; height: 700px; }
    .chart-container-small { width: 100%; height: 450px; }
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
    .control-bar { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; align-items: center; }
    .control-bar select, .control-bar button { padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; background: #fff; cursor: pointer; }
    .control-bar button { background: #1f5f8b; color: #fff; border: none; }
    .ranking-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .ranking-table th, .ranking-table td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; }
    .ranking-table th { background: #f5f7fa; font-weight: 600; color: #1f5f8b; }
    .rank-badge { display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center; border-radius: 50%; font-weight: bold; font-size: 13px; }
    .rank-1 { background: #ffd700; color: #333; }
    .rank-2 { background: #c0c0c0; color: #333; }
    .rank-3 { background: #cd7f32; color: #fff; }
    .rank-other { background: #e8e8e8; color: #666; }
    .score-bar { height: 8px; background: #e8e8e8; border-radius: 4px; overflow: hidden; }
    .score-fill { height: 100%; background: linear-gradient(90deg, #1f77b4, #2ca02c); border-radius: 4px; }
    .company-profile { display: none; margin-top: 16px; padding: 20px; background: #f9fafb; border-radius: 8px; }
    .company-profile.active { display: block; }
    .profile-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
    .profile-header h4 { margin: 0; font-size: 22px; color: #1f5f8b; }
    .profile-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px; }
    .profile-stat { background: #fff; padding: 16px; border-radius: 8px; text-align: center; }
    .profile-stat .value { font-size: 28px; font-weight: bold; color: #1f5f8b; }
    .profile-stat .label { font-size: 13px; color: #666; margin-top: 6px; }
    .back-link { display: inline-block; margin-bottom: 20px; color: #1f5f8b; text-decoration: none; font-weight: 500; }
    .dimension-tabs { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
    .dimension-tab { padding: 8px 16px; background: #e8e8e8; border-radius: 6px; cursor: pointer; font-size: 14px; }
    .dimension-tab.active { background: #1f5f8b; color: #fff; }
    .loading { text-align: center; padding: 40px; color: #666; }
    .error-box { background: #fee; border: 1px solid #fcc; border-radius: 8px; padding: 16px; margin: 16px 0; color: #c33; }
    @media (max-width: 1200px) { .two-col { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header class="site-header">
    <div class="header-content">
      <h1 class="site-title">⚡ 发电企业对标分析数据平台</h1>
      <p class="site-subtitle">高级可视化仪表盘 · 24家国内外能源企业 · 多维深度分析</p>
    </div>
    <nav class="main-nav">
      <a href="index.html" class="nav-link">总览</a>
      <a href="index.html#indicators" class="nav-link">指标体系</a>
      <a href="index.html#companies" class="nav-link">企业入口</a>
      <a href="index.html#comparison" class="nav-link">数据对比</a>
      <a href="charts.html" class="nav-link">图表中心</a>
      <a href="dashboard.html" class="nav-link active">高级仪表盘</a>
      <a href="data_sources.html" class="nav-link">数据来源</a>
    </nav>
  </header>

  <main class="main-content">
    <section class="section">
      <a href="index.html" class="back-link">← 返回总览</a>
      <h2 class="section-title">📊 高级可视化仪表盘</h2>
      <div id="statusMsg" class="loading">正在加载数据和图表...</div>
      <div id="dashboardContent" style="display:none;">

        <!-- 综合得分排行榜 -->
        <div class="dashboard-card">
          <h3>🏆 综合得分排行榜（四大维度加权）</h3>
          <div class="control-bar">
            <span>权重方案：</span>
            <select id="weightScheme">
              <option value="balanced">均衡型（各25%）</option>
              <option value="scale">规模导向（规模40%）</option>
              <option value="profit">效益导向（效益40%）</option>
              <option value="green">绿色导向（绿色40%）</option>
            </select>
            <button onclick="updateRanking()">更新排名</button>
          </div>
          <div id="rankingContainer"></div>
        </div>

        <!-- 四象限矩阵 + 气泡图 -->
        <div class="two-col">
          <div class="dashboard-card">
            <h3>📈 四象限矩阵分析</h3>
            <div class="control-bar">
              <span>X轴：</span>
              <select id="matrixX">
                <option value="installed_capacity">装机容量</option>
                <option value="revenue">营业收入</option>
                <option value="total_assets">资产总额</option>
              </select>
              <span>Y轴：</span>
              <select id="matrixY">
                <option value="roe">ROE</option>
                <option value="ebitda">EBITDA</option>
                <option value="non_fossil_capacity_ratio">非化石占比</option>
              </select>
              <button onclick="updateMatrix()">更新</button>
            </div>
            <div id="matrixChart" class="chart-container"></div>
          </div>

          <div class="dashboard-card">
            <h3>🫧 多维气泡图</h3>
            <p style="font-size:12px;color:#666;">X=装机, Y=ROE, 气泡大小=非化石占比</p>
            <div id="bubbleChart" class="chart-container"></div>
          </div>
        </div>

        <!-- 热力图 -->
        <div class="dashboard-card">
          <h3>🔥 企业×指标热力图（排名分布）</h3>
          <div class="dimension-tabs">
            <div class="dimension-tab active" onclick="switchHeatmap('all', this)">全部</div>
            <div class="dimension-tab" onclick="switchHeatmap('scale', this)">规模</div>
            <div class="dimension-tab" onclick="switchHeatmap('profit', this)">效益</div>
            <div class="dimension-tab" onclick="switchHeatmap('green', this)">绿色</div>
            <div class="dimension-tab" onclick="switchHeatmap('innovation', this)">创新</div>
          </div>
          <div id="heatmapChart" class="chart-container-large"></div>
        </div>

        <!-- 斜率图 + 趋势图 -->
        <div class="two-col">
          <div class="dashboard-card">
            <h3>📐 斜率图（装机排名→ROE排名）</h3>
            <div id="slopeChart" class="chart-container"></div>
          </div>

          <div class="dashboard-card">
            <h3>📉 时间趋势图</h3>
            <div class="control-bar">
              <span>企业：</span>
              <select id="trendCompany"></select>
              <span>指标：</span>
              <select id="trendIndicator">
                <option value="installed_capacity">装机容量</option>
                <option value="revenue">营业收入</option>
                <option value="roe">ROE</option>
                <option value="non_fossil_capacity_ratio">非化石占比</option>
              </select>
              <button onclick="updateTrend()">更新</button>
            </div>
            <div id="trendChart" class="chart-container"></div>
          </div>
        </div>

        <!-- 企业画像 -->
        <div class="dashboard-card">
          <h3>🏢 企业画像（点击排行榜"查看画像"）</h3>
          <div id="companyProfile" class="company-profile">
            <div class="profile-header">
              <h4 id="profileName">选择企业查看画像</h4>
              <span id="profileType" style="font-size:14px;color:#666;"></span>
            </div>
            <div class="profile-stats" id="profileStats"></div>
            <div id="profileRadar" class="chart-container"></div>
          </div>
        </div>

        <!-- 自定义对比 -->
        <div class="dashboard-card">
          <h3>⚖️ 自定义企业对比</h3>
          <div class="control-bar">
            <span>选择企业（按住Ctrl多选）：</span>
            <select id="compareSelect" multiple style="height:100px;min-width:200px;"></select>
            <button onclick="updateComparison()">生成对比</button>
          </div>
          <div id="comparisonTable" style="margin-top:16px;"></div>
          <div id="comparisonRadar" class="chart-container" style="margin-top:16px;"></div>
        </div>

      </div>
    </section>
  </main>

  <script>
  const ALL_DATA = ''' + data_json + ''';
  
  const INDICATOR_NAMES = {
    installed_capacity: '装机容量', power_generation: '发电量', revenue: '营业收入',
    total_assets: '资产总额', ebitda: 'EBITDA', roe: 'ROE',
    debt_ratio: '资产负债率', operating_cash_ratio: '营业现金比率',
    non_fossil_capacity_ratio: '非化石装机占比', non_fossil_generation_ratio: '非化石发电量占比',
    rd_intensity: '研发费用率', overseas_capacity: '海外装机',
    overseas_revenue_ratio: '海外收入占比', labor_productivity: '劳动生产率'
  };
  const INDICATOR_UNITS = {
    installed_capacity: '万千瓦', power_generation: '亿千瓦时', revenue: '亿美元',
    total_assets: '亿美元', ebitda: '亿美元', roe: '%', debt_ratio: '%',
    operating_cash_ratio: '%', non_fossil_capacity_ratio: '%',
    non_fossil_generation_ratio: '%', rd_intensity: '%', overseas_capacity: '万千瓦',
    overseas_revenue_ratio: '%', labor_productivity: '万美元/人'
  };
  const DIMENSION_INDICATORS = {
    scale: ['installed_capacity', 'power_generation', 'revenue', 'total_assets'],
    profit: ['ebitda', 'roe', 'debt_ratio', 'operating_cash_ratio'],
    green: ['non_fossil_capacity_ratio', 'non_fossil_generation_ratio'],
    innovation: ['rd_intensity']
  };
  const HIGHER_IS_BETTER = ['installed_capacity', 'power_generation', 'revenue', 'total_assets',
    'ebitda', 'roe', 'operating_cash_ratio', 'non_fossil_capacity_ratio',
    'non_fossil_generation_ratio', 'rd_intensity', 'overseas_capacity',
    'overseas_revenue_ratio', 'labor_productivity'];

  let companies = [];
  let charts = {};

  function getData(companyId, indicatorId, year) {
    year = year || '2025';
    const item = ALL_DATA.find(d => d.company_id === companyId && d.indicator_id === indicatorId && String(d.year) === year);
    return item ? parseFloat(item.standard_value) : null;
  }

  function getCompanyName(id) {
    const c = companies.find(c => c.id === id);
    return c ? c.name : id;
  }

  function init() {
    try {
      document.getElementById('statusMsg').textContent = '数据加载完成，正在初始化图表...';
      
      // 按company_id去重提取企业列表（数据已合并）
      const companyMap = {};
      ALL_DATA.forEach(d => {
        if (!companyMap[d.company_id]) {
          companyMap[d.company_id] = { id: d.company_id, name: d.company_name, type: d.company_type };
        }
      });
      companies = Object.values(companyMap);
      
      // 初始化下拉框
      const trendSel = document.getElementById('trendCompany');
      const compSel = document.getElementById('compareSelect');
      companies.forEach(c => {
        const o1 = document.createElement('option');
        o1.value = c.id; o1.textContent = c.name;
        trendSel.appendChild(o1);
        const o2 = document.createElement('option');
        o2.value = c.id; o2.textContent = c.name;
        compSel.appendChild(o2);
      });
      
      // 默认选择对比企业
      const domestic = companies.filter(c => c.type === '国内').slice(0, 3);
      const foreign = companies.filter(c => c.type === '国外').slice(0, 2);
      [...domestic, ...foreign].forEach(c => {
        const opt = Array.from(compSel.options).find(o => o.value === c.id);
        if (opt) opt.selected = true;
      });
      
      // 初始化所有图表
      updateRanking();
      updateMatrix();
      initBubbleChart();
      initHeatmap('all');
      initSlopeChart();
      updateTrend();
      updateComparison();
      
      document.getElementById('statusMsg').style.display = 'none';
      document.getElementById('dashboardContent').style.display = 'block';
      
    } catch(e) {
      document.getElementById('statusMsg').innerHTML = 
        '<div class="error-box"><strong>初始化失败：</strong>' + e.message + '<br>请刷新页面重试。</div>';
      console.error(e);
    }
  }

  function calcDimScore(companyId, dim) {
    const inds = DIMENSION_INDICATORS[dim] || [];
    let score = 0, count = 0;
    inds.forEach(ind => {
      const val = getData(companyId, ind);
      if (val !== null) {
        const allVals = companies.map(c => getData(c.id, ind)).filter(v => v !== null);
        if (allVals.length > 1) {
          const max = Math.max(...allVals), min = Math.min(...allVals);
          let norm = HIGHER_IS_BETTER.includes(ind) ? 
            ((val - min) / (max - min)) * 100 : ((max - val) / (max - min)) * 100;
          score += norm; count++;
        }
      }
    });
    return count > 0 ? score / count : 0;
  }

  function updateRanking() {
    const scheme = document.getElementById('weightScheme').value;
    const weights = {
      balanced: {scale:0.25, profit:0.25, green:0.25, innovation:0.25},
      scale: {scale:0.4, profit:0.2, green:0.2, innovation:0.2},
      profit: {scale:0.2, profit:0.4, green:0.2, innovation:0.2},
      green: {scale:0.2, profit:0.2, green:0.4, innovation:0.2}
    };
    const w = weights[scheme];
    
    const scores = companies.map(c => {
      const dims = {};
      let total = 0;
      Object.keys(DIMENSION_INDICATORS).forEach(dim => {
        dims[dim] = calcDimScore(c.id, dim);
        total += dims[dim] * (w[dim] || 0);
      });
      return {company: c, total: Math.round(total*10)/10, dims: dims};
    });
    scores.sort((a,b) => b.total - a.total);
    
    let html = '<table class="ranking-table"><thead><tr><th>排名</th><th>企业</th><th>类型</th><th>综合得分</th><th>规模</th><th>效益</th><th>绿色</th><th>创新</th><th>操作</th></tr></thead><tbody>';
    scores.forEach((s, i) => {
      const rc = i===0?'rank-1':i===1?'rank-2':i===2?'rank-3':'rank-other';
      html += '<tr><td><span class="rank-badge '+rc+'">'+(i+1)+'</span></td>' +
        '<td><strong>'+s.company.name+'</strong></td><td>'+s.company.type+'</td>' +
        '<td><strong style="color:#1f5f8b;">'+s.total+'</strong>' +
        '<div class="score-bar"><div class="score-fill" style="width:'+s.total+'%"></div></div></td>' +
        '<td>'+Math.round(s.dims.scale)+'</td><td>'+Math.round(s.dims.profit)+'</td>' +
        '<td>'+Math.round(s.dims.green)+'</td><td>'+Math.round(s.dims.innovation)+'</td>' +
        '<td><button onclick="showProfile(\\''+s.company.id+'\\')" style="padding:4px 10px;background:#1f5f8b;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:12px;">查看画像</button></td></tr>';
    });
    html += '</tbody></table>';
    document.getElementById('rankingContainer').innerHTML = html;
  }

  function updateMatrix() {
    const xInd = document.getElementById('matrixX').value;
    const yInd = document.getElementById('matrixY').value;
    if (charts.matrix) charts.matrix.dispose();
    charts.matrix = echarts.init(document.getElementById('matrixChart'));
    
    const data = [];
    companies.forEach(c => {
      const x = getData(c.id, xInd), y = getData(c.id, yInd);
      if (x !== null && y !== null) {
        data.push({name: c.name, value: [x, y], 
          itemStyle: {color: c.type==='国内'?'#1f77b4':'#ff7f0e'}});
      }
    });
    const xVals = data.map(d=>d.value[0]), yVals = data.map(d=>d.value[1]);
    const xMean = xVals.reduce((a,b)=>a+b,0)/xVals.length;
    const yMean = yVals.reduce((a,b)=>a+b,0)/yVals.length;
    
    charts.matrix.setOption({
      tooltip: {formatter: p => p.name+'<br/>'+INDICATOR_NAMES[xInd]+': '+p.value[0]+'<br/>'+INDICATOR_NAMES[yInd]+': '+p.value[1]},
      grid: {left:70, right:50, top:40, bottom:60},
      xAxis: {name: INDICATOR_NAMES[xInd], nameLocation:'middle', nameGap:35},
      yAxis: {name: INDICATOR_NAMES[yInd], nameLocation:'middle', nameGap:45},
      series: [{type:'scatter', data:data, symbolSize:18,
        label:{show:true, formatter:'{b}', position:'right', fontSize:11},
        markLine:{silent:true, lineStyle:{type:'dashed', color:'#999'},
          data:[{xAxis:xMean, label:{formatter:'均值'}}, {yAxis:yMean, label:{formatter:'均值'}}]}}]
    });
  }

  function initBubbleChart() {
    if (charts.bubble) charts.bubble.dispose();
    charts.bubble = echarts.init(document.getElementById('bubbleChart'));
    const data = [];
    companies.forEach(c => {
      const x = getData(c.id,'installed_capacity'), y = getData(c.id,'roe'), s = getData(c.id,'non_fossil_capacity_ratio');
      if (x!==null && y!==null && s!==null) {
        data.push({name:c.name, value:[x,y,s],
          itemStyle:{color: c.type==='国内'?'rgba(31,119,180,0.7)':'rgba(255,127,14,0.7)'}});
      }
    });
    charts.bubble.setOption({
      tooltip: {formatter: p => p.name+'<br/>装机: '+p.value[0]+'万千瓦<br/>ROE: '+p.value[1]+'%<br/>非化石占比: '+p.value[2]+'%'},
      grid: {left:70, right:50, top:40, bottom:60},
      xAxis: {name:'装机(万千瓦)', nameLocation:'middle', nameGap:35},
      yAxis: {name:'ROE(%)', nameLocation:'middle', nameGap:45},
      series: [{type:'scatter', data:data, symbolSize: d => Math.max(12, d[2]*0.9),
        label:{show:true, formatter:'{b}', position:'right', fontSize:11}}]
    });
  }

  function initHeatmap(dim) {
    if (charts.heatmap) charts.heatmap.dispose();
    charts.heatmap = echarts.init(document.getElementById('heatmapChart'));
    
    let inds = [];
    if (dim === 'all') {
      inds = Object.keys(INDICATOR_NAMES).filter(k => ALL_DATA.some(d => d.indicator_id === k));
    } else {
      inds = DIMENSION_INDICATORS[dim] || [];
    }
    
    const xData = inds.map(ind => INDICATOR_NAMES[ind] || ind);
    const yData = companies.map(c => c.name);
    const rankData = [];
    
    inds.forEach((ind, i) => {
      const vals = companies.map(c => ({company:c, val:getData(c.id, ind)})).filter(d => d.val !== null);
      vals.sort((a,b) => HIGHER_IS_BETTER.includes(ind) ? b.val-a.val : a.val-b.val);
      vals.forEach((v, rank) => {
        const yIdx = companies.findIndex(c => c.id === v.company.id);
        rankData.push([i, yIdx, rank+1]);
      });
    });
    
    charts.heatmap.setOption({
      tooltip: {formatter: p => yData[p.value[1]]+'<br/>'+xData[p.value[0]]+'<br/>排名: 第'+p.value[2]+'名'},
      grid: {left:140, right:50, top:40, bottom:120},
      xAxis: {type:'category', data:xData, axisLabel:{rotate:45, fontSize:12}},
      yAxis: {type:'category', data:yData, axisLabel:{fontSize:12}},
      visualMap: {min:1, max:24, calculable:true, orient:'horizontal', left:'center', bottom:15,
        inRange:{color:['#d73027','#fc8d59','#fee08b','#d9ef8b','#91cf60','#1a9850']}},
      series: [{type:'heatmap', data:rankData, label:{show:true, fontSize:11, formatter: p => p.value[2]}}]
    });
  }

  function switchHeatmap(dim, el) {
    document.querySelectorAll('.dimension-tab').forEach(t => t.classList.remove('active'));
    el.classList.add('active');
    initHeatmap(dim);
  }

  function initSlopeChart() {
    if (charts.slope) charts.slope.dispose();
    charts.slope = echarts.init(document.getElementById('slopeChart'));
    
    const capRanks = companies.map(c => ({company:c, val:getData(c.id,'installed_capacity')})).filter(d=>d.val!==null);
    capRanks.sort((a,b) => b.val-a.val);
    const roeRanks = companies.map(c => ({company:c, val:getData(c.id,'roe')})).filter(d=>d.val!==null);
    roeRanks.sort((a,b) => b.val-a.val);
    
    const data = [];
    companies.forEach(c => {
      const cr = capRanks.findIndex(d => d.company.id === c.id)+1;
      const rr = roeRanks.findIndex(d => d.company.id === c.id)+1;
      if (cr>0 && rr>0) {
        data.push({name:c.name, value:[cr,rr],
          itemStyle:{color: c.type==='国内'?'#1f77b4':'#ff7f0e'}});
      }
    });
    
    charts.slope.setOption({
      tooltip: {formatter: p => p.name+'<br/>装机排名: 第'+p.value[0]+'名<br/>ROE排名: 第'+p.value[1]+'名'},
      grid: {left:70, right:70, top:40, bottom:50},
      xAxis: {type:'value', name:'装机排名', inverse:true, min:1, max:24, nameLocation:'middle', nameGap:35},
      yAxis: {type:'value', name:'ROE排名', inverse:true, min:1, max:24, nameLocation:'middle', nameGap:45},
      series: [{type:'scatter', data:data, symbolSize:14,
        label:{show:true, formatter:'{b}', position:'right', fontSize:11}}]
    });
  }

  function updateTrend() {
    const cid = document.getElementById('trendCompany').value;
    const ind = document.getElementById('trendIndicator').value;
    if (charts.trend) charts.trend.dispose();
    charts.trend = echarts.init(document.getElementById('trendChart'));
    const years = ['2023','2024','2025'];
    const values = years.map(y => getData(cid, ind, y));
    
    charts.trend.setOption({
      title: {text: getCompanyName(cid)+' - '+INDICATOR_NAMES[ind]+'趋势', left:'center', textStyle:{fontSize:15}},
      tooltip: {trigger:'axis'},
      grid: {left:70, right:50, top:60, bottom:50},
      xAxis: {type:'category', data:years},
      yAxis: {type:'value', name:INDICATOR_UNITS[ind]||''},
      series: [{type:'line', data:values, smooth:true, symbol:'circle', symbolSize:12,
        lineStyle:{width:3, color:'#1f5f8b'}, itemStyle:{color:'#1f5f8b'},
        areaStyle:{color:'rgba(31,95,139,0.1)'}, label:{show:true, formatter:'{c}', fontSize:13}}]
    });
  }

  function showProfile(companyId) {
    const profile = document.getElementById('companyProfile');
    profile.classList.add('active');
    document.getElementById('profileName').textContent = getCompanyName(companyId);
    const c = companies.find(c => c.id === companyId);
    document.getElementById('profileType').textContent = (c ? c.type : '') + '企业';
    
    const keyInds = ['installed_capacity','revenue','roe','non_fossil_capacity_ratio'];
    let sh = '';
    keyInds.forEach(ind => {
      const val = getData(companyId, ind);
      sh += '<div class="profile-stat"><div class="value">'+(val!==null?val:'-')+'</div><div class="label">'+INDICATOR_NAMES[ind]+'</div></div>';
    });
    document.getElementById('profileStats').innerHTML = sh;
    
    if (charts.profile) charts.profile.dispose();
    charts.profile = echarts.init(document.getElementById('profileRadar'));
    const dims = ['scale','profit','green','innovation'];
    const dimNames = ['规模实力','质量效益','绿色低碳','创新驱动'];
    const values = dims.map(dim => Math.round(calcDimScore(companyId, dim)));
    
    charts.profile.setOption({
      title: {text:'四大维度得分', left:'center', textStyle:{fontSize:15}},
      tooltip: {},
      radar: {indicator: dimNames.map(n=>({name:n, max:100})), center:['50%','55%'], radius:'62%'},
      series: [{type:'radar', data:[{value:values, name:getCompanyName(companyId),
        areaStyle:{color:'rgba(31,95,139,0.3)'}, lineStyle:{color:'#1f5f8b', width:2}, itemStyle:{color:'#1f5f8b'}}]}]
    });
    profile.scrollIntoView({behavior:'smooth'});
  }

  function updateComparison() {
    const sel = document.getElementById('compareSelect');
    const selectedIds = Array.from(sel.selectedOptions).map(o => o.value);
    if (selectedIds.length === 0) {
      document.getElementById('comparisonTable').innerHTML = '<p style="color:#999;">请至少选择一家企业</p>';
      return;
    }
    
    const compInds = ['installed_capacity','revenue','roe','non_fossil_capacity_ratio','debt_ratio','rd_intensity'];
    let html = '<table class="ranking-table"><thead><tr><th>指标</th>';
    selectedIds.forEach(id => { html += '<th>'+getCompanyName(id)+'</th>'; });
    html += '</tr></thead><tbody>';
    compInds.forEach(ind => {
      html += '<tr><td><strong>'+INDICATOR_NAMES[ind]+'</strong>（'+INDICATOR_UNITS[ind]+'）</td>';
      selectedIds.forEach(id => {
        const val = getData(id, ind);
        html += '<td>'+(val!==null?val:'-')+'</td>';
      });
      html += '</tr>';
    });
    html += '</tbody></table>';
    document.getElementById('comparisonTable').innerHTML = html;
    
    if (charts.comparison) charts.comparison.dispose();
    charts.comparison = echarts.init(document.getElementById('comparisonRadar'));
    const dims = ['scale','profit','green','innovation'];
    const dimNames = ['规模实力','质量效益','绿色低碳','创新驱动'];
    const seriesData = selectedIds.map(id => ({
      value: dims.map(dim => Math.round(calcDimScore(id, dim))),
      name: getCompanyName(id)
    }));
    
    charts.comparison.setOption({
      title: {text:'多企业维度对比', left:'center', textStyle:{fontSize:15}},
      tooltip: {},
      legend: {bottom:10, data: selectedIds.map(id => getCompanyName(id))},
      radar: {indicator: dimNames.map(n=>({name:n, max:100})), center:['50%','50%'], radius:'58%'},
      series: [{type:'radar', data:seriesData}]
    });
  }

  window.addEventListener('resize', function() {
    Object.values(charts).forEach(c => { if (c && c.resize) c.resize(); });
  });

  if (typeof echarts === 'undefined') {
    document.getElementById('statusMsg').innerHTML = 
      '<div class="error-box"><strong>ECharts库加载失败</strong><br>请检查网络连接后刷新页面。</div>';
  } else {
    window.onload = init;
  }
  </script>
</body>
</html>'''

with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'\n新dashboard.html已生成，大小{len(html)}字符')
print(f'企业数: {len(companies)}')
