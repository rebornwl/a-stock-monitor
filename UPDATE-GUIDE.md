# A股监控系统 v2.0 更新说明

## 新增功能

### 1. 热点板块分析
- 实时统计涨停股的板块分布
- 识别当前最强热点板块
- 按板块涨停数量和成交额排序
- 显示板块内涨停股列表

### 2. 板块轮动监控
- 每5分钟扫描市场板块动态
- 板块异动时推送预警
- 追踪资金流向热点

### 3. 连板股分析
- 识别连续涨停股票
- 分析连板股的板块分布
- 追踪龙头股的市场表现

### 4. 市场情绪分析
- 涨跌停比计算
- 指数平均涨跌
- 情绪等级判定（极度亢奋/偏强/中性/偏弱/极度低迷）

### 5. 增强复盘报告
- 市场概况（涨停/跌停/涨跌停比/情绪）
- 大盘指数表现
- 热点板块TOP5
- 龙头股TOP10
- 连板股分析
- 明日展望与风险提示

### 6. 网页端（新增）
- 实时展示分析报告
- 涨停板/龙头股一览
- 热点板块排名
- 投资机会推荐
- 精美深色主题UI

---

## 文件结构

```
a_stock_monitor/
├── monitor_v2.py        # 增强版监控脚本（新）
├── review_generator.py  # 增强版复盘生成器（更新）
├── push_test.py         # 推送测试
├── requirements.txt     # 依赖
└── web/
    └── index.html       # 网页端（新）
```

---

## 网页端使用方法

### 方案1: GitHub Pages（推荐）

1. 在GitHub仓库设置中启用GitHub Pages
2. Source选择 `gh-pages` 分支
3. 将 `web/` 目录内容部署到 `docs/` 目录
4. 访问 `https://你的用户名.github.io/a-stock-monitor/`

### 方案2: 本地预览

```bash
cd a_stock_monitor
python monitor_v2.py data  # 生成 data/realtime.json
# 然后用浏览器打开 web/index.html
```

### 方案3: 免费静态托管

可以使用以下免费服务：
- Vercel
- Netlify
- Cloudflare Pages

---

## 运行模式

| 模式 | 命令 | 说明 |
|------|------|------|
| monitor | `python monitor_v2.py monitor` | 实时监控模式 |
| review | `python monitor_v2.py review` | 盘后复盘模式 |
| data | `python monitor_v2.py data` | 生成网页数据 |

---

## 定时任务（北京时间）

| 时间 | 任务 | UTC时间 |
|------|------|---------|
| 09:24 | 竞价警告 | 01:24 |
| 09:25-14:55 | 每5分钟监控 | 01:25-55 |
| 14:55 | 收盘预警 | 06:55 |
| 15:00 | 收盘统计 | 07:00 |
| 16:00 | 盘后复盘 | 08:00 |

---

## 更新步骤

1. **上传新文件到GitHub**:
   - `monitor_v2.py` (新)
   - `review_generator.py` (覆盖)
   - `web/index.html` (新)
   - `.github/workflows/monitor.yml` (覆盖)

2. **Secrets配置**（如已配置可跳过）:
   - `BARK_URL`: `https://api.day.app/6GZ4yMmCzeyb9GJQgffWqW/`
   - `SERVERCHAN_KEY`: `SCT330705TA-151U7vBb7Y4QuvXLmVrSGvCz`

3. **测试运行**:
   - Actions → Run workflow → 选择 `data` 模式测试网页数据

---

## 技术说明

### 数据源
- **东方财富API**: 涨停/跌停/板块数据
- 免费无需API Key
- 实时数据更新

### 板块识别
- 当前使用股票名称关键词匹配
- 未来可接入真实板块API

### 推送通道
- **Bark**: iPhone原生推送
- **Server酱**: 微信推送

---

*由WorkBuddy A股Agent团队生成*
