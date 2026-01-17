<template>
  <div class="snp-table-view">
    <!-- Header -->
    <div class="page-header">
      <h1>
        <el-icon><Collection /></el-icon>
        SNP Activity Difference (SAD) Database
      </h1>
      <p class="subtitle">Comprehensive database of variant effect evaluations for cattle genomics Genomics</p>
    </div>

    <!-- Stats Cards -->
    <div class="stats-container">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <el-icon class="stat-icon" color="#409EFF"><Document /></el-icon>
              <div class="stat-info">
                <div class="stat-value">{{ stats.total_snps || '-' }}</div>
                <div class="stat-label">Total SNPs</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <el-icon class="stat-icon" color="#67C23A"><Grid /></el-icon>
              <div class="stat-info">
                <div class="stat-value">{{ stats.total_targets || '-' }}</div>
                <div class="stat-label">Total Targets</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <el-icon class="stat-icon" color="#E6A23C"><DataLine /></el-icon>
              <div class="stat-info">
                <div class="stat-value">{{ formatNumber(stats.total_effect_records) || '-' }}</div>
                <div class="stat-label">Effect Records</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Search and Filter -->
    <el-card shadow="never" class="search-card">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="16" :md="18">
          <el-input
            v-model="searchQuery"
            placeholder="Search SNP (chr:position or rsID, e.g., chr1:15449431)"
            clearable
            @clear="handleClearSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
            <template #append>
              <el-button @click="handleSearch" :loading="loading">
                Search
              </el-button>
            </template>
          </el-input>
        </el-col>
        <el-col :xs="24" :sm="8" :md="6">
          <el-select v-model="pageSize" @change="handlePageSizeChange" style="width: 100%">
            <el-option label="10 / page" :value="10" />
            <el-option label="20 / page" :value="20" />
            <el-option label="50 / page" :value="50" />
            <el-option label="100 / page" :value="100" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <!-- Data Table -->
    <el-card shadow="never" class="table-card" v-loading="loading">
      <el-table
        :data="tableData"
        stripe
        border
        style="width: 100%"
        :default-sort="{ prop: 'id', order: 'ascending' }"
        @sort-change="handleSortChange"
        :empty-text="searchMode ? 'No matching SNPs found' : 'No data available'"
      >
        <el-table-column prop="id" label="ID" width="80" sortable="custom" />
        <el-table-column prop="chrom" label="Chromosome" width="100" sortable="custom" />
        <el-table-column prop="pos" label="Position" width="120" sortable="custom">
          <template #default="{ row }">
            <el-tag size="small">{{ formatNumber(row.pos) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="rs_id" label="rsID" width="150">
          <template #default="{ row }">
            <span v-if="row.rs_id" class="rs-id">{{ row.rs_id }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="ref_allele" label="Ref Allele" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.ref_allele }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="alt_allele" label="Alt Allele" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="warning" size="small">{{ row.alt_allele }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="max_abs_sad" label="Max Abs SAD" width="150" sortable="custom">
          <template #default="{ row }">
            <span class="sad-value">{{ row.max_abs_sad.toFixed(6) }}</span>
          </template>
        </el-table-column>

        <!-- Dynamic Target Columns -->
        <el-table-column
          v-for="targetName in topTargetNames"
          :key="targetName"
          :label="targetName"
          :prop="targetName"
          width="110"
          align="center"
        >
          <template #default="{ row }">
            <span :class="getEffectValueClass(getEffectValue(row, targetName))">
              {{ getEffectValue(row, targetName) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="All targets" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              link
              @click="handleViewDetail(row)"
            >
              Details
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handlePageSizeChange"
        />
      </div>
    </el-card>

    <!-- Detail Dialog -->
    <el-dialog
      v-model="detailDialogVisible"
      title="SNP Details"
      width="70%"
      :close-on-click-modal="false"
    >
      <div v-if="currentSnp" class="snp-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ currentSnp.id }}</el-descriptions-item>
          <el-descriptions-item label="rsID">{{ currentSnp.rs_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="Chromosome">{{ currentSnp.chrom }}</el-descriptions-item>
          <el-descriptions-item label="Position">{{ formatNumber(currentSnp.pos) }}</el-descriptions-item>
          <el-descriptions-item label="Reference Allele">
            <el-tag type="info">{{ currentSnp.ref_allele }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Alternate Allele">
            <el-tag type="warning">{{ currentSnp.alt_allele }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Maximum Absolute SAD Value" :span="2">
            <span class="sad-value-large">{{ currentSnp.max_abs_sad.toFixed(8) }}</span>
          </el-descriptions-item>
        </el-descriptions>

        <!-- Nearest Gene Information -->
        <div v-if="currentSnp.nearest_gene" class="gene-info-section">
          <el-divider>Nearest Gene</el-divider>
          <el-alert type="success" :closable="false" class="gene-alert">
            <template #title>
              <div class="gene-info">
                <div class="gene-main">
                  <span class="gene-label">Gene Name:</span>
                  <el-tag size="large" type="success">{{ currentSnp.nearest_gene.gene_name || currentSnp.nearest_gene.gene_id }}</el-tag>
                  <span v-if="currentSnp.nearest_gene.location === 'within'" class="location-badge">
                    <el-tag type="primary" size="small">Within Gene</el-tag>
                  </span>
                  <span v-else class="location-badge">
                    <el-tag type="info" size="small">Nearby ({{ formatNumber(currentSnp.nearest_gene.distance) }} bp)</el-tag>
                  </span>
                </div>
                <div class="gene-details">
                  <span class="gene-detail-item"><strong>Gene ID:</strong> {{ currentSnp.nearest_gene.gene_id }}</span>
                  <span class="gene-detail-item"><strong>Location:</strong> Chr{{ currentSnp.nearest_gene.chrom }}:{{ formatNumber(currentSnp.nearest_gene.start_pos) }}-{{ formatNumber(currentSnp.nearest_gene.end_pos) }} ({{ currentSnp.nearest_gene.strand }} strand)</span>
                  <span class="gene-detail-item"><strong>Biotype:</strong> {{ currentSnp.nearest_gene.gene_biotype || 'N/A' }}</span>
                  <span v-if="currentSnp.nearest_gene.region" class="gene-detail-item">
                    <strong>Region:</strong>
                    <el-tag v-if="currentSnp.nearest_gene.region.startsWith('exon')" type="success" size="small">
                      {{ currentSnp.nearest_gene.region }}
                    </el-tag>
                    <el-tag v-else-if="currentSnp.nearest_gene.region === 'intron'" type="warning" size="small">
                      Intron
                    </el-tag>
                    <el-tag v-else type="info" size="small">
                      {{ currentSnp.nearest_gene.region }}
                    </el-tag>
                  </span>
                </div>
              </div>
            </template>
          </el-alert>
        </div>
        <div v-else class="gene-info-section">
          <el-divider>Nearest Gene</el-divider>
          <el-alert type="info" :closable="false">No gene information available</el-alert>
        </div>

        <el-divider>Effect Values Distribution</el-divider>

        <div v-loading="effectLoading" class="chart-container">
          <div v-if="!effectLoading && currentSnp.effect_values && currentSnp.effect_values.length > 0" ref="boxPlotChart" class="box-plot-chart"></div>
          <el-alert
            v-if="!effectLoading && (!currentSnp.effect_values || currentSnp.effect_values.length === 0)"
            title="No effect values available"
            type="info"
            :closable="false"
          />
        </div>

        <el-divider>Effect Values Histogram</el-divider>

        <div v-loading="effectLoading" class="chart-container">
          <div v-if="!effectLoading && currentSnp.effect_values && currentSnp.effect_values.length > 0" ref="histogramChart" class="histogram-chart"></div>
        </div>

        <el-divider>Effect Values Data</el-divider>

        <div v-loading="effectLoading" class="effects-container">
          <!-- Filter and Export Controls -->
          <el-row :gutter="20" class="controls-row">
            <el-col :span="16">
              <el-input
                v-model="targetFilter"
                placeholder="Filter by target name"
                clearable
                @clear="handleFilterClear"
                @input="handleTargetFilter"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-col>
            <el-col :span="8">
              <el-button
                type="primary"
                @click="handleExportCSV"
                :loading="exporting"
                style="width: 100%"
              >
                <el-icon><Download /></el-icon>
                Export CSV
              </el-button>
            </el-col>
          </el-row>

          <el-table
            v-if="currentSnp.effect_values && currentSnp.effect_values.length > 0"
            :data="filteredEffectValues"
            stripe
            max-height="400"
            :default-sort="{ prop: 'effect_value', order: 'descending' }"
          >
            <el-table-column
              prop="target_name"
              label="Target Name"
              width="300"
            />
            <el-table-column
              prop="effect_value"
              label="Effect Value"
              sortable
            >
              <template #default="{ row }">
                <span :class="getEffectValueClass(row.effect_value)">
                  {{ row.effect_value.toFixed(6) }}
                </span>
              </template>
            </el-table-column>
          </el-table>

          <el-empty
            v-if="!effectLoading && filteredEffectValues.length === 0 && currentSnp.effect_values.length > 0"
            description="No matching targets found"
          />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { snpApi, statsApi } from '../services/api'
import * as echarts from 'echarts'

// Data
const loading = ref(false)
const effectLoading = ref(false)
const searchMode = ref(false)
const tableData = ref([])
const stats = ref({})
const windowWidth = ref(window.innerWidth)

// Pagination
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// Search
const searchQuery = ref('')

// Sort
const sortBy = ref('id')
const sortOrder = ref('asc')

// Detail dialog
const detailDialogVisible = ref(false)
const currentSnp = ref(null)
const boxPlotChart = ref(null)
const histogramChart = ref(null)
const targetFilter = ref('')
const exporting = ref(false)
let chartInstance = null
let histogramInstance = null

// Computed property for filtered effect values
const filteredEffectValues = computed(() => {
  if (!currentSnp.value?.effect_values) return []

  if (!targetFilter.value.trim()) {
    return currentSnp.value.effect_values
  }

  const filter = targetFilter.value.toLowerCase()
  return currentSnp.value.effect_values.filter(e =>
    e.target_name.toLowerCase().includes(filter)
  )
})

// Calculate number of target columns to show based on screen width
const numTargetColumns = computed(() => {
  const width = windowWidth.value
  // Base columns: ID, Chromosome, Position, rsID, Ref Allele, Alt Allele, Max Abs SAD = 7 columns
  // Actions column = 1 column
  // Total fixed columns = 8 columns
  // Each column is approximately 100-120px wide
  const availableWidth = width - 40 // 40px padding
  const baseColumnsWidth = 770 // 7 base columns * 110px average
  const actionsWidth = 100 // Actions column
  const availableForTargets = availableWidth - baseColumnsWidth - actionsWidth
  const targetColumnWidth = 110 // Average width per target column
  const numColumns = Math.floor(availableForTargets / targetColumnWidth)
  return Math.max(1, Math.min(numColumns, 10)) // Show between 1 and 10 target columns
})

// Get top N target names from data
const topTargetNames = computed(() => {
  if (tableData.value.length === 0) return []

  // Collect all unique target names from the first SNP (they should be the same for all SNPs now)
  const firstRow = tableData.value[0]
  if (!firstRow.top_effects || !Array.isArray(firstRow.top_effects)) return []

  // Extract target names and sort them alphabetically for consistent display
  const targetNames = firstRow.top_effects.map(e => e.target_name)
  return targetNames.sort()
})

// Methods
const formatNumber = (num) => {
  return num ? num.toLocaleString() : '-'
}

const getEffectValue = (row, targetName) => {
  if (!row.top_effects || !Array.isArray(row.top_effects)) return '-'
  const effect = row.top_effects.find(e => e.target_name === targetName)
  return effect ? effect.effect_value.toFixed(4) : '-'
}

const getEffectValueClass = (value) => {
  if (value === '-') return ''
  const absValue = Math.abs(value)
  if (absValue > 0.1) return 'effect-high'
  if (absValue > 0.05) return 'effect-medium'
  return 'effect-low'
}

const handleResize = () => {
  windowWidth.value = window.innerWidth
}

const fetchStats = async () => {
  try {
    const data = await statsApi.getStats()
    stats.value = data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

const fetchSNPs = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
      top_n: numTargetColumns.value + 2 // Request a few more than we display
    }

    const response = searchMode.value && searchQuery.value
      ? await snpApi.search(searchQuery.value, params)
      : await snpApi.getList(params)

    tableData.value = response.data
    total.value = response.total
  } catch (error) {
    ElMessage.error(`Failed to load data: ${error.message}`)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('Please enter a search keyword')
    return
  }
  searchMode.value = true
  currentPage.value = 1
  fetchSNPs()
}

const handleClearSearch = () => {
  searchMode.value = false
  searchQuery.value = ''
  currentPage.value = 1
  fetchSNPs()
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchSNPs()
}

const handlePageSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchSNPs()
}

const handleSortChange = ({ prop, order }) => {
  sortBy.value = prop || 'id'
  sortOrder.value = order === 'descending' ? 'desc' : 'asc'
  fetchSNPs()
}

const handleViewDetail = async (row) => {
  currentSnp.value = { ...row, effect_values: [] }
  detailDialogVisible.value = true
  effectLoading.value = true

  try {
    const detail = await snpApi.getDetail(row.id)
    currentSnp.value = detail
  } catch (error) {
    ElMessage.error(`Failed to load details: ${error.message}`)
  } finally {
    effectLoading.value = false

    // Wait for DOM update and loading to finish then render charts
    await nextTick()
    setTimeout(() => {
      renderBoxPlot()
      renderHistogram()
    }, 100)
  }
}

// Calculate box plot statistics
const calculateBoxPlotData = (data) => {
  const sortedData = [...data].sort((a, b) => a - b)
  const n = sortedData.length

  const q1Index = Math.floor(n * 0.25)
  const q2Index = Math.floor(n * 0.5)
  const q3Index = Math.floor(n * 0.75)

  const min = sortedData[0]
  const q1 = sortedData[q1Index]
  const median = sortedData[q2Index]
  const q3 = sortedData[q3Index]
  const max = sortedData[n - 1]

  return [min, q1, median, q3, max]
}

// Render box plot chart
const renderBoxPlot = () => {
  console.log('renderBoxPlot called')
  console.log('boxPlotChart.value:', boxPlotChart.value)
  console.log('currentSnp.value:', currentSnp.value)

  if (!boxPlotChart.value) {
    console.error('boxPlotChart ref is null')
    return
  }

  if (!currentSnp.value?.effect_values || currentSnp.value.effect_values.length === 0) {
    console.error('No effect values available')
    return
  }

  // Dispose existing chart instance
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }

  try {
    // Create new chart instance
    chartInstance = echarts.init(boxPlotChart.value)
    console.log('ECharts instance created')

    // Extract effect values
    const effectValues = currentSnp.value.effect_values.map(e => e.effect_value)
    console.log('Effect values count:', effectValues.length)

    const boxData = calculateBoxPlotData(effectValues)
    console.log('Box data:', boxData)

    // Calculate additional statistics
    const mean = effectValues.reduce((sum, val) => sum + val, 0) / effectValues.length
    const stdDev = Math.sqrt(
      effectValues.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / effectValues.length
    )

    const [min, q1, median, q3, max] = boxData

    // Create custom box plot using lines and areas
    const option = {
      title: {
        text: `Effect Value Distribution (N=${effectValues.length})`,
        left: 'center',
        textStyle: {
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'none'
        },
        formatter: () => {
          return `
            <div style="padding: 5px;">
              <strong>Statistics:</strong><br/>
              Min: ${min.toFixed(6)}<br/>
              Q1: ${q1.toFixed(6)}<br/>
              Median: ${median.toFixed(6)}<br/>
              Q3: ${q3.toFixed(6)}<br/>
              Max: ${max.toFixed(6)}<br/>
              Mean: ${mean.toFixed(6)}<br/>
              Std Dev: ${stdDev.toFixed(6)}
            </div>
          `
        }
      },
      grid: {
        left: '10%',
        right: '10%',
        bottom: '15%',
        top: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: ['All Targets'],
        axisLabel: {
          fontSize: 14,
          fontWeight: 'bold'
        },
        axisLine: {
          lineStyle: {
            color: '#303133'
          }
        }
      },
      yAxis: {
        type: 'value',
        name: 'Effect Value',
        nameTextStyle: {
          fontSize: 14,
          fontWeight: 'bold'
        },
        axisLabel: {
          formatter: (value) => value.toFixed(4)
        },
        splitLine: {
          lineStyle: {
            type: 'dashed'
          }
        }
      },
      series: [
        // Vertical whisker line from min to max
        {
          type: 'line',
          data: [
            [0, min],
            [0, max]
          ],
          lineStyle: {
            color: '#409EFF',
            width: 2
          },
          symbol: 'none',
          z: 1,
          tooltip: { show: false }
        },
        // Box (Q1 to Q3) - horizontal bar centered at median
        {
          type: 'bar',
          data: [
            {
              value: q3 - q1,
              itemStyle: {
                color: 'rgba(64, 158, 255, 0.3)',
                borderColor: '#409EFF',
                borderWidth: 2
              }
            }
          ],
          barWidth: 40,
          label: {
            show: false
          },
          z: 0,
          tooltip: {
            formatter: () => {
              return `Box: Q1=${q1.toFixed(6)}, Q3=${q3.toFixed(6)}`
            }
          }
        },
        // Median line
        {
          type: 'line',
          data: [
            [-0.2, median],
            [0.2, median]
          ],
          lineStyle: {
            color: '#F56C6C',
            width: 3
          },
          symbol: 'none',
          z: 2,
          tooltip: {
            formatter: () => `Median: ${median.toFixed(6)}`
          }
        }
      ]
    }

    console.log('Setting chart option...')
    chartInstance.setOption(option)
    console.log('Chart rendered successfully')

    // Handle window resize
    window.addEventListener('resize', handleChartResize)
  } catch (error) {
    console.error('Error rendering chart:', error)
    ElMessage.error(`Failed to render chart: ${error.message}`)
  }
}

const handleChartResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
  if (histogramInstance) {
    histogramInstance.resize()
  }
}

// Render histogram chart
const renderHistogram = () => {
  if (!histogramChart.value) {
    console.error('histogramChart ref is null')
    return
  }

  if (!currentSnp.value?.effect_values || currentSnp.value.effect_values.length === 0) {
    console.error('No effect values available for histogram')
    return
  }

  // Dispose existing chart instance
  if (histogramInstance) {
    histogramInstance.dispose()
    histogramInstance = null
  }

  try {
    // Create new chart instance
    histogramInstance = echarts.init(histogramChart.value)

    // Extract effect values
    const effectValues = currentSnp.value.effect_values.map(e => e.effect_value)

    // Calculate histogram bins
    const min = Math.min(...effectValues)
    const max = Math.max(...effectValues)
    const binCount = 20 // Number of bins
    const binSize = (max - min) / binCount

    // Initialize bins
    const bins = Array(binCount).fill(0)

    // Count values in each bin
    effectValues.forEach(val => {
      let binIndex = Math.floor((val - min) / binSize)
      if (binIndex >= binCount) binIndex = binCount - 1
      bins[binIndex]++
    })

    // Create bin labels
    const binLabels = bins.map((_, i) => {
      const start = (min + i * binSize).toFixed(4)
      const end = (min + (i + 1) * binSize).toFixed(4)
      return `${start}-${end}`
    })

    const option = {
      title: {
        text: `Effect Value Distribution (N=${effectValues.length}, Bins=${binCount})`,
        left: 'center',
        textStyle: {
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: (params) => {
          const param = params[0]
          const range = param.name
          const count = param.value
          const percentage = ((count / effectValues.length) * 100).toFixed(2)
          return `
            <div style="padding: 5px;">
              <strong>Range:</strong> ${range}<br/>
              <strong>Count:</strong> ${count} targets<br/>
              <strong>Percentage:</strong> ${percentage}%
            </div>
          `
        }
      },
      grid: {
        left: '10%',
        right: '10%',
        bottom: '20%',
        top: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: binLabels,
        name: 'Effect Value Range',
        nameTextStyle: {
          fontSize: 14,
          fontWeight: 'bold'
        },
        axisLabel: {
          fontSize: 10,
          rotate: 45,
          interval: 0
        },
        axisLine: {
          lineStyle: {
            color: '#303133'
          }
        }
      },
      yAxis: {
        type: 'value',
        name: 'Number of Targets',
        nameTextStyle: {
          fontSize: 14,
          fontWeight: 'bold'
        },
        splitLine: {
          lineStyle: {
            type: 'dashed'
          }
        }
      },
      series: [
        {
          type: 'bar',
          data: bins,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.5, color: '#188df0' },
              { offset: 1, color: '#188df0' }
            ]),
            borderRadius: [4, 4, 0, 0]
          },
          emphasis: {
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#2378f7' },
                { offset: 0.7, color: '#2378f7' },
                { offset: 1, color: '#83bff6' }
              ])
            }
          },
          label: {
            show: true,
            position: 'top',
            formatter: (params) => {
              if (params.value > 0) {
                return params.value
              }
              return ''
            },
            fontSize: 10
          }
        }
      ]
    }

    histogramInstance.setOption(option)
    console.log('Histogram rendered successfully')
  } catch (error) {
    console.error('Error rendering histogram:', error)
    ElMessage.error(`Failed to render histogram: ${error.message}`)
  }
}

