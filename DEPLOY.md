# GitHub 部署指南

## 快速部署到 GitHub

### 方式一：手动上传（推荐新手）

1. **登录 GitHub**
   - 访问 https://github.com
   - 登录您的账号

2. **创建新仓库**
   - 点击右上角 **+** → **New repository**
   - Repository name: `a-stock-monitor`
   - 选择 **Private**（私有仓库）
   - 点击 **Create repository**

3. **上传文件**
   - 点击 **uploading an existing file**
   - 将 `github-deploy` 文件夹内的所有内容拖入上传区：
     ```
     a_stock_monitor/
     ├── monitor.py
     ├── review_generator.py
     ├── requirements.txt
     └── push_test.py
     .github/
     └── workflows/
         └── monitor.yml
     .gitignore
     README.md
     ```
   - 点击 **Commit changes**

4. **配置 Secrets**
   - 进入仓库 → **Settings** → **Secrets and variables** → **Actions**
   - 点击 **New repository secret**，添加：
     - Name: `BARK_URL`
       Value: `https://api.day.app/6GZ4yMmCzeyb9GJQgffWqW/`
     - Name: `SERVERCHAN_KEY`
       Value: `SCT330705TA-151U7vBb7Y4QuvXLmVrSGvCz`

5. **启用 Actions**
   - 进入仓库 → **Actions** 标签
   - 点击 **I understand my workflows, go ahead and enable them**

6. **手动测试**
   - 进入 **Actions** → **A股打板监控** → **Run workflow**
   - 选择模式：`both`
   - 点击 **Run workflow**

### 方式二：使用 Git 命令行

```bash
# 1. 进入项目目录
cd "c:\Users\Administrator\Documents\个股及打板推荐监控\github-deploy"

# 2. 初始化 Git
git init

# 3. 添加所有文件
git add .

# 4. 提交
git commit -m "Initial commit: A股打板监控系统"

# 5. 在 GitHub 创建仓库后，添加远程地址
git remote add origin https://github.com/您的用户名/a-stock-monitor.git

# 6. 推送
git push -u origin main
```

## 配置说明

### 定时任务安排

| 时间 | 任务 |
|------|------|
| 09:25 | 开盘前准备推送 |
| 09:30 | 实时监控（开盘） |
| 10:00 | 盘中监控 |
| 10:30 | 盘中监控 |
| 11:00 | 盘中监控 |
| 13:00 | 下午开盘 |
| 13:30 | 盘中监控 |
| 14:00 | 盘中监控 |
| 14:30 | 盘中监控 |
| 15:00 | 收盘统计 |
| 16:00 | 盘后复盘报告 |

### 推送限制

- 每小时最多推送 **3条** 消息
- 非交易时段不推送
- 同一股票不重复推送

### 推送效果预览

```
📱 iPhone 通知：

🔥【龙头机会】中旗新材(001212)
板块：半导体装备
信号：首次涨停/二连板
建议：强势封板，关注
⚠️ 风险提示：高位风险
⏰ 时间：09:45
```

## 验证部署成功

1. 查看 GitHub Actions 运行记录
2. 检查 iPhone 是否收到测试推送
3. 查看复盘报告是否自动生成

## 常见问题

### Q: 为什么没收到推送？
- 检查 GitHub Actions 是否运行成功
- 验证 Secrets 配置是否正确
- 确认 iPhone 网络正常

### Q: 如何手动触发？
- GitHub → Actions → 点击工作流 → Run workflow

### Q: 如何停止监控？
- 在 GitHub Actions 中禁用工作流即可

---

**部署完成后，您的系统将完全独立运行，无需电脑！**
