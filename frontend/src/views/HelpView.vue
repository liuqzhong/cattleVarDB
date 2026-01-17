<template>
  <div class="help-view">
    <div class="page-header">
      <h1>
        <el-icon><QuestionFilled /></el-icon>
        Help & Documentation
      </h1>
      <p class="subtitle">User Guide and Documentation for Cattle SNP Effect Database</p>
    </div>

    <el-card shadow="never" class="content-card">
      <h2>Database Overview</h2>
      <p>
        The Cattle SNP Effect Database provides comprehensive SNP (Single Nucleotide Polymorphism) effect values
        for cattle genomics research. This database contains effect values for multiple target genes/traits,
        enabling researchers to explore the genetic basis of important economic traits in cattle.
      </p>

      <el-divider />

      <h2>How to Use</h2>

      <el-collapse>
        <el-collapse-item title="Searching for SNPs" name="1">
          <p>You can search for SNPs using two formats:</p>
          <ul>
            <li><strong>Chromosome:Position format:</strong> Enter coordinates like <code>chr1:15449431</code> or <code>1:15449431</code></li>
            <li><strong>rsID format:</strong> Enter the dbSNP reference ID like <code>rs110821456</code></li>
          </ul>
          <p>Click the Search button or press Enter to execute your search.</p>
        </el-collapse-item>

        <el-collapse-item title="Understanding the Data Table" name="2">
          <p>The main table displays:</p>
          <ul>
            <li><strong>ID:</strong> Unique identifier for each SNP</li>
            <li><strong>Chromosome & Position:</strong> Genomic coordinates</li>
            <li><strong>rsID:</strong> dbSNP reference identifier (if available)</li>
            <li><strong>Ref/Alt Allele:</strong> Reference and alternate alleles</li>
            <li><strong>Max Abs SAD:</strong> Maximum absolute SAD (selection signature deviation) value across all targets</li>
            <li><strong>Target Columns:</strong> Effect values for common targets (number varies by screen size)</li>
          </ul>
        </el-collapse-item>

        <el-collapse-item title="Viewing Detailed Information" name="3">
          <p>Click the "Details" button in the Actions column to view:</p>
          <ul>
            <li>Complete SNP information</li>
            <li>All target effect values (sorted by effect magnitude)</li>
            <li>Full effect value dataset for the selected SNP</li>
          </ul>
        </el-collapse-item>

        <el-collapse-item title="Sorting and Pagination" name="4">
          <p>
            Click any column header to sort the data. Use the pagination controls at the bottom to navigate
            through large datasets. You can also change the number of items displayed per page.
          </p>
        </el-collapse-item>
      </el-collapse>

      <el-divider />

      <h2>Understanding Effect Values</h2>
      <p>
        Effect values represent the estimated impact of each SNP on various target genes or traits.
        Higher absolute values indicate stronger effects. The color-coded display helps identify:
      </p>
      <ul>
        <li><span class="effect-high">Red (bold):</span> Strong effects (>0.1)</li>
        <li><span class="effect-medium">Orange (medium):</span> Moderate effects (0.05-0.1)</li>
        <li><span class="effect-low">Gray (light):</span> Weak effects (<0.05)</li>
      </ul>

      <el-divider />

      <h2>Contact & Support</h2>
      <p>
        For questions, bug reports, or feature requests, please contact the database administrators.
        This database is continuously updated with new data and features.
      </p>
    </el-card>
  </div>
</template>

<script setup>
import { QuestionFilled } from '@element-plus/icons-vue'
</script>

<style scoped>
.help-view {
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

.content-card {
  margin-bottom: 20px;
}

.content-card h2 {
  font-size: 22px;
  color: #303133;
  margin-bottom: 15px;
  border-left: 4px solid #409EFF;
  padding-left: 12px;
}

.content-card p {
  font-size: 15px;
  color: #606266;
  line-height: 1.8;
  margin-bottom: 15px;
}

.content-card ul {
  margin: 10px 0;
  padding-left: 20px;
}

.content-card li {
  font-size: 15px;
  color: #606266;
  line-height: 1.8;
  margin-bottom: 8px;
}

.content-card code {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  color: #409EFF;
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
  .help-view {
    padding: 10px;
  }

  .page-header h1 {
    font-size: 20px;
  }
}
</style>
