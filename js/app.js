// 发电企业对标分析数据平台 - 主应用JS

// 全局数据
let benchmarkData = [];
let companyData = [];
let indicatorData = [];
let rankingChart = null;
let comparisonChart = null;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
  loadData();
  initNavigation();
  initDimensionTabs();
  initIndicatorSelector();
  initCompanyFilter();
  initComparisonTabs();
});

// 加载数据
function loadData() {
  try {
    const benchmarkEl = document.getElementById('benchmark-data');
    const companyEl = document.getElementById('company-data');
    const indicatorEl = document.getElementById('indicator-data');
    
    if (benchmarkEl && benchmarkEl.textContent !== '__BENCHMARK_DATA__') {
      benchmarkData = JSON.parse(benchmarkEl.textContent);
    }
    if (companyEl && companyEl.textContent !== '__COMPANY_DATA__') {
      companyData = JSON.parse(companyEl.textContent);
    }
    if (indicatorEl && indicatorEl.textContent !== '__INDICATOR_DATA__') {
      indicatorData = JSON.parse(indicatorEl.textContent);
    }
    
    console.log(`数据加载完成: ${benchmarkData.length}条数据, ${companyData.length}家企业, ${indicatorData.length}项指标`);
    
    // 渲染企业卡片
    renderCompanyCards();
    
    // 初始化图表
    setTimeout(() => {
      initRankingChart();
      initComparisonChart();
    }, 100);
  } catch (e) {
    console.error('数据加载失败:', e);
  }
}

// 导航切换
function initNavigation() {
  const navLinks = document.querySelectorAll('.nav-link');
  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const targetId = this.getAttribute('href').substring(1);
      const targetSection = document.getElementById(targetId);
      if (targetSection) {
        targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
      navLinks.forEach(l => l.classList.remove('active'));
      this.classList.add('active');
    });
  });
}

// 维度Tab
function initDimensionTabs() {
  const tabs = document.querySelectorAll('.dim-tab');
  const select = document.getElementById('indicator-select');
  
  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      tabs.forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      
      const dim = this.dataset.dim;
      // 筛选指标
      const options = select.querySelectorAll('option');
      options.forEach(opt => {
        const ind = indicatorData.find(i => i.indicator_id === opt.value);
        if (dim === 'all' || (ind && ind.dimension === dim)) {
          opt.style.display = '';
        } else {
          opt.style.display = 'none';
        }
      });
      // 如果当前选中的指标被隐藏，选择第一个可见的
      if (select.options[select.selectedIndex].style.display === 'none') {
        for (let i = 0; i < select.options.length; i++) {
          if (select.options[i].style.display !== 'none') {
            select.selectedIndex = i;
            break;
          }
        }
      }
      updateRankingChart();
    });
  });
}

// 指标选择器
function initIndicatorSelector() {
  const indicatorSelect = document.getElementById('indicator-select');
  const yearSelect = document.getElementById('year-select');
  
  indicatorSelect.addEventListener('change', updateRankingChart);
  yearSelect.addEventListener('change', updateRankingChart);
}

// 初始化排名图表
function initRankingChart() {
  const chartDom = document.getElementById('ranking-chart');
  rankingChart = echarts.init(chartDom);
  updateRankingChart();
  
  window.addEventListener('resize', () => {
    if (rankingChart) rankingChart.resize();
  });
}

// 更新排名图表
function updateRankingChart() {
  if (!rankingChart) return;
  
  const indicatorId = document.getElementById('indicator-select').value;
  const year = document.getElementById('year-select').value;
  
  // 筛选数据
  const data = benchmarkData.filter(d => 
    d.indicator_id === indicatorId && 
    d.year === year && 
    d.standard_value
  ).sort((a, b) => parseFloat(b.standard_value) - parseFloat(a.standard_value));
  
  // 获取指标信息
  const indicator = indicatorData.find(i => i.indicator_id === indicatorId);
  const unit = indicator ? indicator.standard_unit : '';
  
  // 配置图表
  const option = {
    title: {
      text: `${indicator ? indicator.indicator_name : indicatorId} (${year}年)`,
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 600 }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: function(params) {
        const p = params[0];
        const item = data[p.dataIndex];
        return `<strong>${item.company_name}</strong><br/>
                数值: ${parseFloat(item.standard_value).toLocaleString()} ${unit}<br/>
                排名: 第${p.dataIndex + 1}名<br/>
                ${item.rank_change ? `排名变化: ${item.rank_change > 0 ? '+' : ''}${item.rank_change}` : ''}`;
      }
    },
    grid: { left: 120, right: 60, top: 50, bottom: 30 },
    xAxis: {
      type: 'value',
      name: unit,
      nameTextStyle: { fontSize: 12 }
    },
    yAxis: {
      type: 'category',
      data: data.map(d => d.company_name).reverse(),
      axisLabel: { fontSize: 11 }
    },
    series: [{
      type: 'bar',
      data: data.map(d => ({
        value: parseFloat(d.standard_value),
        itemStyle: {
          color: d.company_type === '国内' ? '#1f5f8b' : '#d4762a'
        }
      })).reverse(),
      barWidth: '60%',
      label: {
        show: true,
        position: 'right',
        formatter: function(params) {
          return parseFloat(params.value).toLocaleString();
        },
        fontSize: 11
      }
    }]
  };
  
  rankingChart.setOption(option, true);
  
  // 更新指标说明
  updateIndicatorInfo(indicator);
}