// Handle target filter
const handleTargetFilter = () => {
  // Filter is handled by the computed property
}

// Clear filter
const handleFilterClear = () => {
  targetFilter.value = ''
}

// Export filtered data to CSV
const handleExportCSV = () => {
  if (!currentSnp.value?.effect_values || currentSnp.value.effect_values.length === 0) {
    ElMessage.warning('No data to export')
    return
  }

  exporting.value = true

  try {
    // Prepare CSV content
    const dataToExport = filteredEffectValues.value
    const headers = ['target', 'effect_value']

    // Build CSV string
    let csvContent = headers.join(',') + '\n'

    dataToExport.forEach(row => {
      // Escape target name if it contains commas
      const targetName = row.target_name.includes(',')
        ? `"${row.target_name}"`
        : row.target_name

      csvContent += `${targetName},${row.effect_value.toFixed(6)}\n`
    })

    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)

    // Generate filename with SNP info
    const snpInfo = currentSnp.value.rs_id
      ? `${currentSnp.value.rs_id}`
      : `${currentSnp.value.chrom}_${currentSnp.value.pos}`
    const filename = `SNP_${snpInfo}_effect_values.csv`

    link.setAttribute('href', url)
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success(`Exported ${dataToExport.length} records to CSV`)
  } catch (error) {
    console.error('Export error:', error)
    ElMessage.error(`Failed to export: ${error.message}`)
  } finally {
    exporting.value = false
  }
}

