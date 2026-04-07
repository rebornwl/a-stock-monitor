# GitHub Pages 部署指南

本文档说明如何将A股监控系统部署到GitHub Pages，实现网页端访问。

---

## 方案概览

```
用户访问 → GitHub Pages → 静态网页 → 读取JSON数据
                              ↑
                    GitHub Actions定时更新数据
```

---

## 部署步骤

### Step 1: 上传所有文件到GitHub

需要上传以下文件：

```
你的仓库/
├── .github/
│   └── workflows/
│       ├── monitor.yml           # 监控workflow
│       └── deploy-pages.yml      # 网页部署workflow (新)
├── a_stock_monitor/
│   ├── monitor_v2.py
│   ├── review_generator.py
│   ├── push_test.py
│   └── requirements.txt
├── docs/                         # GitHub Pages目录 (新)
│   ├── index.html
│   └── data/
│       └── realtime.json         # 示例数据
├── README.md
└── a-stock-monitor-v2.zip       # 可用此文件上传
```

**上传方式**：

1. 解压 `a-stock-monitor-v2.zip`
2. 在GitHub仓库页面，点击 **Add file** → **Upload files**
3. 拖入所有文件
4. 点击 **Commit changes**

### Step 2: 配置 Secrets

确保以下Secrets已配置（如已配置可跳过）：

1. 进入 **Settings** → **Secrets and variables** → **Actions**
2. 添加：
   - `BARK_URL`: `https://api.day.app/6GZ4yMmCzeyb9GJQgffWqW/`
   - `SERVERCHAN_KEY`: `SCT330705TA-151U7vBb7Y4QuvXLmVrSGvCz`

### Step 3: 启用 GitHub Pages

1. 进入 **Settings** → **Pages**
2. **Source** 选择: **Deploy from a branch**
3. **Branch** 选择: `gh-pages` / `/ (root)`
4. 点击 **Save**

> ⚠️ 如果没有gh-pages分支，Actions会自动创建

### Step 4: 启用部署Workflow

1. 进入 **Actions** 标签
2. 你会看到 **"Deploy to GitHub Pages"** workflow
3. 点击 workflow → **Run workflow** → **Run workflow**

### Step 5: 等待部署完成

1. 等待部署job完成（约1-2分钟）
2. 进入 **Settings** → **Pages**
3. 看到 **"Your site is live at https://xxx.github.io/a-stock-monitor/"**

---

## 访问你的网页

部署成功后，访问：

```
https://[你的用户名].github.io/a-stock-monitor/
```

例如：
```
https://zhangsan.github.io/a-stock-monitor/
```

---

## 数据更新频率

GitHub Pages 部署 workflow 配置为：

| 时间段 | 更新频率 |
|--------|----------|
| 09:25-14:55 | 每10分钟 |
| 15:05-16:45 | 每10分钟 |

> 💡 数据会在交易时段自动更新，非交易时段显示"等待开盘"

---

## 手动触发更新

如果需要立即更新数据：

1. 进入 **Actions** 标签
2. 选择 **"Deploy to GitHub Pages"**
3. 点击 **Run workflow**
4. 选择 **Run workflow**

---

## 自定义域名（可选）

如果需要使用自己的域名：

1. 购买域名（阿里云/腾讯云）
2. 在GitHub仓库 **Settings** → **Pages** → **Custom domain** 输入域名
3. 在你的域名服务商添加DNS记录：
   - **CNAME**: `[你的用户名].github.io`
4. 等待DNS生效（约10分钟-48小时）

---

## 故障排查

### 网页显示"数据加载失败"

1. 检查Actions是否正常运行
2. 检查 `docs/data/realtime.json` 是否存在
3. 手动运行 **"Deploy to GitHub Pages"** workflow

### Actions部署失败

1. 检查Secrets是否正确配置
2. 检查Python依赖是否完整
3. 查看Actions日志定位问题

### 页面空白

1. 检查浏览器控制台是否有错误
2. 确认 `docs/index.html` 文件存在

---

## 完整文件列表

| 文件 | 用途 |
|------|------|
| `.github/workflows/monitor.yml` | 监控定时任务 |
| `.github/workflows/deploy-pages.yml` | 网页部署任务 |
| `a_stock_monitor/monitor_v2.py` | 增强版监控脚本 |
| `a_stock_monitor/review_generator.py` | 复盘生成器 |
| `a_stock_monitor/push_test.py` | 推送测试 |
| `a_stock_monitor/requirements.txt` | Python依赖 |
| `docs/index.html` | 网页端首页 |
| `docs/data/realtime.json` | 实时数据JSON |

---

## 下一步

1. ✅ 部署完成后，分享你的网页链接
2. ✅ 可将链接保存到书签，随时查看
3. ✅ 手机收到推送时，点击可跳转网页查看详情

---

*由WorkBuddy A股Agent团队生成*
