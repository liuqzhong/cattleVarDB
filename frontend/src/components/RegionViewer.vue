<template>
  <div class="region-viewer">
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>Loading genomic data...</span>
    </div>

    <div v-if="error" class="error-container">
      <el-alert type="error" :title="error" :closable="false" />
    </div>

    <!-- IGV 风格基因组可视化 -->
    <div v-if="dataLoaded && !error" class="igv-visualization">
      <!-- 坐标轴标尺 -->
      <div class="igv-ruler">
        <div class="ruler-ticks">
          <div
            v-for="(tick, index) in rulerTicks"
            :key="index"
            class="ruler-tick"
            :style="{ left: tick.position + '%' }"
          >
            <div class="tick-line"></div>
            <div class="tick-label">{{ tick.label }}</div>
          </div>
        </div>
      </div>

      <!-- 基因注释轨道 -->
      <div class="igv-track">
        <div class="track-label">Gene Annotations</div>
        <div class="track-content genes-track">
          <div
            v-for="gene in regionData.genes"
            :key="gene.gene_id"
            class="gene-structure"
            :style="{
              left: calculatePosition(gene.start, regionData.start, regionData.end) + '%',
              width: calculateWidth(gene.start, gene.end, regionData.start, regionData.end) + '%'
            }"
          >
            <!-- 基因主体线（内含子） -->
            <div class="gene-line"></div>
            <!-- 外显子方块（代表整个基因区域） -->
            <div
              class="exon-block"
              :title="getGeneTooltip(gene)"
            ></div>
            <!-- 基因名称标签 -->
            <div class="gene-name">{{ gene.name }}</div>
            <!-- 链方向指示 -->
            <div class="gene-strand" :class="gene.strand === '+' ? 'strand-forward' : 'strand-reverse'">
              {{ gene.strand }}
            </div>
          </div>

          <!-- 当前 SNP 位置标记 -->
          <div
            v-if="regionData.center_snp"
            class="snp-position-marker"
            :style="{
              left: calculatePosition(regionData.center_snp.pos, regionData.start, regionData.end) + '%'
            }"
          >
            <div class="snp-line"></div>
            <div class="snp-arrow">▼</div>
          </div>
        </div>
      </div>

      <!-- SNP 轨道 -->
      <div class="igv-track" v-if="regionData.snps && regionData.snps.length > 0">
        <div class="track-label">SNPs</div>
        <div class="track-content snps-track">
          <div
            v-for="snp in regionData.snps"
            :key="snp.snp_id"
            class="snp-marker"
            :class="{ 'current-snp': snp.pos === regionData.center_snp.pos }"
            :style="{
              left: calculatePosition(snp.pos, regionData.start, regionData.end) + '%'
            }"
            :title="`${snp.name}\n${snp.ref} → ${snp.alt}\nPosition: ${snp.pos.toLocaleString()}`"
          >
            <div class="snp-point"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../services/api'

const props = defineProps({
  snpId: {
    type: Number,
    required: true
  }
})

const loading = ref(false)
const error = ref(null)
const dataLoaded = ref(false)
const regionData = ref({})

// 生成标尺刻度
const rulerTicks = computed(() => {
  if (!regionData.value.start || !regionData.value.end) return []

  const ticks = []
  const start = regionData.value.start
  const end = regionData.value.end
  const range = end - start

  // 生成5个刻度
  const numTicks = 5
  for (let i = 0; i <= numTicks; i++) {
    const pos = start + (range * i / numTicks)
    const position = (i / numTicks) * 100

    // 转换为 kb 单位
    const posKb = (pos / 1000).toFixed(3)
    const label = `${posKb} kb`

    ticks.push({ position, label })
  }

  return ticks
})

// 计算位置（百分比）
function calculatePosition(pos, regionStart, regionEnd) {
  const regionLength = regionEnd - regionStart
  const relativePos = pos - regionStart
  return (relativePos / regionLength) * 100
}

// 计算宽度（百分比）
function calculateWidth(start, end, regionStart, regionEnd) {
  const regionLength = regionEnd - regionStart
  const geneLength = end - start
  return Math.max((geneLength / regionLength) * 100, 1) // 最小1%
}

// 生成基因的工具提示信息
function getGeneTooltip(gene) {
  const strandSymbol = gene.strand === '+' ? '→' : '←'
  const length = ((gene.end - gene.start) / 1000).toFixed(2)

  let tooltip = `Gene: ${gene.name}\n`
  tooltip += `Gene ID: ${gene.gene_id}\n`
  tooltip += `Location: chr${regionData.value.chrom}:${gene.start.toLocaleString()}-${gene.end.toLocaleString()}\n`
  tooltip += `Strand: ${strandSymbol} (${gene.strand})\n`
  tooltip += `Length: ${length} kb\n`
  tooltip += `Biotype: ${gene.gene_biotype || 'protein_coding'}`

  return tooltip
}

