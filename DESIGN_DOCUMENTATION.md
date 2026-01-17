# 牛SNP效应值数据库 - 设计文档

## Cattle SNP Effect Value Database - Design Documentation

---

## 1. 项目概述 / Project Overview

### 1.1 项目背景
本项目旨在构建一个前后端分离的牛变异效应值数据库系统，用于存储、查询和展示牛SNP（单核苷酸多态性）对578个组织/细胞类型的表观效应大小数据。

### 1.2 核心功能
- SNP基础信息查询（染色体、位置、参考/变异碱基）
- SNP搜索（支持chr:position格式和rsID）
- SNP详细效应值查看
- 分页、排序功能
- 数据库统计信息展示

---

## 2. 数据库设计 / Database Design

### 2.1 数据库选型
**选择：PostgreSQL**

**理由：**
1. 支持JSONB数据类型，便于存储灵活的元数据
2. 优秀的全文搜索能力
3. 高级索引选项（GIN、GiST）
4. 物化视图支持查询优化
5. 更好的并发处理能力

### 2.2 ER图

```
┌─────────────────┐
│    TARGETS      │
├─────────────────┤
│ id (PK)         │
│ name            │
│ category        │
│ description     │
│ metadata (JSONB)│
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────┴────────┐         ┌─────────────────┐
│  SNP_EFFECTS    │         │     SNPS        │
├─────────────────┤         ├─────────────────┤
│ id (PK)         │    N:1  │ id (PK)         │
│ snp_id (FK)     │◄────────│ chrom           │
│ target_id (FK)  │         │ pos             │
│ effect_value    │         │ rs_id           │
│ created_at      │         │ ref_allele      │
└─────────────────┘         │ alt_allele      │
                            │ max_abs_sad     │
                            │ created_at      │
                            │ updated_at      │
                            └─────────────────┘
```

### 2.3 表结构说明

#### SNPS表 - SNP基础信息
| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键 |
| chrom | VARCHAR(10) | 染色体 (chr1-chr29, chrX) |
| pos | BIGINT | 染色体位置 |
| rs_id | VARCHAR(100) | dbSNP标识符 |
| ref_allele | VARCHAR(10) | 参考碱基 |
| alt_allele | VARCHAR(10) | 变异碱基 |
| max_abs_sad | FLOAT | 最大绝对SAD值 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

#### TARGETS表 - 靶点（组织/细胞类型）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键 |
| name | VARCHAR(255) | 靶点名称（唯一） |
| category | VARCHAR(100) | 类别（组织/细胞类型等） |
| description | TEXT | 描述信息 |
| metadata | JSONB | 扩展元数据 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

#### SNP_EFFECTS表 - SNP效应值
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGSERIAL | 主键 |
| snp_id | INTEGER | SNP ID（外键） |
| target_id | INTEGER | 靶点ID（外键） |
| effect_value | FLOAT | 效应值 |
| created_at | TIMESTAMP | 创建时间 |

### 2.4 索引设计

| 表名 | 索引名 | 字段 | 类型 | 用途 |
|------|--------|------|------|------|
| SNPS | idx_snps_chrom_pos | chrom, pos | B-tree | 按染色体位置查询 |
| SNPS | idx_snps_rs_id | rs_id | B-tree | 按rsID查询 |
| SNPS | idx_snps_max_abs_sad | max_abs_sad | B-tree | 按效应值排序 |
| SNP_EFFECTS | idx_snp_effects_snp_id | snp_id | B-tree | 关联查询优化 |
| SNP_EFFECTS | idx_snp_effects_target_id | target_id | B-tree | 按靶点查询 |
| SNP_EFFECTS | idx_snp_effects_value | effect_value | B-tree | 效应值范围查询 |

---

## 3. 后端API设计 / Backend API Design

### 3.1 技术栈
- **框架**: FastAPI 0.109.0
- **数据库**: SQLAlchemy 2.0 + PostgreSQL
- **数据验证**: Pydantic 2.5
- **ASGI服务器**: Uvicorn

