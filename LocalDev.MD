# 本地开发环境配置指南

## Cattle SNP Effect Value Database - Local Development Setup

本文档说明如何配置本地开发环境，用于开发和调试牛SNP效应值数据库系统。

---

## 目录

1. [软件清单](#软件清单)
2. [数据库安装配置](#数据库安装配置)
3. [后端环境配置](#后端环境配置)
4. [前端环境配置](#前端环境配置)
5. [完整启动流程](#完整启动流程)
6. [常用开发命令](#常用开发命令)
7. [故障排查](#故障排查)

---

## 软件清单

### 必需软件

| 类别 | 软件 | 版本要求 | 下载地址 | 用途 |
|------|------|----------|----------|------|
| 数据库 | PostgreSQL | 15+ | https://www.postgresql.org/download/windows/ | 存储SNP数据 |
| 后端 | Python | 3.11+ | https://www.python.org/downloads/ | 运行FastAPI |
| 前端 | Node.js | 20+ | https://nodejs.org/ | 运行开发服务器 |
| 版本控制 | Git | 最新 | https://git-scm.com/downloads/ | 代码版本管理 |

### 可选软件

| 软件 | 版本要求 | 下载地址 | 用途 |
|------|----------|----------|------|
| Docker | 最新 | https://www.docker.com/products/docker-desktop/ | 运行PostgreSQL容器 |
| pgAdmin | 最新 | https://www.pgadmin.org/download/ | 数据库可视化管理 |
| VS Code | 最新 | https://code.visualstudio.com/ | 代码编辑器 |

### VS Code 推荐插件

```
- Python (Microsoft)          # Python语言支持
- Vue - Official (Vue)        # Vue语言支持
- Pylance (Microsoft)         # Python智能提示
- PostgreSQL (Chris Kolkman)  # 数据库管理
- ESLint                      # 代码检查
- Prettier - Code formatter   # 代码格式化
```

---

## 数据库安装配置

### 方式一：使用Docker（推荐）

Docker方式最简单，无需手动安装PostgreSQL。

**1. 安装Docker Desktop**
```
下载: https://www.docker.com/products/docker-desktop/
安装后启动Docker Desktop
```

**2. 启动PostgreSQL容器**

Windows CMD:
```batch
docker run -d --name cattle_db -p 5432:5432 ^
  -e POSTGRES_USER=cattle_user ^
  -e POSTGRES_PASSWORD=cattle_pass ^
  -e POSTGRES_DB=cattle_snp_db ^
  postgres:15-alpine
```

Windows PowerShell:
```powershell
docker run -d --name cattle_db -p 5432:5432 `
  -e POSTGRES_USER=cattle_user `
  -e POSTGRES_PASSWORD=cattle_pass `
  -e POSTGRES_DB=cattle_snp_db `
  postgres:15-alpine
```

**3. 验证容器运行**
```bash
docker ps
# 应该看到 cattle_db 容器在运行
```

**4. 常用Docker命令**
```bash
# 查看容器日志
docker logs cattle_db

# 停止容器
docker stop cattle_db

# 启动容器
docker start cattle_db

# 删除容器
docker rm cattle_db

# 进入数据库
docker exec -it cattle_db psql -U cattle_user -d cattle_snp_db
```

---

### 方式二：本地安装PostgreSQL

**1. 下载安装PostgreSQL**

```
下载地址: https://www.postgresql.org/download/windows/
选择版本 15.x
安装时记住设置的密码（默认用户是 postgres）
```

**2. 创建数据库**

使用 pgAdmin 或命令行创建：

```bash
# 使用命令行创建
psql -U postgres
CREATE USER cattle_user WITH PASSWORD 'cattle_pass';
CREATE DATABASE cattle_snp_db OWNER cattle_user;
GRANT ALL PRIVILEGES ON DATABASE cattle_snp_db TO cattle_user;
\q
```

**3. 测试连接**
```bash
psql -h localhost -U cattle_user -d cattle_snp_db
```

---

## 后端环境配置

### 1. 安装Python

```
下载: https://www.python.org/downloads/
下载 Python 3.11.x 或更高版本
安装时勾选 "Add Python to PATH"
```

验证安装：
```bash
python --version
# 应显示: Python 3.11.x 或更高

pip --version
# 应显示: pip 版本信息
```

### 2. 创建虚拟环境（推荐）

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
Windows CMD:
venv\Scripts\activate.bat

Windows PowerShell:
venv\Scripts\Activate.ps1

# 如果PowerShell报错，先执行:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. 安装Python依赖

```bash
cd backend

# 确保虚拟环境已激活
pip install -r requirements.txt
```

**requirements.txt 包含:**
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
pydantic==2.5.3
pydantic-settings==2.1.0
python-multipart==0.0.6
python-dotenv==1.0.0
tqdm==4.66.1
```

### 4. 设置环境变量

**Windows CMD:**
```batch
set DATABASE_URL=postgresql://cattle_user:cattle_pass@localhost:5432/cattle_snp_db
```

**Windows PowerShell:**
```powershell
$env:DATABASE_URL="postgresql://cattle_user:cattle_pass@localhost:5432/cattle_snp_db"
```

**或创建 .env 文件:**
```bash
cd backend
# 创建 .env 文件，内容如下:
DATABASE_URL=postgresql://cattle_user:cattle_pass@localhost:5432/cattle_snp_db
LOG_LEVEL=info
```

---

## 前端环境配置

### 1. 安装Node.js

```
下载: https://nodejs.org/
选择 LTS 版本（长期支持版本）
安装后 npm 会自动安装
```

验证安装：
```bash
node --version
# 应显示: v20.x.x 或更高

npm --version
# 应显示: 10.x.x 或更高
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
```

**package.json 主要依赖:**
```json
{
  "vue": "^3.4.15",
  "vue-router": "^4.2.5",
  "axios": "^1.6.5",
  "element-plus": "^2.5.2",
  "@element-plus/icons-vue": "^2.3.1"
}
```

### 3. 配置开发代理

`vite.config.js` 已配置API代理：
```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

---

## 完整启动流程

### 第一步：启动数据库

**使用Docker（推荐）:**
```bash
docker start cattle_db
# 或首次运行
docker run -d --name cattle_db -p 5432:5432 -e POSTGRES_USER=cattle_user -e POSTGRES_PASSWORD=cattle_pass -e POSTGRES_DB=cattle_snp_db postgres:15-alpine
```

**使用本地PostgreSQL:**
```bash
# 确保PostgreSQL服务正在运行
# Windows 服务中找到 PostgreSQL 15 服务并启动
```

---

### 第二步：初始化数据库结构

```bash
# 方式一：使用psql命令
psql -h localhost -U cattle_user -d cattle_snp_db -f database/schema.sql

# 方式二：使用Docker容器
docker exec -i cattle_db psql -U cattle_user -d cattle_snp_db < database/schema.sql

# 方式三：使用Python
cd backend
python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://cattle_user:cattle_pass@localhost:5432/cattle_snp_db'); conn = engine.connect(); script = open('../database/schema.sql').read(); conn.connection.cursor().execute(script); conn.close(); print('Database initialized!')"
```

---

### 第三步：启动后端服务

```bash
cd backend

# 激活虚拟环境（如果使用）
venv\Scripts\activate

# 设置环境变量
set DATABASE_URL=postgresql://cattle_user:cattle_pass@localhost:5432/cattle_snp_db

# 启动开发服务器（推荐，支持热重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或直接运行
python main.py
```

**验证后端运行:**
```
浏览器访问: http://localhost:8000
应该看到: {"message":"Cattle SNP Effect Value Database API"...}

API文档: http://localhost:8000/docs
健康检查: http://localhost:8000/health
```

---

### 第四步：导入数据（可选）

```bash
cd backend

# 确保虚拟环境已激活
venv\Scripts\activate

# 运行导入脚本
python import_data.py --file ../SNP-disease/variant_sad_all_targets.tsv

# 带参数导入
python import_data.py --file ../SNP-disease/variant_sad_all_targets.tsv --batch-size 1000 --refresh-views
```

---

### 第五步：启动前端服务

```bash
cd frontend

# 启动开发服务器
npm run dev
```

**验证前端运行:**
```
浏览器访问: http://localhost:5173
应该看到: 牛SNP效应值数据库界面
```

---

## 常用开发命令

### 后端

```bash
# 进入后端目录
cd backend

# 激活虚拟环境
venv\Scripts\activate

# 安装新依赖
pip install <package-name>
pip freeze > requirements.txt

# 运行开发服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 运行数据导入
python import_data.py --file ../SNP-disease/variant_sad_all_targets.tsv

# 退出虚拟环境
deactivate
```

### 前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### 数据库

```bash
# 连接数据库
psql -h localhost -U cattle_user -d cattle_snp_db

# 常用SQL命令
\dt                    # 列出所有表
\d snps                # 查看snps表结构
SELECT COUNT(*) FROM snps;  # 统计SNP数量
\q                     # 退出

# 导出数据库
pg_dump -h localhost -U cattle_user cattle_snp_db > backup.sql

# 导入数据库
psql -h localhost -U cattle_user cattle_snp_db < backup.sql
```

### Docker

```bash
# 查看运行中的容器
docker ps

# 查看容器日志
docker logs cattle_db
docker logs -f cattle_db  # 实时查看

# 停止/启动容器
docker stop cattle_db
docker start cattle_db

# 删除容器
docker rm cattle_db

# 进入容器
docker exec -it cattle_db bash
docker exec -it cattle_db psql -U cattle_user -d cattle_snp_db
```

---

## 开发端口分配

| 服务 | 端口 | 地址 |
|------|------|------|
| 前端开发服务器 | 5173 | http://localhost:5173 |
| 后端API | 8000 | http://localhost:8000 |
| Swagger API文档 | 8000 | http://localhost:8000/docs |
| ReDoc API文档 | 8000 | http://localhost:8000/redoc |
| PostgreSQL | 5432 | localhost:5432 |

---

## 故障排查

### 问题1：端口被占用

```bash
# 查看端口占用
netstat -ano | findstr :5432
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# 结束占用端口的进程
taskkill /PID <进程ID> /F
```

### 问题2：数据库连接失败

```bash
# 检查PostgreSQL是否运行
docker ps  # 如果使用Docker
# 或检查Windows服务中的PostgreSQL服务

# 测试连接
psql -h localhost -U cattle_user -d cattle_snp_db

# 检查防火墙设置
```

### 问题3：Python模块导入错误

```bash
# 确保虚拟环境已激活
# 重新安装依赖
pip install -r requirements.txt

# 检查Python路径
where python
```

### 问题4：前端npm install失败

```bash
# 清除npm缓存
npm cache clean --force

# 删除node_modules重新安装
rmdir /s node_modules
npm install

# 或使用淘宝镜像
npm config set registry https://registry.npmmirror.com
```

### 问题5：psycopg2安装失败

```bash
# Windows下可能需要安装C编译工具
# 或使用预编译的二进制版本
pip install psycopg2-binary
```

---

## 项目结构

```
cattleVarDB/
├── database/
│   └── schema.sql              # 数据库结构
├── backend/
│   ├── main.py                 # FastAPI应用
│   ├── import_data.py          # 数据导入脚本
│   ├── requirements.txt        # Python依赖
│   ├── .env                    # 环境变量（需自己创建）
│   └── venv/                   # 虚拟环境（创建后生成）
├── frontend/
│   ├── src/                    # 源代码
│   ├── node_modules/           # npm依赖（安装后生成）
│   ├── package.json            # Node依赖配置
│   └── vite.config.js          # Vite配置
├── SNP-disease/
│   └── variant_sad_all_targets.tsv  # 数据文件
└── LocalDev.MD                 # 本文档
```

---

## 下一步

环境配置完成后，您可以：

1. 查看 API 文档: http://localhost:8000/docs
2. 访问前端界面: http://localhost:5173
3. 阅读完整设计文档: `DESIGN_DOCUMENTATION.md`
4. 开始开发新功能

---

**文档版本**: 1.0.0
**最后更新**: 2024-01-14







> 安装了docker后，想更好的本地开发，想安装python，那么是先安装anaconda,在anaconda中安装虚拟环境，用虚拟环境中的python.
还是不安装anaconda，直接安装Python呢？

● 这是一个很好的问题！两种方案各有优劣，我帮你分析一下：

  推荐：直接安装 Python

  对于大多数开发者来说，我更推荐直接安装 Python，原因如下：

  直接安装 Python 的优势

  - 轻量简洁：Python 安装包只有 ~30MB，Anaconda 需要 ~500MB+
  - 更接近生产环境：生产服务器通常不会安装 Anaconda
  - 学习价值：能更好地理解 Python 环境管理（pip、venv）
  - 启动更快：conda 环境激活相对较慢

  使用方式

  # 安装 Python 后
  python -m venv venv          # 创建虚拟环境
  source venv/bin/activate      # 激活（Linux/Mac）
  # 或
  venv\Scripts\activate         # 激活（Windows）

  pip install -r requirements.txt

  ---
  选择 Anaconda 的场景

  Anaconda 更适合以下情况：

  1. 数据科学/Machine Learning：预装了 numpy、pandas、scikit-learn 等大量科学计算包
  2. 不想折腾环境：开箱即用，解决依赖冲突能力强
  3. 团队统一使用：如果团队都用 conda，保持一致
  4. 需要管理非 Python 依赖：conda 可以管理 C++ 库等

  ---
  我的建议

  | 你的需求            | 推荐                |
  |-----------------|-------------------|
  | Web 开发、脚本编写、自动化 | 直接安装 Python       |
  | 数据科学、ML、深度学习    | Anaconda          |
  | Docker 容器化部署    | 直接安装 Python（镜像更小） |
  | 初学者想快速上手        | Anaconda          |

  既然你已经用 Docker，说明对开发环境有一定理解，我建议直接安装 Python，用 venv 或 poetry 管理虚拟环境即可。这样更灵活，也更适合容器化部署。

> python是直接安装在window 路径下，还是在dock-desktop中的linux虚拟机环境中安装？

● 这是个很关键的问题！答案很明确：

  Python 应该安装在 Windows 上（宿主机）

  理解 Docker 的架构

  ┌─────────────────────────────────────────┐
  │           Windows (你的开发环境)          │
  │  ┌────────────────────────────────────┐ │
  │  │  Python 安装在这里                  │ │
  │  │  - VSCode/PyCharm 写代码            │ │
  │  │  - 本地测试、调试                   │ │
  │  └────────────────────────────────────┘ │
  │                                         │
  │  ┌────────────────────────────────────┐ │
  │  │  Docker Desktop                    │ │
  │  │  ┌──────────────────────────────┐ │ │
  │  │  │  Linux VM (WSL2)             │ │ │
  │  │  │  ┌────────────────────────┐  │ │ │
  │  │  │  │  Docker 容器           │  │ │ │
  │  │  │  │  (运行时环境)          │  │ │ │
  │  │  │  └────────────────────────┘  │ │ │
  │  │  └──────────────────────────────┘ │ │
  │  └────────────────────────────────────┘ │
  └─────────────────────────────────────────┘

  为什么不在 Docker 的 Linux VM 中安装？

  1. 开发 ≠ 运行
    - 开发环境：写代码、调试、测试（Windows）
    - 运行环境：Docker 容器部署（Linux VM）
  2. Docker 的 Linux VM 是被管理的
    - 它是 Docker 自己管理的，不适合手动安装软件
    - 重启 Docker Desktop 可能会重置某些配置
  3. 容器里的 Python 通过 Dockerfile 定义
    - 不需要手动在容器里安装
    - 构建镜像时自动安装

  正确的工作流

  # Dockerfile（定义容器里的 Python）
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY . .
  CMD ["python", "app.py"]

  # Windows 上开发
  python -m venv venv
  venv\Scripts\activate
  pip install -r requirements.txt
  python app.py              # 本地运行

  # 构建并运行容器
  docker build -t myapp .
  docker run myapp           # 容器运行

  总结

  | 环境        | 用途    | Python 来源                    |
  |-----------|-------|------------------------------|
  | Windows   | 开发、调试 | 直接安装 Python                  |
  | Docker 容器 | 生产部署  | Dockerfile 中 FROM python:xxx |

  简单说：你在 Windows 上装 Python 开发，Docker 容器里的 Python 是通过 Dockerfile 自动构建的，两套独立的环境，互不干扰。

> 如果我用docker启动postgres，那么我可以通过SQL语句操作postgres吗？能查看postgres中的数据吗？

● 当然可以！ 有多种方式操作 Docker 中的 PostgreSQL：

  方法 1：使用 docker exec 进入容器

  # 直接在容器中执行 psql
  docker exec -it <postgres容器名> psql -U postgres

  # 或者指定数据库
  docker exec -it <postgres容器名> psql -U postgres -d mydb

  进入后就可以直接执行 SQL：
  \dt                          -- 查看所有表
  SELECT * FROM users;         -- 查询数据
  \q                           -- 退出

  ---
  方法 2：在 Windows 上安装 PostgreSQL 客户端工具

  选项 A：安装 psql 命令行

  1. 下载 PostgreSQL 安装包，只安装命令行工具
  2. 连接到 Docker 中的数据库：

  psql -h localhost -p 5432 -U postgres -d mydb

  选项 B：使用图形化工具（推荐）

  | 工具        | 特点              |
  |-----------|-----------------|
  | DBeaver   | 免费、功能强大、支持多种数据库 |
  | pgAdmin 4 | PostgreSQL 官方工具 |
  | TablePlus | 界面简洁、收费但有免费版    |
  | DataGrip  | JetBrains 出品，收费 |

  以 DBeaver 为例：
  1. 下载安装 DBeaver
  2. 新建连接 → PostgreSQL
  3. 配置：
    - Host: localhost
    - Port: 5432
    - Database: mydb
    - Username: postgres
    - Password: 你的密码
  4. 连接后可以可视化查看表、执行 SQL

  ---
  方法 3：docker-compose 示例

  version: '3.8'
  services:
    postgres:
      image: postgres:16
      container_name: my-postgres
      environment:
        POSTGRES_USER: postgres
        POSTGRES_PASSWORD: mypassword
        POSTGRES_DB: mydb
      ports:
        - "5432:5432"    # 映射到宿主机
      volumes:
        - postgres_data:/var/lib/postgresql/data

  volumes:
    postgres_data:

  启动后：
  docker-compose up -d
  docker exec -it my-postgres psql -U postgres -d mydb

  ---
  常用 psql 命令

  -- 元命令（前面有反斜杠）
  \l                  -- 列出所有数据库
  \c mydb             -- 切换数据库
  \dt                 -- 列出当前数据库的表
  \d table_name       -- 查看表结构
  \du                 -- 列出所有用户
  \conninfo           -- 显示连接信息

  -- SQL 语句
  SELECT * FROM users WHERE id = 1;
  INSERT INTO users (name, email) VALUES ('Tom', 'tom@example.com');
  UPDATE users SET email = 'new@example.com' WHERE id = 1;
  DELETE FROM users WHERE id = 1;

  ---
  总结

  | 方式              | 适合场景       |
  |-----------------|------------|
  | docker exec     | 快速执行命令、调试  |
  | DBeaver/pgAdmin | 日常开发、可视化操作 |
  | 代码连接            | 应用程序访问数据库  |

  推荐：安装一个 DBeaver，既能可视化查看数据，又能执行 SQL，开发体验最好。

> DBeaver的下载网址是

● DBeaver 官网下载地址：

  https://dbeaver.io/download/

  下载步骤

  1. 打开官网后会自动识别你的操作系统
  2. 选择 Community 版本（免费，功能够用）
  3. 下载安装包

  快速选择

  | 系统      | 下载链接                                                  |
  |---------|-------------------------------------------------------|
  | Windows | https://dbeaver.io/files/dbeaver-ce-latest-stable.exe |
  | macOS   | https://dbeaver.io/files/dbeaver-ce-latest-stable.dmg |
  | Linux   | 在官网选择对应发行版                                            |

  ---
  安装后配置 PostgreSQL 连接

  1. 打开 DBeaver
  2. 点击 新建数据库连接 图标（或 Ctrl + Shift + N）
  3. 选择 PostgreSQL
  4. 配置连接信息：
    - Host: localhost
    - Port: 5432
    - Database: mydb（或你的数据库名）
    - Username: postgres
    - Password: 你的密码
  5. 点击 测试连接 → 成功后 完成

  连接成功后，你就能看到左侧的数据库树，可以浏览表、执行 SQL 查询了。