// 加载区域数据
async function loadRegion() {
  if (!props.snpId) {
    return
  }

  loading.value = true
  error.value = null

  try {
    console.log('Loading region data for SNP:', props.snpId)
    const data = await api.get(`/snps/${props.snpId}/region`)
    console.log('Region data loaded:', data)

    if (!data) {
      throw new Error('Empty response from server')
    }

    if (data.total_genes === undefined || data.total_snps === undefined) {
      throw new Error('Invalid response structure from server')
    }

    regionData.value = {
      chrom: data.chrom || 'Unknown',
      start: data.start || 0,
      end: data.end || 0,
      total_genes: data.total_genes || 0,
      total_snps: data.total_snps || 0,
      genes: data.genes || [],
      snps: data.snps || [],
      center_snp: data.center_snp || null
    }
    dataLoaded.value = true

    ElMessage.success(`Loaded ${regionData.value.total_genes} genes and ${regionData.value.total_snps} SNPs`)
  } catch (err) {
    console.error('Error loading region data:', err)
    error.value = 'Failed to load genomic region data: ' + (err.response?.data?.detail || err.message)
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRegion()
})
</script>

<style scoped>
.region-viewer {
  margin-top: 20px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 16px;
  background: white;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #409EFF;
  gap: 10px;
}

.loading-container .el-icon {
  font-size: 32px;
}

.error-container {
  margin-top: 20px;
}

/* IGV 可视化容器 */
.igv-visualization {
  width: 100%;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

/* 坐标轴标尺 */
.igv-ruler {
  height: 30px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
  position: relative;
}

.ruler-ticks {
  position: relative;
  width: 100%;
  height: 100%;
}

.ruler-tick {
  position: absolute;
  top: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.tick-line {
  width: 1px;
  height: 8px;
  background: #666;
  margin-top: 2px;
}

.tick-label {
  font-size: 10px;
  color: #333;
  margin-top: 2px;
  font-family: Arial, sans-serif;
}

/* 轨道容器 */
.igv-track {
  display: flex;
  border-bottom: 1px solid #e0e0e0;
  min-height: 60px;
}

.igv-track:last-child {
  border-bottom: none;
}

.track-label {
  width: 120px;
  min-width: 120px;
  padding: 8px 12px;
  font-size: 11px;
  font-weight: 500;
  color: #333;
  background: #fafafa;
  border-right: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  font-family: Arial, sans-serif;
}

.track-content {
  flex: 1;
  position: relative;
  background: white;
  min-height: 60px;
}

/* 基因结构 */
.gene-structure {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  height: 30px;
  display: flex;
  align-items: center;
}

.gene-line {
  position: absolute;
  left: 0;
  right: 0;
  top: 50%;
  height: 2px;
  background: #4a90e2;
}

.exon-block {
  position: absolute;
  top: 50%;
  left: 10%;
  right: 10%;
  height: 20px;
  background: #2c5aa0;
  border: 2px solid #1e3f6f;
  border-radius: 2px;
  transform: translateY(-50%);
  cursor: help;
  transition: all 0.2s;
}

.exon-block:hover {
  background: #3a7bc8;
  border-color: #2c5aa0;
  box-shadow: 0 2px 8px rgba(44, 90, 160, 0.3);
  transform: translateY(-50%) scale(1.05);
  z-index: 5;
}

.gene-name {
  position: absolute;
  bottom: -18px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 10px;
  color: #333;
  white-space: nowrap;
  font-family: Arial, sans-serif;
  font-weight: 500;
}

.gene-strand {
  position: absolute;
  top: -15px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 9px;
  font-weight: bold;
  padding: 1px 4px;
  border-radius: 2px;
}

.strand-forward {
  color: #2c5aa0;
  background: #e8f0fe;
}

.strand-reverse {
  color: #c62828;
  background: #ffebee;
}

/* SNP 位置标记线 */
.snp-position-marker {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1px;
  z-index: 10;
  pointer-events: none;
}

.snp-position-marker .snp-line {
  width: 100%;
  height: 100%;
  background: #ff4444;
  opacity: 0.6;
}

.snp-position-marker .snp-arrow {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  color: #ff4444;
  font-size: 12px;
  margin-top: -2px;
}

/* SNP 轨道 */
.snps-track {
  padding: 10px 0;
}

.snp-marker {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 12px;
  height: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.snp-point {
  width: 100%;
  height: 100%;
  background: #ff6b6b;
  border: 2px solid #e55353;
  border-radius: 50%;
}

.snp-marker:hover .snp-point {
  background: #ff4444;
  transform: scale(1.3);
}

.snp-marker.current-snp .snp-point {
  background: #ffd700;
  border-color: #ffb700;
  box-shadow: 0 0 6px rgba(255, 215, 0, 0.8);
  width: 16px;
  height: 16px;
  margin: -2px;
}
</style>