### 3.2 API端点

#### 基础接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | / | API根路径 |
| GET | /health | 健康检查 |
| GET | /docs | Swagger API文档 |

#### SNP接口

| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| GET | /snps | page, page_size, sort_by, sort_order | 分页获取SNP列表 |
| GET | /snps/search | query, page, page_size | 搜索SNP |
| GET | /snps/{id} | id | 获取SNP详情 |

#### 靶点接口

| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| GET | /targets | skip, limit | 获取靶点列表 |

#### 统计接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /stats | 获取数据库统计信息 |

### 3.3 响应格式

**成功响应示例:**
```json
{
  "total": 47,
  "page": 1,
  "page_size": 20,
  "total_pages": 3,
  "data": [
    {
      "id": 1,
      "chrom": "chr15",
      "pos": 15449431,
      "rs_id": "rs1115118696",
      "ref_allele": "C",
      "alt_allele": "T",
      "max_abs_sad": 0.328275,
      "created_at": "2024-01-14T10:00:00Z"
    }
  ]
}
```

**错误响应示例:**
```json
{
  "error": "http_error",
  "message": "SNP not found",
  "status_code": 404
}
```

---

## 4. 前端设计 / Frontend Design

### 4.1 技术栈
- **框架**: Vue 3 (Composition API)
- **UI组件库**: Element Plus
- **构建工具**: Vite 5
- **HTTP客户端**: Axios
- **路由**: Vue Router 4

### 4.2 页面结构

```
┌─────────────────────────────────────────┐
│           页面头部                       │
│       牛SNP效应值数据库                   │
├─────────────────────────────────────────┤
│           统计卡片                       │
│    SNP数 | 靶点数 | 效应值记录数          │
├─────────────────────────────────────────┤
│           搜索栏                         │
│    [搜索框 chr:位置 或 rsID] [每页数量]   │
├─────────────────────────────────────────┤
│           数据表格                       │
│  ID | 染色体 | 位置 | rsID | 碱基 | SAD值 │
├─────────────────────────────────────────┤
│           分页组件                       │
│         « 1 2 3 ... 10 »                │
└─────────────────────────────────────────┘
```

### 4.3 组件结构

```
src/
├── main.js                 # 应用入口
├── App.vue                 # 根组件
├── router/
│   └── index.js            # 路由配置
├── services/
│   └── api.js              # API服务封装
├── views/
│   └── SNPTableView.vue    # SNP列表视图
└── styles/
    └── main.css            # 全局样式
```

### 4.4 响应式设计
- 桌面端：全宽展示，表格完整显示
- 平板端：自适应布局，表格可横向滚动
- 移动端：单列布局，优化触摸操作

---

## 5. 数据导入流程 / Data Import Flow

### 5.1 数据格式
TSV文件，制表符分隔：
```
chrom	pos	id	ref	alt	max_abs_sad	0986_CD4.norRPKM	...
chr15	15449431	rs1115118696	C	T	0.328275	0.026892	...
```

### 5.2 导入步骤
1. 解析TSV文件头，识别SNP列和效应值列
2. 导入靶点数据（578个组织/细胞类型）
3. 批量导入SNP基础信息
4. 批量导入效应值数据
5. 刷新物化视图
6. 记录导入日志

### 5.3 性能优化
- 使用批量插入（batch_size=1000）
- 利用PostgreSQL的ON CONFLICT进行upsert
- 定期提交事务
- 进度条显示

---

## 6. 部署方案 / Deployment

### 6.1 Docker Compose架构

```
┌─────────────────────────────────────────┐
│              Nginx (Frontend)           │
│                   :80                    │
└─────────────────┬───────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│            FastAPI (Backend)            │
│                   :8000                  │
└─────────────────┬───────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│          PostgreSQL (Database)          │
│                   :5432                  │
└─────────────────────────────────────────┘
```