// 更新指标说明
function updateIndicatorInfo(indicator) {
  const infoEl = document.getElementById('indicator-definition');
  if (indicator) {
    infoEl.innerHTML = `
      <strong>定义：</strong>${indicator.definition || '暂无定义'}<br/>
      <strong>计算公式：</strong>${indicator.formula || '直接取数'}<br/>
      <strong>标准单位：</strong>${indicator.standard_unit}<br/>
      <strong>口径说明：</strong>${indicator.caliber_notes || '使用合并报表口径官方数据'}
    `;
  }
}

// 企业筛选
function initCompanyFilter() {
  const filterBtns = document.querySelectorAll('.filter-btn');
  const searchInput = document.getElementById('company-search');
  
  filterBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      filterBtns.forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      renderCompanyCards();
    });
  });
  
  searchInput.addEventListener('input', renderCompanyCards);
}

// 渲染企业卡片
function renderCompanyCards() {
  const grid = document.getElementById('company-grid');
  const activeFilter = document.querySelector('.filter-btn.active').dataset.type;
  const searchTerm = document.getElementById('company-search').value.toLowerCase();
  
  let filtered = companyData.filter(c => {
    if (activeFilter !== 'all' && c.company_type !== activeFilter) return false;
    if (searchTerm && !c.company_name.toLowerCase().includes(searchTerm) && 
        !(c.company_name_en && c.company_name_en.toLowerCase().includes(searchTerm))) return false;
    return true;
  });
  
  grid.innerHTML = filtered.map(c => {
    // 获取该企业的关键指标
    const revenue = benchmarkData.find(d => 
      d.company_id === c.company_id && d.indicator_id === 'revenue' && d.year === '2025'
    );
    const capacity = benchmarkData.find(d => 
      d.company_id === c.company_id && d.indicator_id === 'installed_capacity' && d.year === '2025'
    );
    
    return `
      <div class="company-card ${c.company_type === '国内' ? 'domestic' : 'foreign'}" 
           data-company-id="${c.company_id}">
        <div class="company-name">${c.company_name}</div>
        <span class="company-type-tag ${c.company_type === '国内' ? 'domestic' : 'foreign'}">
          ${c.company_type}企业
        </span>
        <div class="company-stats">
          <div class="company-stat">
            <div class="company-stat-value">${revenue ? parseFloat(revenue.standard_value).toFixed(0) : '-'}</div>
            <div class="company-stat-label">营收(亿美元)</div>
          </div>
          <div class="company-stat">
            <div class="company-stat-value">${capacity ? parseFloat(capacity.standard_value).toFixed(0) : '-'}</div>
            <div class="company-stat-label">装机(万千瓦)</div>
          </div>
        </div>
      </div>
    `;
  }).join('');
  
  // 添加点击事件
  grid.querySelectorAll('.company-card').forEach(card => {
    card.addEventListener('click', function() {
      const companyId = this.dataset.companyId;
      showCompanyDetail(companyId);
    });
  });
}