// Watch for dialog close to clean up chart
watch(detailDialogVisible, (newVal) => {
  if (!newVal) {
    // Clean up box plot chart
    if (chartInstance) {
      chartInstance.dispose()
      chartInstance = null
    }
    // Clean up histogram chart
    if (histogramInstance) {
      histogramInstance.dispose()
      histogramInstance = null
    }
    window.removeEventListener('resize', handleChartResize)
    // Clear filter
    targetFilter.value = ''
  }
})

// Lifecycle
onMounted(() => {
  fetchStats()
  fetchSNPs()
  window.addEventListener('resize', handleResize)
})

// Cleanup
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.snp-table-view {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  color: #303133;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.stats-container {
  margin-bottom: 20px;
}

.stat-card {
  height: 100%;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  font-size: 36px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.rs-id {
  font-family: 'Courier New', monospace;
  color: #409EFF;
  font-weight: 500;
}

.text-muted {
  color: #C0C4CC;
}

.sad-value {
  font-family: 'Courier New', monospace;
  font-weight: 500;
}

.sad-value-large {
  font-family: 'Courier New', monospace;
  font-size: 18px;
  font-weight: 600;
  color: #409EFF;
}

/* Gene Information Styles */
.gene-info-section {
  margin: 20px 0;
}

.gene-alert {
  margin: 10px 0;
}

.gene-info {
  width: 100%;
}

.gene-main {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.gene-label {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.location-badge {
  margin-left: auto;
}

.gene-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-left: 20px;
  border-left: 3px solid #67C23A;
}

.gene-detail-item {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.gene-detail-item strong {
  color: #303133;
  margin-right: 8px;
}

.effects-container {
  margin-top: 20px;
}

.controls-row {
  margin-bottom: 15px;
}

.chart-container {
  margin: 20px 0;
  min-height: 300px;
}

.box-plot-chart {
  width: 100%;
  height: 350px;
}

.histogram-chart {
  width: 100%;
  height: 400px;
}

.effect-high {
  color: #F56C6C;
  font-weight: bold;
}

.effect-medium {
  color: #E6A23C;
  font-weight: 500;
}

.effect-low {
  color: #909399;
}

@media (max-width: 768px) {
  .snp-table-view {
    padding: 10px;
  }

  .page-header h1 {
    font-size: 20px;
  }

  .stat-value {
    font-size: 18px;
  }
}
</style>
