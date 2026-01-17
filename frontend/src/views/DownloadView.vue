<template>
  <div class="download-view">
    <div class="page-header">
      <h1>
        <el-icon><Download /></el-icon>
        Download Center
      </h1>
      <p class="subtitle">Download SNP Effect Data and Resources</p>
    </div>

    <el-result
      icon="info"
      title="Coming Soon"
      sub-title="Bulk data download functionality will be available in future releases."
    >
      <template #extra>
        <el-button type="primary" @click="$router.push('/')">
          Back to Home
        </el-button>
      </template>
    </el-result>

    <el-divider>Planned Features</el-divider>

    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" class="feature-card">
          <el-icon class="feature-icon" color="#409EFF"><Document /></el-icon>
          <h3>Complete SNP Dataset</h3>
          <p>Download all SNP effect values in standard formats (TSV, CSV, JSON)</p>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" class="feature-card">
          <el-icon class="feature-icon" color="#67C23A"><Grid /></el-icon>
          <h3>Target-Specific Data</h3>
          <p>Filter and download data for specific target genes or traits</p>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" class="feature-card">
          <el-icon class="feature-icon" color="#E6A23C"><Files /></el-icon>
          <h3>Batch Export</h3>
          <p>Export filtered query results for offline analysis</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { Download, Document, Grid, Files } from '@element-plus/icons-vue'
</script>

<style scoped>
.download-view {
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

.feature-card {
  text-align: center;
  padding: 10px;
  margin-bottom: 20px;
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.feature-card h3 {
  font-size: 18px;
  color: #303133;
  margin: 10px 0;
}

.feature-card p {
  font-size: 14px;
  color: #606266;
  margin: 0;
}
</style>