// 显示企业详情（简单弹窗）
function showCompanyDetail(companyId) {
  const company = companyData.find(c => c.company_id === companyId);
  const companyIndicators = benchmarkData.filter(d => 
    d.company_id === companyId && d.year === '2025' && d.standard_value
  );
  
  if (!company) return;
  
  let detailHtml = `<h3>${company.company_name}</h3>`;
  if (company.company_name_en) detailHtml += `<p style="color:#666;">${company.company_name_en}</p>`;
  if (company.country) detailHtml += `<p>国家/地区：${company.country}</p>`;
  if (company.website) detailHtml += `<p>官网：<a href="${company.website}" target="_blank">${company.website}</a></p>`;
  
  detailHtml += '<h4 style="margin-top:16px;">2025年关键指标</h4><table style="width:100%;border-collapse:collapse;">';
  detailHtml += '<tr style="background:#f5f7fb;"><th style="padding:8px;text-align:left;border:1px solid #ddd;">指标</th><th style="padding:8px;text-align:left;border:1px solid #ddd;">数值</th><th style="padding:8px;text-align:left;border:1px solid #ddd;">排名</th></tr>';
  
  companyIndicators.forEach(d => {
    detailHtml += `<tr>
      <td style="padding:8px;border:1px solid #ddd;">${d.indicator_name}</td>
      <td style="padding:8px;border:1px solid #ddd;">${parseFloat(d.standard_value).toLocaleString()} ${d.standard_unit}</td>
      <td style="padding:8px;border:1px solid #ddd;">${d.rank ? '第' + d.rank + '名' : '-'}</td>
    </tr>`;
  });
  
  detailHtml += '</table>';
  
  // 简单弹窗
  const modal = document.createElement('div');
  modal.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;z-index:9999;';
  modal.innerHTML = `<div style="background:white;padding:30px;border-radius:10px;max-width:600px;max-height:80vh;overflow-y:auto;position:relative;">
    <button onclick="this.parentElement.parentElement.remove()" style="position:absolute;top:10px;right:15px;border:none;background:none;font-size:20px;cursor:pointer;">&times;</button>
    ${detailHtml}
  </div>`;
  modal.addEventListener('click', function(e) {
    if (e.target === modal) modal.remove();
  });
  document.body.appendChild(modal);
}

// 对比Tab
function initComparisonTabs() {
  const tabs = document.querySelectorAll('.comp-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      tabs.forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      updateComparisonChart(this.dataset.chart);
    });
  });
}

// 初始化对比图表
function initComparisonChart() {
  const chartDom = document.getElementById('comparison-chart');
  comparisonChart = echarts.init(chartDom);
  updateComparisonChart('radar');
  
  window.addEventListener('resize', () => {
    if (comparisonChart) comparisonChart.resize();
  });
}

// 更新对比图表
function updateComparisonChart(chartType) {
  if (!comparisonChart) return;
  
  if (chartType === 'radar') {
    renderRadarChart();
  } else if (chartType === 'scatter') {
    renderScatterChart();
  } else if (chartType === 'trend') {
    renderTrendChart();
  }
}

// 雷达图：中外维度均值对比
function renderRadarChart() {
  const dimensions = ['产品卓越', '品牌卓著', '创新领先', '治理现代'];
  const dimIndicators = {
    '产品卓越': ['installed_capacity', 'power_generation', 'non_fossil_capacity_ratio', 'non_fossil_generation_ratio', 'overseas_capacity'],
    '品牌卓著': ['revenue', 'total_assets', 'overseas_revenue_ratio'],
    '创新领先': ['rd_intensity'],
    '治理现代': ['ebitda', 'roe', 'debt_ratio', 'operating_cash_ratio', 'labor_productivity']
  };
  
  // 计算国内和国外各维度均值（归一化）
  const domesticScores = [];
  const foreignScores = [];
  
  dimensions.forEach(dim => {
    const indicators = dimIndicators[dim];
    const domesticVals = [];
    const foreignVals = [];
    
    indicators.forEach(indId => {
      const data = benchmarkData.filter(d => 
        d.indicator_id === indId && d.year === '2025' && d.standard_value
      );
      const maxVal = Math.max(...data.map(d => parseFloat(d.standard_value)));
      
      data.forEach(d => {
        const normalized = parseFloat(d.standard_value) / maxVal * 100;
        if (d.company_type === '国内') domesticVals.push(normalized);
        else foreignVals.push(normalized);
      });
    });
    
    domesticScores.push(domesticVals.length ? domesticVals.reduce((a,b) => a+b, 0) / domesticVals.length : 0);
    foreignScores.push(foreignVals.length ? foreignVals.reduce((a,b) => a+b, 0) / foreignVals.length : 0);
  });
  
  const option = {
    title: { text: '中外企业四维度均值对比 (2025年)', left: 'center', textStyle: { fontSize: 16 } },
    tooltip: {},
    legend: { data: ['国内企业均值', '国外企业均值'], bottom: 10 },
    radar: {
      indicator: dimensions.map(d => ({ name: d, max: 100 })),
      center: ['50%', '55%'],
      radius: '60%'
    },
    series: [{
      type: 'radar',
      data: [
        { value: domesticScores, name: '国内企业均值', itemStyle: { color: '#1f5f8b' }, areaStyle: { opacity: 0.3 } },
        { value: foreignScores, name: '国外企业均值', itemStyle: { color: '#d4762a' }, areaStyle: { opacity: 0.3 } }
      ]
    }]
  };
  
  comparisonChart.setOption(option, true);
}

