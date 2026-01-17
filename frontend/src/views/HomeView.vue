<template>
  <div class="home-view">
    <!-- Header -->
    <div class="page-header">
      <h1>
        <el-icon><Collection /></el-icon>
        Cattle SNP Effect Database
      </h1>
      <p class="subtitle">Comprehensive SNP Effect Values for Cattle Genomics Research</p>
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

    <!-- Quick Access Cards -->
    <div class="quick-access-container">
      <h2 class="section-title">Quick Access</h2>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover" class="action-card" @click="$router.push('/snps')">
            <div class="action-content">
              <el-icon class="action-icon" color="#409EFF"><Collection /></el-icon>
              <div class="action-info">
                <h3>Browse SNPs</h3>
                <p>Explore the complete SNP dataset with effect values and detailed information</p>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover" class="action-card" @click="$router.push('/download')">
            <div class="action-content">
              <el-icon class="action-icon" color="#67C23A"><Download /></el-icon>
              <div class="action-info">
                <h3>Download Data</h3>
                <p>Access bulk data downloads for offline analysis and research</p>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover" class="action-card" @click="$router.push('/help')">
            <div class="action-content">
              <el-icon class="action-icon" color="#E6A23C"><QuestionFilled /></el-icon>
              <div class="action-info">
                <h3>Get Help</h3>
                <p>Learn how to use the database and understand the data</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- About Section -->
    <el-card shadow="never" class="about-card">
      <template #header>
        <div class="card-header">
          <el-icon><InfoFilled /></el-icon>
          <span>About This Database</span>
        </div>
      </template>
      <div class="about-content">
        <p>
          The Cattle SNP Effect Database provides comprehensive SNP (Single Nucleotide Polymorphism) effect values
          for cattle genomics research. This database contains effect values for multiple target genes and traits,
          enabling researchers to explore the genetic basis of important economic traits in cattle breeding programs.
        </p>
        <el-divider />
        <h3>Key Features</h3>
        <el-row :gutter="20" class="features-row">
          <el-col :xs="24" :sm="12">
            <ul class="feature-list">
              <li>
                <el-icon color="#409EFF"><Check /></el-icon>
                <span>Search SNPs by chromosome:position or rsID</span>
              </li>
              <li>
                <el-icon color="#409EFF"><Check /></el-icon>
                <span>View effect values across multiple targets</span>
              </li>
              <li>
                <el-icon color="#409EFF"><Check /></el-icon>
                <span>Sort and filter data interactively</span>
              </li>
            </ul>
          </el-col>
          <el-col :xs="24" :sm="12">
            <ul class="feature-list">
              <li>
                <el-icon color="#67C23A"><Check /></el-icon>
                <span>Detailed SNP information in dialogs</span>
              </li>
              <li>
                <el-icon color="#67C23A"><Check /></el-icon>
                <span>Color-coded effect values</span>
              </li>
              <li>
                <el-icon color="#67C23A"><Check /></el-icon>
                <span>Responsive design for all devices</span>
              </li>
            </ul>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Collection, Document, Grid, DataLine, Download, QuestionFilled, InfoFilled, Check } from '@element-plus/icons-vue'
import { statsApi } from '../services/api'

// Data
const stats = ref({})

// Methods
const formatNumber = (num) => {
  return num ? num.toLocaleString() : '-'
}

const fetchStats = async () => {
  try {
    const data = await statsApi.getStats()
    stats.value = data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

// Lifecycle
onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.home-view {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 32px;
  color: #303133;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.subtitle {
  font-size: 16px;
  color: #909399;
  margin: 0;
}

.stats-container {
  margin-bottom: 40px;
}

.stat-card {
  height: 100%;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  font-size: 48px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.quick-access-container {
  margin-bottom: 40px;
}

.section-title {
  font-size: 24px;
  color: #303133;
  margin: 0 0 20px 0;
  text-align: center;
}

.action-card {
  cursor: pointer;
  transition: all 0.3s;
  height: 100%;
}

.action-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.action-content {
  display: flex;
  align-items: flex-start;
  gap: 15px;
}

.action-icon {
  font-size: 48px;
  flex-shrink: 0;
}

.action-info h3 {
  font-size: 18px;
  color: #303133;
  margin: 0 0 10px 0;
}

.action-info p {
  font-size: 14px;
  color: #606266;
  margin: 0;
  line-height: 1.6;
}

.about-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.about-content p {
  font-size: 15px;
  color: #606266;
  line-height: 1.8;
  margin-bottom: 15px;
}

.about-content h3 {
  font-size: 18px;
  color: #303133;
  margin: 20px 0 15px 0;
}

.features-row {
  margin-top: 15px;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  color: #606266;
  margin-bottom: 12px;
  line-height: 1.6;
}

.feature-list li span {
  flex: 1;
}

@media (max-width: 768px) {
  .home-view {
    padding: 10px;
  }

  .page-header h1 {
    font-size: 24px;
  }

  .subtitle {
    font-size: 14px;
  }

  .stat-value {
    font-size: 22px;
  }

  .stat-icon,
  .action-icon {
    font-size: 36px;
  }

  .action-content {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .section-title {
    font-size: 20px;
  }
}
</style>
