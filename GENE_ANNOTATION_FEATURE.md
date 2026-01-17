# SNP Gene Annotation Feature
# SNP 基因注释功能

## 概述

为 SNP Details 页面添加了最近基因信息显示功能。该功能通过解析 Ensembl 基因组注释文件（GTF格式），将 SNP 与最近的基因关联，为用户提供更全面的基因组上下文信息。

## 实现细节

### 1. 数据库层

#### Gene Model (`backend/main.py`)
```python
class GeneModel(Base):
    """基因注释表"""
    __tablename__ = "genes"

    id = Column(Integer, primary_key=True, index=True)
    gene_id = Column(String(50), nullable=False, unique=True, index=True)
    gene_name = Column(String(255), nullable=True)
    chrom = Column(String(50), nullable=False, index=True)
    start_pos = Column(BigInteger, nullable=False)
    end_pos = Column(BigInteger, nullable=False)
    strand = Column(String(1), nullable=True)
    gene_biotype = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 2. 基因数据导入

#### 导入脚本 (`backend/import_genes.py`)
- 解析 GTF 文件（支持 gzipped 格式）
- 提取基因记录（feature type = "gene"）
- 提取基因属性：
  - `gene_id`: Ensembl 基因 ID
  - `gene_name`: 基因名称
  - `chrom`: 染色体
  - `start_pos`: 起始位置
  - `end_pos`: 结束位置
  - `strand`: 链方向（+/-）
  - `gene_biotype`: 基因生物类型

#### 使用方法
```bash
cd backend
python import_genes.py
```

#### 导入结果
- 成功导入 **27,607** 个牛基因注释
- 数据来源：Ensembl Bos taurus ARS-UCD1.2.110

### 3. API 层

#### 查找最近基因函数 (`find_nearest_gene`)
```python
def find_nearest_gene(db: Session, chrom: str, pos: int) -> Optional[dict]:
```

**算法逻辑**：
1. **优先查找包含 SNP 的基因**
   - 查找 `gene_start <= SNP_pos <= gene_end`
   - 如果找到，返回距离 = 0，location = "within"

2. **查找最近的基因**
   - 查找 SNP 之前的最近基因（基因结束位置 < SNP 位置）
   - 查找 SNP 之后的最近基因（基因起始位置 > SNP 位置）
   - 选择距离更近的基因
   - 返回实际距离，location = "nearby"

#### API 响应更新 (`SNPDetailResponse`)
```python
class SNPDetailResponse(SNPResponse):
    effect_values: List[dict]
    nearest_gene: Optional[dict] = Field(default=None, description="最近的基因信息")
```

**示例响应**：
```json
{
  "nearest_gene": {
    "gene_id": "ENSBTAG00000007913",
    "gene_name": "CWC15",
    "chrom": "15",
    "start_pos": 15447722,
    "end_pos": 15456214,
    "strand": "+",
    "distance": 0,
    "gene_biotype": "protein_coding",
    "location": "within"
  }
}
```

### 4. 前端层

#### SNP 详情页面更新 (`frontend/src/views/SNPTableView.vue`)

**显示内容**：
1. **基因名称**：大标签显示，如果有 gene_name 显示名称，否则显示 gene_id
2. **位置标记**：
   - "Within Gene"（蓝色标签）：SNP 在基因内部
   - "Nearby X bp"（灰色标签）：SNP 在基因附近，显示距离
3. **基因详情**：
   - Gene ID：Ensembl 基因标识符
   - Location：染色体位置（起始-结束）和链方向
   - Biotype：基因生物类型（如 protein_coding）

**样式特性**：
- 绿色成功框突出显示基因信息
- 左侧绿色边框标识详情区域
- 响应式布局，适配不同屏幕尺寸

## 数据库性能优化

### 索引创建
```sql
CREATE INDEX idx_genes_chrom_start ON genes(chrom, start_pos);
CREATE INDEX idx_genes_chrom_end ON genes(chrom, end_pos);
CREATE INDEX idx_genes_name ON genes(gene_name);
```

这些索引确保：
- 快速查找特定染色体上的基因
- 高效的范围查询（start_pos, end_pos）
- 基因名称快速搜索

## 测试示例

### 示例 1：SNP 在基因内
**SNP**: rs1115118696 (Chr15:15449431)
**最近基因**: CWC15 (ENSBTAG00000007913)
**位置**: Chr15:15447722-15456214
**关系**: Within Gene（在基因内）

### 示例 2：SNP 在基因间
**SNP**: (假设位置 Chr15:10000000，在基因之间)
**最近基因**: (距离最近的基因)
**关系**: Nearby (显示具体距离)

## 使用场景

1. **功能基因组学研究**：
   - 了解 SNP 位于哪个基因内部或附近
   - 分析 SNP 对基因功能的潜在影响

2. **变异注释**：
   - 为 SNP 提供基因上下文信息
   - 辅助判断 SNP 的功能意义

3. **数据可视化**：
   - 直观显示 SNP 与基因的关系
   - 帮助研究者快速理解 SNP 位置

## 未来扩展

可能的改进方向：

1. **多基因支持**：
   - 显示多个附近的基因（前 5 个）
   - 支持基因重叠区域

2. **基因功能注释**：
   - 集成 GO (Gene Ontology) 信息
   - 添加通路（Pathway）信息

3. **可视化增强**：
   - 基因组浏览器集成
   - 交互式基因图谱

4. **批量查询**：
   - 支持批量 SNP 基因注释
   - 基因富集分析

## 技术栈

- **后端**: FastAPI + SQLAlchemy + PostgreSQL
- **前端**: Vue 3 + Element Plus
- **数据源**: Ensembl Bos taurus ARS-UCD1.2.110
- **基因数量**: 27,607 个蛋白编码基因和非编码 RNA 基因

## 维护说明

### 更新基因注释
当新版本的基因组注释可用时：

1. 下载新的 GTF 文件到 `database/reference/`
2. 清空现有基因表：
   ```sql
   DROP TABLE IF EXISTS genes CASCADE;
   ```
3. 重新运行导入脚本：
   ```bash
   python import_genes.py
   ```

### 数据备份
基因表数据包含在 PostgreSQL 数据库中，随常规数据库备份一起保存。
