<template>
  <div class="igv-container">
    <div class="igv-header">
      <h4>Genomic Region Viewer (50K)</h4>
      <el-button size="small" @click="loadRegion">Refresh</el-button>
    </div>
    <div id="igv-div" class="igv-browser"></div>
    <div v-if="loading" class="loading-overlay">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>Loading genomic data...</span>
    </div>
    <div v-if="error" class="error-message">
      <el-alert type="error" :title="error" :closable="false" />
    </div>
    <div v-if="dataLoaded" class="data-info">
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="Chromosome">{{ regionData.chrom }}</el-descriptions-item>
        <el-descriptions-item label="Region">{{ regionData.start }} - {{ regionData.end }}</el-descriptions-item>
        <el-descriptions-item label="Genes">{{ regionData.total_genes }}</el-descriptions-item>
        <el-descriptions-item label="SNPs">{{ regionData.total_snps }}</el-descriptions-item>
      </el-descriptions>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
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

let igvBrowser = null

// 染色体名称标准化
function formatChrom(chrom) {
  if (!chrom) return 'chr1'
  chrom = chrom.toString().replace(/^chr/i, '').replace(/^CHR/i, '')
  return 'chr' + chrom
}

// 加载区域数据
async function loadRegion() {
  if (!props.snpId) {
    console.error('No SNP ID provided')
    return
  }

  loading.value = true
  error.value = null

  try {
    console.log('Loading region data for SNP:', props.snpId)
    const response = await api.get(`/snps/${props.snpId}/region`)
    const data = response.data
    console.log('Region data loaded:', data)
    regionData.value = data
    dataLoaded.value = true

    // 初始化或更新 IGV 浏览器
    await nextTick()
    if (!igvBrowser) {
      await initializeIGV(data)
    } else {
      await updateIGV(data)
    }

    ElMessage.success(`Loaded ${data.total_genes} genes and ${data.total_snps} SNPs`)
  } catch (err) {
    console.error('Error loading region data:', err)
    error.value = 'Failed to load genomic region data: ' + (err.response?.data?.detail || err.message)
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

// 初始化 IGV 浏览器 (IGV 3.x API)
async function initializeIGV(data) {
  const chrom = formatChrom(data.chrom)
  const locus = `${chrom}:${data.start}-${data.end}`

  console.log('Initializing IGV with locus:', locus)

  // 动态导入 IGV
  const igv = await import('igv')
  console.log('IGV module loaded:', igv)

  // 准备轨道配置
  const tracks = []

  // 基因轨道
  if (data.genes && data.genes.length > 0) {
    const geneFeatures = data.genes.map(gene => {
      const geneChrom = formatChrom(gene.chrom)
      return {
        chrom: geneChrom,
        start: gene.start,
        end: gene.end,
        name: gene.name || gene.gene_id,
        strand: gene.strand || '+',
        gene_id: gene.gene_id,
        gene_biotype: gene.gene_biotype
      }
    })

    tracks.push({
      id: 'genes_track',
      name: 'Genes',
      type: 'annotation',
      format: 'bed',
      features: geneFeatures,
      color: 'rgb(100, 149, 237)',
      height: 120,
      displayMode: 'EXPANDED'
    })
  }

  // SNP 轨道
  if (data.snps && data.snps.length > 0) {
    const snpFeatures = data.snps.map(snp => {
      const snpChrom = formatChrom(snp.chrom)
      return {
        chrom: snpChrom,
        start: snp.start,
        end: snp.end,
        name: snp.name,
        ref: snp.ref,
        alt: snp.alt,
        pos: snp.pos,
        isCurrent: snp.pos === data.center_snp.pos
      }
    })

    // 所有 SNP
    tracks.push({
      id: 'snps_track',
      name: 'All SNPs',
      type: 'variant',
      format: 'bed',
      features: snpFeatures.filter(s => !s.isCurrent),
      color: 'rgb(255, 0, 0)',
      height: 40
    })

    // 当前 SNP (高亮)
    const currentSnp = snpFeatures.find(s => s.isCurrent)
    if (currentSnp) {
      tracks.push({
        id: 'current_snp_track',
        name: 'Current SNP',
        type: 'variant',
        format: 'bed',
        features: [currentSnp],
        color: 'rgb(0, 255, 0)',
        height: 50
      })
    }
  }

  // IGV 配置
  const igvConfig = {
    locus: locus,
    tracks: tracks,
    genome: 'custom'  // 使用自定义基因组
  }

  try {
    console.log('Creating IGV browser with config:', igvConfig)

    // IGV 3.x 使用不同的方式
    const container = document.getElementById('igv-div')
    if (!container) {
      throw new Error('IGV container not found')
    }

    // 清空容器
    container.innerHTML = ''

    // 创建 IGV 浏览器实例
    igvBrowser = igv.createBrowser(container, igvConfig)
    console.log('IGV browser created successfully')

    // 等待 IGV 初始化完成
    await new Promise(resolve => setTimeout(resolve, 1000))
    console.log('IGV initialized')
  } catch (err) {
    console.error('Error creating IGV browser:', err)
    error.value = 'Failed to initialize IGV browser: ' + err.message
    throw err
  }
}

// 更新 IGV 浏览器
async function updateIGV(data) {
  const chrom = formatChrom(data.chrom)
  const locus = `${chrom}:${data.start}-${data.end}`

  console.log('Updating IGV to locus:', locus)

  try {
    // IGV 3.x 中，我们重新创建整个浏览器
    const igv = await import('igv')

    const tracks = []

    // 基因轨道
    if (data.genes && data.genes.length > 0) {
      const geneFeatures = data.genes.map(gene => {
        const geneChrom = formatChrom(gene.chrom)
        return {
          chrom: geneChrom,
          start: gene.start,
          end: gene.end,
          name: gene.name || gene.gene_id,
          strand: gene.strand || '+',
          gene_id: gene.gene_id,
          gene_biotype: gene.gene_biotype
        }
      })

      tracks.push({
        id: 'genes_track',
        name: 'Genes',
        type: 'annotation',
        format: 'bed',
        features: geneFeatures,
        color: 'rgb(100, 149, 237)',
        height: 120,
        displayMode: 'EXPANDED'
      })
    }

    // SNP 轨道
    if (data.snps && data.snps.length > 0) {
      const snpFeatures = data.snps.map(snp => {
        const snpChrom = formatChrom(snp.chrom)
        return {
          chrom: snpChrom,
          start: snp.start,
          end: snp.end,
          name: snp.name,
          ref: snp.ref,
          alt: snp.alt,
          pos: snp.pos,
          isCurrent: snp.pos === data.center_snp.pos
        }
      })

      // 所有 SNP
      tracks.push({
        id: 'snps_track',
        name: 'All SNPs',
        type: 'variant',
        format: 'bed',
        features: snpFeatures.filter(s => !s.isCurrent),
        color: 'rgb(255, 0, 0)',
        height: 40
      })

      // 当前 SNP
      const currentSnp = snpFeatures.find(s => s.isCurrent)
      if (currentSnp) {
        tracks.push({
          id: 'current_snp_track',
          name: 'Current SNP',
          type: 'variant',
          format: 'bed',
          features: [currentSnp],
          color: 'rgb(0, 255, 0)',
          height: 50
        })
      }
    }

    const igvConfig = {
      locus: locus,
      tracks: tracks,
      genome: 'custom'
    }

    // 重新创建浏览器
    const container = document.getElementById('igv-div')
    container.innerHTML = ''
    igvBrowser = igv.createBrowser(container, igvConfig)

    await new Promise(resolve => setTimeout(resolve, 1000))
    console.log('IGV updated successfully')
  } catch (err) {
    console.error('Error updating IGV browser:', err)
    error.value = 'Failed to update IGV browser: ' + err.message
    throw err
  }
}

// 监听 snpId 变化
watch(() => props.snpId, (newId) => {
  console.log('SNP ID changed to:', newId)
  if (newId) {
    loadRegion()
  }
})

onMounted(() => {
  console.log('IGVBrowser component mounted, SNP ID:', props.snpId)
  loadRegion()
})

onBeforeUnmount(() => {
  if (igvBrowser) {
    try {
      // IGV 3.x 可能没有 dispose 方法
      if (typeof igvBrowser.dispose === 'function') {
        igvBrowser.dispose()
      }
    } catch (err) {
      console.warn('Error disposing IGV browser:', err)
    }
    igvBrowser = null
  }
})
</script>

<style scoped>
.igv-container {
  margin-top: 20px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 16px;
  background: white;
  position: relative;
}

.igv-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.igv-header h4 {
  margin: 0;
  color: #303133;
}

.igv-browser {
  width: 100%;
  height: 400px;
  background-color: #f5f5f5;
  border-radius: 4px;
  min-height: 400px;
  position: relative;
}

.loading-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  color: #409EFF;
  font-size: 14px;
  z-index: 10;
}

.loading-overlay .el-icon {
  font-size: 32px;
}

.error-message {
  margin-top: 20px;
}

.data-info {
  margin-top: 16px;
}
</style>
