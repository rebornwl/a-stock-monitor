# 详细 GitHub 上传指南

> 一步步将A股监控系统部署到GitHub

---

## 第一步：创建GitHub仓库

### 1.1 登录GitHub
打开浏览器访问：https://github.com

如果还没有账号，点击 **Sign up** 注册。

### 1.2 创建新仓库
1. 点击右上角的 **+** 按钮
2. 选择 **New repository**

![创建仓库按钮位置](https://i.imgur.com/example.png)

### 1.3 填写仓库信息
```
Owner: 你的用户名 (自动填充)
Repository name: a-stock-monitor
Description: A股打板监控系统 - 龙头战法与打板机会实时推送
```

**重要设置：**
- ✅ **Private** (选择私有仓库，保护您的配置安全)
- ❌ 不要勾选 "Initialize this repository with a README"

然后点击 **Create repository**

---

## 第二步：上传文件

### 方式A：网页上传（推荐）

#### Step 1: 进入仓库页面
创建仓库后会跳转到空仓库页面。

#### Step 2: 上传文件
1. 点击 **uploading an existing file** 链接
   (或者点击仓库页面中的 "uploading an existing file" 按钮)

#### Step 3: 拖拽文件
将 `github-deploy` 文件夹内的**所有内容**拖入上传区域：

```
需要上传的文件结构：
├── .github/
│   └── workflows/
│       └── monitor.yml
├── a_stock_monitor/
│   ├── monitor.py
│   ├── review_generator.py
│   ├── push_test.py
│   └── requirements.txt
├── .gitignore
├── README.md
└── DEPLOY.md
```

**操作方法：**
1. 打开文件资源管理器
2. 导航到 `C:\Users\Administrator\Documents\个股及打板推荐监控\github-deploy`
3. 全选所有文件和文件夹 (Ctrl+A)
4. 拖拽到GitHub上传区域

#### Step 4: 确认上传
1. 滚动到页面底部
2. 点击 **Commit changes** 按钮

---

### 方式B：使用Git命令行

如果您熟悉命令行，可以用这种方式：

```powershell
# 1. 打开PowerShell，进入项目目录
cd "C:\Users\Administrator\Documents\个股及打板推荐监控\github-deploy"

# 2. 初始化Git仓库
git init

# 3. 添加所有文件
git add .

# 4. 提交
git commit -m "Initial commit: A股打板监控系统"

# 5. 添加远程仓库（替换YOUR_USERNAME为你的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/a-stock-monitor.git

# 6. 推送
git branch -M main
git push -u origin main
```

---

## 第三步：配置Secrets

Secrets用于安全存储您的推送配置，不会被公开。

### 3.1 进入仓库设置
1. 在仓库页面，点击 **Settings** 标签
2. 在左侧菜单中找到 **Secrets and variables**
3. 点击 **Actions**

### 3.2 添加BARK_URL
1. 点击 **New repository secret**
2. 填写信息：
   ```
   Name: BARK_URL
   Secret: https://api.day.app/6GZ4yMmCzeyb9GJQgffWqW/
   ```
3. 点击 **Add secret**

### 3.3 添加SERVERCHAN_KEY
1. 再次点击 **New repository secret**
2. 填写信息：
   ```
   Name: SERVERCHAN_KEY
   Secret: SCT330705TA-151U7vBb7Y4QuvXLmVrSGvCz
   ```
3. 点击 **Add secret**

### 3.4 确认Secrets已添加
页面应该显示：
```
BARK_URL      ✅
SERVERCHAN_KEY ✅
```

---

## 第四步：启用Actions

### 4.1 进入Actions页面
在仓库页面，点击 **Actions** 标签

### 4.2 启用工作流
1. 会看到 "A股打板监控" 工作流
2. 点击 **Enable workflow**（如果显示）

### 4.3 允许Actions运行
点击 **I understand my workflows, go ahead and enable them**

---

## 第五步：测试运行

### 5.1 手动触发测试
1. 进入 **Actions** 标签
2. 点击左侧 **A股打板监控**
3. 点击 **Run workflow** 按钮
4. 在下拉菜单中选择模式：**both**
5. 点击绿色 **Run workflow**

### 5.2 查看运行状态
- 点击正在运行的workflow
- 可以看到每个步骤的日志
- 等待约1-2分钟完成

### 5.3 检查推送
- 检查您的iPhone是否收到推送
- 检查Server酱是否收到微信通知

---

## 第六步：验证成功

### ✅ 成功标志
1. **Actions显示绿色勾选** - 所有步骤完成
2. **iPhone收到测试推送** - 推送服务正常
3. **微信收到Server酱通知** - 双重确认

### ❌ 如果失败
查看Actions日志中的错误信息，常见问题：
- Secrets名称错误
- 网络问题（重试即可）
- Python依赖安装失败

---

## 定时任务说明

### 执行时间表（每5分钟监控）
| 时间 | 任务 |
|------|------|
| 09:15 | 竞价开始监控 |
| 09:20 | 竞价观察 |
| 09:24 | 🚨 **竞价即将结束警告** |
| 09:25 | 开盘前准备 |
| 09:30-14:55 | 每5分钟盘中监控 |
| 15:00 | 收盘统计 |
| 16:00 | 盘后复盘报告 |

### ⚠️ GitHub Actions限制
- 最小定时精度：**5分钟**（无法设置1分钟）
- 如果需要更频繁的监控（如1分钟），可以考虑：
  - 腾讯云函数
  - Railway/Render定时任务
  - 阿里云函数计算

---

## 后续维护

### 拉取更新
如果修改了代码，需要重新推送：

```bash
git add .
git commit -m "更新说明"
git push
```

### 查看运行历史
- Actions页面可以查看所有历史运行
- 点击每次运行可以看到详细日志

### 禁用监控
如果需要停止：
- Settings → Actions → 禁用workflow
- 或删除整个仓库

---

## 常见问题

### Q: 推送没收到？
1. 检查GitHub Actions是否成功运行
2. 验证Secrets配置正确
3. 确认iPhone网络正常

### Q: 如何修改推送内容？
编辑 `a_stock_monitor/monitor.py` 后重新推送

### Q: 可以推送几次？
- 每小时最多3条（防骚扰）
- 非交易时段不推送

---

**完成后，您的系统将完全自动化运行！**
