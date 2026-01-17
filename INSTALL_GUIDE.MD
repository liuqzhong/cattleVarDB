# 软件安装详细指南

## Cattle SNP Effect Value Database - Software Installation Guide

本文档详细说明每个软件的安装步骤，包括下载、安装配置和验证。

---

## 目录

1. [软件安装顺序](#软件安装顺序)
2. [Git 安装](#1-git-安装)
3. [VS Code 安装](#2-vs-code-安装)
4. [Docker Desktop 安装](#3-docker-desktop-安装)
5. [PostgreSQL 安装](#4-postgresql-安装)
6. [Python 安装](#5-python-安装)
7. [Node.js 安装](#6-nodejs-安装)
8. [完整启动流程](#完整启动流程)

---

## 软件安装顺序

建议按以下顺序安装软件：

```
1. Git (版本控制)
2. VS Code (代码编辑器)
3. Docker Desktop (容器化 - 可选，推荐)
4. PostgreSQL (数据库)
5. Python (后端开发)
6. Node.js (前端开发)
```

---

## 1. Git 安装

### 1.1 下载 Git

1. 访问 Git 官网: **https://git-scm.com/downloads**
2. 点击 **Windows** 下载按钮
3. 下载文件名类似: `Git-2.47.0-64-bit.exe`

### 1.2 安装步骤

双击下载的安装程序，按以下步骤操作：

| 步骤 | 说明 | 选择 |
|------|------|------|
| 1 | 欢迎界面 | 点击 "Next" |
| 2 | 安装路径 | 默认 `C:\Program Files\Git`，点击 "Next" |
| 3 | 选择组件 | 勾选: Git Bash Here, Git GUI Here |
| 4 | 开始菜单 | 默认，点击 "Next" |
| 5 | 默认编辑器 | 选择 VS Code (推荐) 或 Vim |
| 6 | PATH 环境 | **选择 "Git from the command line"** |
| 7 | HTTPS 后端 | 选择 "Use native Windows Secure Channel" |
| 8 | 行尾符 | 选择 "Checkout Windows-style, commit Unix-style" |
| 9 | 终端模拟 | 选择 "Use Windows' default console" |
| 10 | git pull | 选择 "Default (fast-forward or merge)" |
| 11 | 凭证助手 | 选择 "Enable credential manager" |
| 12 | 额外选项 | 勾选 "Enable file system caching" |
| 13 | 安装 | 点击 "Install"，等待完成 |
| 14 | 完成 | 点击 "Finish" |

### 1.3 验证安装

打开 **命令提示符 (CMD)** 或 **PowerShell**：

```bash
git --version
# 应显示: git version 2.47.0.windows.x
```

### 1.4 配置 Git

```bash
# 设置用户名
git config --global user.name "Your Name"

# 设置邮箱
git config --global user.email "your.email@example.com"
```

---

## 2. VS Code 安装

### 2.1 下载 VS Code

1. 访问 VS Code 官网: **https://code.visualstudio.com/**
2. 点击 **Download for Windows**
3. 下载文件名: `VSCodeUserSetup-x64.exe`

### 2.2 安装步骤

| 步骤 | 说明 | 选择 |
|------|------|------|
| 1 | 欢迎界面 | 勾选"我同意协议"，点击"下一步" |
| 2 | 安装路径 | 默认，点击"下一步" |
| 3 | 开始菜单 | 默认，点击"下一步" |
| 4 | 上下文菜单 | **全部勾选** |
| 5 | PATH | **勾选"添加到 PATH"** |
| 6 | 安装 | 点击"安装" |
| 7 | 完成 | 点击"完成" |

### 2.3 安装推荐插件

1. 启动 VS Code
2. 点击左侧 **扩展** 图标 (或按 `Ctrl+Shift+X`)
3. 搜索并安装以下插件：

| 插件名 | 发布者 | 说明 |
|--------|--------|------|
| Python | Microsoft | Python 语言支持 |
| Pylance | Microsoft | Python 智能提示 |
| Vue - Official | Vue | Vue 3 语言支持 |
| ESLint | Microsoft | 代码检查 |
| Prettier | Prettier | 代码格式化 |
| PostgreSQL | Chris Kolkman | 数据库管理 |

---

## 3. Docker Desktop 安装

> 如果不想使用 Docker，可以跳过此步骤，直接安装 PostgreSQL。

### 3.1 系统要求

- Windows 10/11 专业版或企业版 (64位)
- 启用 WSL 2
- 至少 4GB 内存

### 3.2 下载 Docker Desktop

1. 访问 Docker 官网: **https://www.docker.com/products/docker-desktop/**
2. 点击 **Download for Windows**
3. 下载文件名: `Docker Desktop Installer.exe`

### 3.3 安装步骤

| 步骤 | 说明 | 选择 |
|------|------|------|
| 1 | 启动安装 | 双击安装程序 |
| 2 | 安装选项 | **勾选"Use WSL 2 based engine"** |
| 3 | 安装 | 点击"Ok"，等待完成 |
| 4 | 重启 | 点击"Close and restart" |

### 3.4 首次启动

1. Docker Desktop 自动启动
2. 接受服务协议
3. 选择"免费使用"
4. 等待 Docker 引擎启动（系统托盘出现图标）

### 3.5 验证安装

```bash
docker --version
# 应显示: Docker version 24.0.x

docker ps
# 应显示: CONTAINER ID   IMAGE   COMMAND   CREATED   STATUS   PORTS   NAMES
```

### 3.6 启动 PostgreSQL 容器

```bash
# Windows CMD
docker run -d --name cattle_db -p 5432:5432 ^
  -e POSTGRES_USER=cattle_user ^
  -e POSTGRES_PASSWORD=cattle_pass ^
  -e POSTGRES_DB=cattle_snp_db ^
  postgres:15-alpine


docker run -d --name cattle_db -p 5432:5432
  -e POSTGRES_USER=lqz
  -e POSTGRES_PASSWORD=35jn645x
  -e POSTGRES_DB=cattle_disease_snps_db
  postgres:15-alpine

# Windows PowerShell
docker run -d --name cattle_var_db -p 5432:5432 `
  -e POSTGRES_USER=cattle_user `
  -e POSTGRES_PASSWORD=cattle_pass `
  -e POSTGRES_DB=cattle_snp_db `
  postgres:15-alpine
```

---

## 4. PostgreSQL 安装

> 如果已使用 Docker 运行 PostgreSQL，可跳过此部分。

### 4.1 下载 PostgreSQL

1. 访问 PostgreSQL 官网: **https://www.postgresql.org/download/windows/**
2. 点击 **Download the installer**
3. 选择版本 **15.x**
4. 下载文件名: `postgresql-15.x-1-windows-x64.exe`

### 4.2 安装步骤

| 步骤 | 说明 | 选择 |
|------|------|------|
| 1 | 启动安装 | 双击安装程序，点击"Next" |
| 2 | 安装路径 | 默认，点击"Next" |
| 3 | 组件选择 | **全部勾选** (Server, pgAdmin, Tools) |
| 4 | 数据目录 | 默认，点击"Next" |
| 5 | 设置密码 | **为 postgres 用户设置密码（记住！）** |
| 6 | 端口 | 默认 5432，点击"Next" |
| 7 | 区域设置 | 选择"Chinese"或"English" |
| 8 | 安装 | 点击"Next"，等待完成 |
| 9 | 完成 | 点击"Finish" |

### 4.3 创建数据库

打开 **SQL Shell (psql)**：

```sql
-- 输入 postgres 密码
-- 然后执行以下命令:

CREATE USER cattle_user WITH PASSWORD 'cattle_pass';
CREATE DATABASE cattle_snp_db OWNER cattle_user;
GRANT ALL PRIVILEGES ON DATABASE cattle_snp_db TO cattle_user;
\q
```

### 4.4 验证安装

```bash
psql -h localhost -U cattle_user -d cattle_snp_db
# 输入密码: cattle_pass
```

---

## 5. Python 安装

### 5.1 下载 Python

1. 访问 Python 官网: **https://www.python.org/downloads/**
2. 点击 **Download Python 3.12.x**
3. 下载文件名: `python-3.12.x-amd64.exe`

### 5.2 安装步骤

| 步骤 | 说明 | 选择 |
|------|------|------|
| 1 | 启动安装 | **重要：勾选"Add Python to PATH"** |
| 2 | 安装方式 | 选择"Install Now"或"Customize installation" |
| 2a | 自定义组件 | 全部勾选 (pip, tcl/tk, test suite) |
| 3 | 高级选项 | **勾选"Add to environment variables"** |
| 4 | 安装 | 点击"Install" |
| 5 | 完成 | 点击"Close" |

### 5.3 验证安装

**重新打开命令提示符**（重要！）

```bash
python --version
# 应显示: Python 3.12.x

pip --version
# 应显示: pip 24.x.x
```

### 5.4 配置后端环境

```bash
# 进入后端目录
cd D:\CCProject\VEP\cattleVarDB\backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows CMD:
venv\Scripts\activate.bat
# Windows PowerShell:
venv\Scripts\Activate.ps1

# 升级 pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### 5.5 创建 .env 文件

```bash
# 在 backend 目录创建 .env 文件
echo DATABASE_URL=postgresql://cattle_user:cattle_pass@localhost:5432/cattle_snp_db > .env
echo LOG_LEVEL=info >> .env
```

---

## 6. Node.js 安装

### 6.1 下载 Node.js

1. 访问 Node.js 官网: **https://nodejs.org/**
2. 选择 **LTS** 版本（推荐）
3. 下载文件名: `node-v20.x.x-x64.msi`

### 6.2 安装步骤

| 步骤 | 说明 | 选择 |
|------|------|------|
| 1 | 启动安装 | 双击 MSI 安装程序 |
| 2 | 许可协议 | 勾选"接受协议"，点击"Next" |
| 3 | 安装路径 | 默认，点击"Next" |
| 4 | 自定义安装 | **勾选"Add to PATH"** |
| 5 | 构建工具 | **勾选"Automatically install tools"** |
| 6 | 安装 | 点击"Install" |
| 7 | C++ 工具 | 点击"是"（如提示） |
| 8 | 完成 | 点击"Finish" |

### 6.3 验证安装

**重新打开命令提示符**（重要！）

```bash
node --version
# 应显示: v20.x.x

npm --version
# 应显示: 10.x.x
```

### 6.4 配置前端环境

```bash
# 进入前端目录
cd D:\CCProject\VEP\cattleVarDB\frontend

# 设置淘宝镜像（可选，国内推荐）
npm config set registry https://registry.npmmirror.com

# 安装依赖
npm install
```

---

## 完整启动流程

### 第一步：启动数据库

**使用 Docker:**
```bash
docker start cattle_db
```

**使用本地 PostgreSQL:**
确保 PostgreSQL 服务正在运行（Windows 服务中）

---

### 第二步：初始化数据库

```bash
# 使用 psql
psql -h localhost -U cattle_user -d cattle_snp_db -f database/schema.sql

# 或使用 Docker
docker exec -i cattle_db psql -U cattle_user -d cattle_snp_db < database/schema.sql
```

---

### 第三步：启动后端

```bash
cd D:\CCProject\VEP\cattleVarDB\backend
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000 验证

---

### 第四步：导入数据（可选）

```bash
cd D:\CCProject\VEP\cattleVarDB\backend
venv\Scripts\activate
python import_data.py --file ../SNP-disease/variant_sad_all_targets.tsv
```

---

### 第五步：启动前端

```bash
cd D:\CCProject\VEP\cattleVarDB\frontend
npm run dev
```

访问 http://localhost:5173

---

## 开发端口

| 服务 | 端口 | 地址 |
|------|------|------|
| 前端 | 5173 | http://localhost:5173 |
| 后端 API | 8000 | http://localhost:8000 |
| API 文档 | 8000 | http://localhost:8000/docs |
| PostgreSQL | 5432 | localhost:5432 |

---

## 故障排查

### Python 命令不识别
```bash
# 确保勾选了 "Add Python to PATH"
# 或手动添加到环境变量
```

### PowerShell 无法激活虚拟环境
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### npm install 失败
```bash
npm cache clean --force
npm config set registry https://registry.npmmirror.com
npm install
```

---

**文档版本**: 2.0.0
**最后更新**: 2024-01-14



> 也就是说，用户不需要安装本地任何环境软件，操作Docker中的环境软件，也能完成本地开发，是吗？总之，
用户完全能操作Docker中的所有软件环境，请纠正我说的错误地方

● 纠正您的理解

  您的理解基本正确，但有几个关键点需要澄清：

  ---
  必须安装在本地的软件

  1. Docker Desktop ✅ 必须

  Docker Desktop 是必须安装在本地系统的软件
  它是一个"容器运行环境"，类似于"虚拟机软件"
  没有它，就无法运行任何Docker容器

  2. 代码编辑器 ✅ 必须（或强烈推荐）

  VS Code / 其他编辑器 必须/强烈推荐安装

  虽然理论上可以用 Windows 记事本写代码，但：
  - 没有语法高亮
  - 没有代码提示
  - 没有错误检查
  - 开发效率极低（几乎不可行）

  3. 浏览器 ✅ 通常已有

  用于查看前端应用
  通常系统自带（Edge/Chrome）

  ---
  可以用 Docker 替代的软件

  | 软件          | 是否必须本地安装 | Docker 替代方案                  |
  |-------------|----------|------------------------------|
  | PostgreSQL  | ❌ 不需要    | docker run postgres          |
  | Python      | ⚠️ 可选    | docker run python，但本地开发仍推荐安装 |
  | Node.js     | ⚠️ 可选    | docker run node，但本地开发仍推荐安装   |
  | MySQL/Redis | ❌ 不需要    | docker run mysql/redis       |

  ---
  完整对比

  方案 A：最小化安装（Docker 为主）

  必须安装:
  ├── Docker Desktop        ✅ 必须安装
  ├── VS Code              ✅ 必须安装
  └── 浏览器               ✅ 通常已有

  用 Docker 运行:
  ├── PostgreSQL           ✅ 容器运行
  ├── Python              ⚠️ 可以容器，但本地安装更方便
  └── Node.js             ⚠️ 可以容器，但本地安装更方便

  方案 B：传统本地安装（不用 Docker）

  必须安装:
  ├── PostgreSQL          ✅ 本地安装
  ├── Python             ✅ 本地安装
  ├── Node.js            ✅ 本地安装
  ├── VS Code            ✅ 本地安装
  └── 浏览器             ✅ 通常已有

  方案 C：混合模式（推荐）

  必须安装:
  ├── Docker Desktop      ✅ 本地安装
  ├── Python             ✅ 本地安装（运行后端代码）
  ├── Node.js            ✅ 本地安装（运行前端代码）
  ├── VS Code            ✅ 本地安装
  └── 浏览器             ✅ 通常已有

  用 Docker 运行:
  └── PostgreSQL         ✅ 容器运行（只需数据库）

  ---
  为什么 Python/Node.js 仍推荐本地安装？

  虽然可以用 Docker 容器运行 Python/Node.js，但本地开发时安装它们更方便：

  | 功能            | 本地安装   | Docker 容器  |
  |---------------|--------|------------|
  | 热重载（代码改动自动刷新） | ✅ 支持   | ⚠️ 需额外配置   |
  | 调试（断点调试）      | ✅ 方便   | ❌ 麻烦       |
  | VS Code 集成    | ✅ 原生支持 | ⚠️ 需配置远程开发 |
  | 启动速度          | ✅ 快    | ⚠️ 稍慢      |
  | 多项目切换         | ✅ 方便   | ⚠️ 需管理容器   |

  ---
  结论：纠正您的说法

  您说的：

  "用户不需要安装本地任何环境软件，操作Docker中的环境软件，也能完成本地开发"

  纠正后：

  用户必须安装:
  ✅ Docker Desktop（容器运行环境）
  ✅ 代码编辑器（VS Code 或其他）
  ✅ 浏览器（查看应用）

  用户不需要安装:
  ❌ PostgreSQL（用 Docker 容器替代）
  ⚠️ Python/Node.js（虽然可以用 Docker，但本地安装开发体验更好）

  所以准确说法是:
  "用户只需安装 Docker Desktop 和代码编辑器，数据库用 Docker 运行，
  即可完成本地开发。Python/Node.js 本地安装会更方便。"

  ---
  开发环境安装对比

  | 方案       | 本地安装软件数 | Docker 容器数 | 推荐度   |
  |----------|---------|------------|-------|
  | 纯 Docker | 2 个     | 3+ 个       | ⭐⭐⭐   |
  | 混合模式     | 4 个     | 1 个        | ⭐⭐⭐⭐⭐ |
  | 纯本地      | 5 个     | 0 个        | ⭐⭐⭐⭐  |

  ---
  总结

  您的理解大方向正确，但需要明确：

  1. ✅ Docker 本身必须安装在本地
  2. ✅ 代码编辑器必须安装在本地
  3. ✅ 数据库可以完全用 Docker，不需要本地安装
  4. ⚠️ Python/Node.js 技术上可以用 Docker，但本地安装开发体验更好

  最简洁的回答：
  用户需要安装 Docker Desktop + 代码编辑器，然后可以用 Docker 运行 PostgreSQL 完成数据库相关开发。Python/Node.js 本地安装会更方便，但不是绝对必须。

  这样理解是否更清晰？
