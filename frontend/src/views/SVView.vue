<template>
  <div class="sv-view">
    <div class="page-header">
      <h1>
        <el-icon><Grid /></el-icon>
        Structural Variants Database
      </h1>
      <p class="subtitle">Comprehensive Structural Variant Data for Cattle Genomics</p>
    </div>

    <el-result
      icon="info"
      title="Coming Soon"
      sub-title="Structural Variant (SV) data will be available in future releases."
    >
      <template #extra>
        <el-button type="primary" @click="$router.push('/')">
          Back to Home
        </el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup>
import { Grid } from '@element-plus/icons-vue'
</script>

<style scoped>
.sv-view {
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
</style>
