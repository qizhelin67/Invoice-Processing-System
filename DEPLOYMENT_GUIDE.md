# 🚀 生产环境部署指南

## 部署方案对比

| 方案 | 难度 | 价格 | 速度 | 推荐度 |
|------|------|------|------|--------|
| **Fly.io** | ⭐ 简单 | 免费 | 快 | ⭐⭐⭐⭐⭐ |
| **Railway** | ⭐⭐ 很简单 | 免费/便宜 | 快 | ⭐⭐⭐⭐⭐ |
| **Render** | ⭐⭐ 简单 | 免费 | 快 | ⭐⭐⭐⭐ |
| **VPS+Docker** | ⭐⭐⭐ 中等 | $5-20/月 | 中 | ⭐⭐⭐ |
| **AWS/GCP** | ⭐⭐⭐⭐ 复杂 | 昂贵 | 慢 | ⭐⭐ |

---

## 方案 1: Railway ⭐⭐⭐⭐⭐ (最推荐)

**优点**: 完全免费、最简单、GitHub集成、自动部署

### 步骤:

#### 1. 准备 GitHub 仓库
```bash
# 在 invoice_processor 文件夹中初始化 Git
cd C:\Users\linqz\invoice_processor
git init
git add .
git commit -m "Initial commit: Invoice Processing System"
```

#### 2. 创建 GitHub 仓库
1. 访问 https://github.com/new
2. 仓库名: `invoice-processor`
3. 选择 Public (公开)
4. 点击 "Create repository"
5. 按照GitHub的提示推送代码:
```bash
git remote add origin https://github.com/你的用户名/invoice-processor.git
git branch -M main
git push -u origin main
```

#### 3. 在 Railway 部署
1. 访问 https://railway.app/
2. 点击 "Sign in with GitHub" (授权)
3. 点击 "New Project" → "Deploy from GitHub repo"
4. 选择您的 `invoice-processor` 仓库
5. Railway 会自动检测到 `railway.json` 配置
6. 点击 "Deploy"

#### 4. 等待部署完成
- Railway 会自动安装依赖、配置服务器
- 大约 3-5 分钟完成
- 部署完成后会得到一个公开的 URL，如: `https://invoice-processor.up.railway.app`

#### 5. 访问您的应用
- 打开部署后的 URL
- 上传发票、测试功能

#### 6. 设置环境变量 (可选)
在 Railway 控制台中:
- 添加 `OPENAI_API_KEY` - 如果想用 AI 功能
- 添加 `PORT` = `8000`

---

## 方案 2: Render ⭐⭐⭐⭐ (免费稳定)

### 步骤:

#### 1. 创建 GitHub 仓库
(同方案 1)

#### 2. 在 Render 部署
1. 访问 https://render.com/
2. 注册账号 (GitHub 登录)
3. 点击 "New +" → "Web Service"
4. 选择 "Build and deploy from a Git repository"
5. 连接您的 GitHub 仓库
6. 选择 `invoice-processor`
7. Render 会自动检测 `render.yaml`

#### 3. 配置
- **Name**: invoice-processor
- **Region**: Singapore (离中国近)
- **Branch**: main
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### 4. 创建 Web Service
- 点击 "Create Web Service"
- 等待部署 (5-10 分钟)
- 获得 URL: `https://invoice-processor.onrender.com`

---

## 方案 3: Fly.io ⭐⭐⭐⭐⭐ (全球 CDN)

### 步骤:

#### 1. 安装 Fly CLI
```bash
# Windows (PowerShell)
pwsh -Command "iwr https://fly.io/install.ps1 | iex"
```

#### 2. 登录
```bash
flyctl auth signup
```

#### 3. 创建应用
```bash
cd C:\Users\linqz\invoice_processor
flyctl launch
```

#### 4. 部署
```bash
flyctl deploy
```

#### 5. 获取 URL
```bash
flyctl info
```

会得到 URL: `https://invoice-process.fly.dev`

---

## 方案 4: Docker 本地/私有服务器 ⭐⭐⭐

### 步骤:

#### 1. 构建 Docker 镜像
```bash
cd C:\Users\linqz\invoice_processor
docker build -t invoice-processor:latest .
```

#### 2. 运行容器
```bash
docker run -d -p 8000:8000 -v $(pwd)/results:/app/results invoice-processor:latest
```

#### 3. 访问
- http://localhost:8000 (本地)
- 或配置反向代理到域名

---

## 🔐 配置反向代理 (Nginx)

如果部署到 VPS，配置 Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## 📊 监控和日志

### Railway 监控
- Dashboard: https://railway.app/dashboard
- 实时日志、CPU、内存使用
- 自动重启

### Render 监控
- Dashboard: https://dashboard.render.com/
- 日志流、部署历史
- 性能指标

### Fly.io 监控
```bash
flyctl logs
flyctl status
flyctl scale count 1
```

---

## 💰 成本估算

| 平台 | 免费额度 | 超额费用 |
|------|----------|----------|
| Railway | $5/月免费额度 | 按用量付费 |
| Render | 750小时/月免费 | ~$7/月起 |
| Fly.io | 3个小应用x256MB免费 | ~$5-20/月起 |
| VPS (Vultr) | - | $5/月起 |

---

## 🎯 推荐选择

### 如果您：
- **想要最简单** → Railway
- **想要稳定免费** → Render
- **想要全球CDN** → Fly.io
- **有服务器** → Docker
- **企业级** → AWS/GCP

---

## 📝 部署前检查清单

- [x] 代码已提交到 GitHub
- [x] Dockerfile 已创建
- [x] railway.json 已创建
- [x] render.yaml 已创建
- [x] fly.toml 已创建
- [x] requirements.txt 完整
- [x] .dockerignore 已创建
- [ ] `OPENAI_API_KEY` (可选)

---

## 🚀 快速部署命令

### Railway (推荐)
```bash
# 1. GitHub: 创建仓库并推送代码
# 2. Railway: 点击部署按钮
# 3. 完成！
```

### Docker
```bash
# 构建
docker build -t invoice-processor .

# 运行
docker run -p 8000:8000 invoice-processor
```

### Render
```bash
# 1. 连接 GitHub 仓库
# 2. 配置并部署
# 3. 自动完成
```

---

## ✅ 部署后验证

1. **访问您的 URL**
2. **上传测试发票**
3. **确认功能正常**
4. **测试多个文件上传**
5. **检查下载 ZIP 功能**

---

## 🔧 生产环境优化

### 1. 添加文件大小限制
```python
@app.post("/upload")
async def upload_invoices(files: List[UploadFile] = File(...)):
    # 限制每个文件 10MB
    MAX_FILE_SIZE = 10 * 1024 * 1024
```

### 2. 添加速率限制
```python
from slowapi import Limiter
limiter = Limiter(app)

@app.post("/upload")
@limiter.limit("10/minute")
async def upload_invoices(...):
```

### 3. 添加数据库 (PostgreSQL)
- 存储处理历史
- 用户管理
- API 密钥管理

### 4. 添加 CDN
- 静态资源CDN
- 加速文件下载

---

## 🎉 部署完成！

部署后您的系统将：
- ✅ 24/7 在线访问
- ✅ 全球用户可使用
- ✅ 自动扩展
- ✅ 自动备份
- ✅ HTTPS 加密

---

**选择一个方案，我会帮您完成部署！** 🚀

推荐从 **Railway** 开始，最简单！