### 6.2 启动命令

```bash
# 启动所有服务
docker-compose up -d

# 导入数据
docker-compose --profile import up data-import

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 6.3 环境变量

| 服务 | 变量名 | 默认值 |
|------|--------|--------|
| Backend | DATABASE_URL | postgresql://cattle_user:cattle_pass@db:5432/cattle_snp_db |
| Frontend | VITE_API_BASE_URL | http://localhost:8000 |
| Database | POSTGRES_USER | cattle_user |
| Database | POSTGRES_PASSWORD | cattle_pass |
| Database | POSTGRES_DB | cattle_snp_db |

---

## 7. 扩展性设计 / Extensibility

### 7.1 预留扩展能力

1. **结构变异(SV)数据表**
   ```sql
   CREATE STRUCTURAL_VARIANTS (
       id SERIAL PRIMARY KEY,
       sv_type VARCHAR(50),  -- DEL, DUP, INV, TRA
       chrom VARCHAR(10),
       start_pos BIGINT,
       end_pos BIGINT,
       ...
   );
   ```

2. **多种效应值指标**
   - 添加新的effect_type字段
   - 支持不同算法的效应值

3. **外部数据关联**
   - 基因注释表 (GENES)
   - 疾病关联表 (DISEASES)
   - QTL关联表 (QTLS)

### 7.2 API扩展点
- 预留效应值筛选接口
- 预留组织特异性查询接口
- 预留批量查询接口

---

## 8. 性能优化建议 / Performance Optimization

### 8.1 数据库层
- 定期VACUUM和ANALYZE
- 考虑分区表（按染色体）
- 使用连接池
- 缓存热点数据

### 8.2 应用层
- 实现Redis缓存
- 使用异步处理
- 限流和降级

### 8.3 前端层
- 虚拟滚动（大数据量）
- 请求防抖
- 离线缓存

---

## 9. 安全建议 / Security Recommendations

1. 使用HTTPS部署
2. 添加API认证（如JWT）
3. CORS配置白名单
4. SQL注入防护（使用参数化查询）
5. 限流防爬虫

---

## 10. 项目文件结构 / Project Structure

```
cattleVarDB/
├── database/
│   └── schema.sql              # 数据库结构定义
├── backend/
│   ├── main.py                 # FastAPI应用
│   ├── import_data.py          # 数据导入脚本
│   ├── requirements.txt        # Python依赖
│   └── Dockerfile              # 后端镜像
├── frontend/
│   ├── src/
│   │   ├── main.js             # 应用入口
│   │   ├── App.vue             # 根组件
│   │   ├── router/             # 路由配置
│   │   ├── views/              # 页面组件
│   │   ├── services/           # API服务
│   │   └── styles/             # 样式文件
│   ├── index.html              # HTML模板
│   ├── vite.config.js          # Vite配置
│   ├── nginx.conf              # Nginx配置
│   ├── package.json            # Node依赖
│   └── Dockerfile              # 前端镜像
├── SNP-disease/
│   └── variant_sad_all_targets.tsv  # 原始数据文件
├── docker-compose.yml          # Docker编排配置
└── DESIGN_DOCUMENTATION.md     # 本文档
```

---

## 11. 快速开始 / Quick Start

### 本地开发

```bash
# 1. 启动数据库
docker-compose up -d db

# 2. 初始化数据库
psql -h localhost -U cattle_user -d cattle_snp_db -f database/schema.sql

# 3. 启动后端
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# 4. 启动前端
cd frontend
npm install
npm run dev

# 5. 导入数据
cd backend
python import_data.py --file ../SNP-disease/variant_sad_all_targets.tsv
```

### Docker部署

```bash
# 启动所有服务
docker-compose up -d

# 导入数据
docker-compose --profile import up data-import

# 访问应用
# 前端: http://localhost
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

---

**文档版本**: 1.0.0
**最后更新**: 2024-01-14

