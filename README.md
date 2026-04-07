# A股打板监控系统

> 🤖 自动化A股龙头战法与打板机会监控，推送到iPhone

## 功能特性

- 📊 **实时监控** - 追踪涨停板、龙头股、异动个股
- 🔥 **龙头识别** - 自动识别板块龙头、跟风股
- 📱 **即时推送** - 发现机会立即推送到iPhone（Bark + Server酱）
- 📋 **每日复盘** - 盘后自动生成复盘报告
- 🚀 **完全自动** - GitHub Actions 定时执行，无需电脑

## 系统架构

```
GitHub Actions (定时任务)
    ↓
Python 监控系统
    ↓
├─ MarketDataService (市场数据)
├─ DragonAnalyzer (龙头分析)
├─ PushOfficer (推送决策)
└─ ReviewService (复盘生成)
    ↓
iPhone (Bark / Server酱)
```

## 推送效果

### 🔴 紧急（立即行动）
```
🔥【龙头机会】中旗新材(001212)
板块：半导体装备
信号：首次涨停/二连板/龙回头
建议：开盘介入/板上买入/等待回踩
⚠️ 风险提示：高位风险
```

## 快速开始

### 1. Fork 本仓库

### 2. 配置推送渠道

在 GitHub Secrets 中添加：

| Name | Value |
|------|-------|
| `BARK_URL` | `https://api.day.app/你的Bark地址/` |
| `SERVERCHAN_KEY` | `SCT你的Server酱Key` |

### 3. 启用定时任务

在 GitHub Actions 中启用工作流，或手动触发：

- **盘中监控** (9:30, 10:00, 10:30, 11:00, 13:30, 14:00, 14:30)
- **盘后复盘** (16:00)

## 文件结构

```
a_stock_monitor/
├── monitor.py          # 核心监控脚本
├── requirements.txt    # Python依赖
├── reviews/            # 复盘报告目录
└── .github/
    └── workflows/
        └── monitor.yml  # GitHub Actions配置
```

## 推送配置

### Bark（推荐）
1. iPhone App Store 下载 **Bark**
2. 打开App，复制推送地址
3. 填入 GitHub Secrets

### Server酱
1. 访问 https://sct.ftqq.com/
2. 登录后复制 SendKey
3. 填入 GitHub Secrets

## 免责声明

⚠️ 本系统仅供信息参考，不构成投资建议。股市有风险，投资需谨慎！

## License

MIT
