# IGV Genome Browser Integration

## 概述

为 SNP Details 页面集成了 IGV (Integrative Genomics Viewer) 基因组浏览器，可视化显示 SNP 周围 50K 范围内的基因组区域。

## 功能特性

### 1. **自动区域检测**
- 以当前 SNP 为中心
- 显示 50K bp 范围（25K 上游 + 25K 下游）
- 窗口大小可通过 API 参数调整（1K - 1M bp）

### 2. **基因注释轨道**
- 显示范围内的所有基因
- 基因方向链信息 (+/-)
- 基因生物类型 (gene_biotype)
- 颜色：蓝色 (#6495ED)

### 3. **SNP 轨道**
- 显示范围内的所有 SNP
- 每个 SNP 的参考碱基和变异碱基
- 颜色：红色 (#FF0000)

### 4. **当前 SNP 高亮**
- 绿色标记当前查看的 SNP
- 颜色：绿色 (#00FF00)

## API 接口

### 获取区域数据

```
GET /snps/{snp_id}/region?window_size=50000
```

**参数：**
- `snp_id` (路径参数): SNP ID
- `window_size` (查询参数): 窗口大小，默认 50000 bp

**响应格式：**
```json
{
  "chrom": "1",
  "start": 1027616,
  "end": 1077616,
  "center_snp": {
    "id": 1,
    "snp_id": "rs110000388",
    "pos": 1077616,
    "ref": "C",
    "alt": "T"
  },
  "genes": [
    {
      "chrom": "1",
      "start": 1049895,
      "end": 1086098,
      "name": "GPR180",
      "gene_id": "ENSBTAG00000000003",
      "strand": "+",
      "gene_biotype": "protein_coding"
    }
  ],
  "snps": [
    {
      "chrom": "1",
      "start": 1077615,
      "end": 1077616,
      "name": "rs110000388",
      "snp_id": "rs110000388",
      "ref": "C",
      "alt": "T",
      "pos": 1077616
    }
  ],
  "total_genes": 1,
  "total_snps": 1
}
```

## 前端组件

### IG VBrowser 组件

**位置：** `frontend/src/components/IGVBrowser.vue`

**Props：**
- `snpId` (Number, required): SNP ID

**功能：**
- 自动加载区域数据
- 使用 igv.js 创建交互式基因组浏览器
- 支持缩放、平移、点击查看详情
- 响应式设计，加载状态提示

**使用示例：**
```vue
<template>
  <IG VBrowser :snp-id="currentSnp.id" />
</template>

<script setup>
import IG VBrowser from '@/components/IGVBrowser.vue'
</script>
```

## 数据库查询

### 查询范围内的基因

```sql
SELECT * FROM genes
WHERE chrom = ?
  AND start_pos <= ?
  AND end_pos >= ?
```

### 查询范围内的 SNP

```sql
SELECT * FROM snps
WHERE chrom = ?
  AND pos >= ?
  AND pos <= ?
```

## 参考基因组

### 基因组文件
- **文件：** `database/reference/ARS-UCD1.2_ChangeNamegenome.Chromosome.fasta`
- **版本：** ARS-UCD1.2
- **物种：** 牛 (*Bos taurus*)

### 基因注释
- **文件：** `database/reference/Bos_taurus.ARS-UCD1.2.110.gtf.gz`
- **来源：** Ensembl
- **版本：** 110
- **基因数量：** 27,607
- **转录本数量：** 43,984
- **外显子数量：** 433,820

## 使用说明

1. **在 SNP Details 页面查看**
   - 点击任意 SNP 查看详情
   - 滚动到 "Genomic Region Viewer (50K)" 部分
   - 等待数据加载（通常 < 2 秒）

2. **与 IGV 交互**
   - **缩放**：使用鼠标滚轮或拖动滑块
   - **平移**：拖动基因组标尺
   - **查看详情**：点击基因或 SNP 标记
   - **刷新数据**：点击 "Refresh" 按钮

3. **轨道说明**
   - 顶部轨道：基因注释（蓝色）
   - 中间轨道：所有 SNP（红色标记）
   - 底部轨道：当前查看的 SNP（绿色高亮）

## 性能优化

- **后端优化**
  - 使用索引字段查询（chrom, start_pos, end_pos）
  - 单次数据库查询获取所有数据
  - 坐标格式转换（1-based 转 0-based for BED）

- **前端优化**
  - 懒加载组件（仅在需要时创建 IGV）
  - 组件销毁时清理 IGV 实例
  - 加载状态提示

## 依赖项

### 前端
```json
{
  "igv": "^2.15.0"
}
```

### 后端
- SQLAlchemy ORM
- PostgreSQL 数据库
- Fast API 框架

## 已知限制

1. **基因组浏览器限制**
   - 需要手动添加参考基因组轨道（目前使用简化版本）
   - 不支持实时序列查看
   - 染色体名称需要添加 'chr' 前缀

2. **性能限制**
   - 大窗口（>1M bp）可能导致渲染变慢
   - SNP 密度高的区域可能显示拥挤

## 未来改进

1. **参考基因组集成**
   - 添加 FASTA 参考序列轨道
   - 支持 GC 含量查看
   - 序列提取和下载

2. **更多数据轨道**
   - UTR 区域注释
   - 外显子/内含子详细视图
   - CpG 岛标记

3. **交互增强**
   - 点击 SNP 导航到详情
   - 右键菜单提供更多操作
   - 自定义轨道颜色和样式

4. **导出功能**
   - 导出区域为图片
   - 导出 BED 文件
   - 导出基因组序列

## 故障排除

### IGV 不显示
1. 检查浏览器控制台错误
2. 确认 SNP ID 有效
3. 验证后端 API 响应
4. 检查网络连接

### 数据不完整
1. 确认数据库中有基因和 SNP 数据
2. 检查坐标系统一致性
3. 验证染色体名称格式

### 性能问题
1. 减小窗口大小
2. 清除浏览器缓存
3. 重启后端服务

## 相关文档

- [IGV.js 官方文档](https://github.com/igvteam/igv.js)
- [BED 格式规范](https://genome.ucsc.edu/FAQ/FAQformat.html#format1)
- [GENE_ANNOTATION_FEATURE.md](./GENE_ANNOTATION_FEATURE.md)
- [SNP_REGION_FEATURE.md](./SNP_REGION_FEATURE.md)