// 散点图：规模效益方阵
function renderScatterChart() {
  const revenueData = benchmarkData.filter(d => 
    d.indicator_id === 'revenue' && d.year === '2025' && d.standard_value
  );
  const roeData = benchmarkData.filter(d => 
    d.indicator_id === 'roe' && d.year === '2025' && d.standard_value
  );
  
  const commonIds = new Set(revenueData.map(d => d.company_id));
  roeData.forEach(d => commonIds.add(d.company_id));
  
  const domesticData = [];
  const foreignData = [];
  
  commonIds.forEach(id => {
    const rev = revenueData.find(d => d.company_id === id);
    const roe = roeData.find(d => d.company_id === id);
    if (rev && roe) {
      const point = {
        value: [parseFloat(rev.standard_value), parseFloat(roe.standard_value)],
        name: rev.company_name
      };
      if (rev.company_type === '国内') domesticData.push(point);
      else foreignData.push(point);
    }
  });
  
  const option = {
    title: { text: '对标企业综合方阵图 (规模×效益, 2025年)', left: 'center', textStyle: { fontSize: 16 } },
    tooltip: {
      formatter: function(p) {
        return `<strong>${p.data.name}</strong><br/>营业收入: ${p.value[0].toFixed(1)} 亿美元<br/>ROE: ${p.value[1].toFixed(1)}%`;
      }
    },
    legend: { data: ['国内企业', '国外企业'], bottom: 10 },
    grid: { left: 80, right: 40, top: 60, bottom: 60 },
    xAxis: { name: '营业收入 (亿美元)', nameLocation: 'middle', nameGap: 30 },
    yAxis: { name: '净资产收益率 (%)', nameLocation: 'middle', nameGap: 50 },
    series: [
      {
        type: 'scatter',
        name: '国内企业',
        data: domesticData,
        symbolSize: 15,
        itemStyle: { color: '#1f5f8b' },
        label: { show: true, formatter: '{b}', position: 'right', fontSize: 10 }
      },
      {
        type: 'scatter',
        name: '国外企业',
        data: foreignData,
        symbolSize: 15,
        itemStyle: { color: '#d4762a' },
        label: { show: true, formatter: '{b}', position: 'right', fontSize: 10 }
      }
    ]
  };
  
  comparisonChart.setOption(option, true);
}

// 趋势图：三年趋势对比
function renderTrendChart() {
  const topCompanies = benchmarkData
    .filter(d => d.indicator_id === 'revenue' && d.year === '2025' && d.standard_value)
    .sort((a, b) => parseFloat(b.standard_value) - parseFloat(a.standard_value))
    .slice(0, 8)
    .map(d => d.company_id);
  
  const years = ['2023', '2024', '2025'];
  const colors = ['#1f5f8b', '#d4762a', '#2d8a4e', '#c0392b', '#8e44ad', '#16a085', '#f39c12', '#34495e'];
  
  const series = topCompanies.map((compId, idx) => {
    const compName = benchmarkData.find(d => d.company_id === compId)?.company_name || compId;
    const data = years.map(year => {
      const d = benchmarkData.find(d => 
        d.company_id === compId && d.indicator_id === 'revenue' && d.year === year && d.standard_value
      );
      return d ? parseFloat(d.standard_value) : null;
    });
    return {
      name: compName,
      type: 'line',
      data: data,
      smooth: true,
      itemStyle: { color: colors[idx % colors.length] },
      lineStyle: { width: 2 }
    };
  });
  
  const option = {
    title: { text: '营业收入三年趋势对比 (Top 8企业)', left: 'center', textStyle: { fontSize: 16 } },
    tooltip: { trigger: 'axis' },
    legend: { type: 'scroll', bottom: 10, textStyle: { fontSize: 11 } },
    grid: { left: 60, right: 40, top: 50, bottom: 80 },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value', name: '亿美元' },
    series: series
  };
  
  comparisonChart.setOption(option, true);
}
