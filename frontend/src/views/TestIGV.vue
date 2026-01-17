<template>
  <div class="test-igv">
    <h2>IGV Test Page</h2>
    <el-button @click="testIGV">Test IGV</el-button>
    <el-button @click="testWithData" style="margin-left: 10px;">Test with Sample Data</el-button>
    <div id="igv-test" style="width: 100%; height: 400px; margin-top: 20px; background: #f5f5f5; border-radius: 4px;"></div>
    <div v-if="error" style="color: red; margin-top: 10px;">
      {{ error }}
    </div>
    <div v-if="success" style="color: green; margin-top: 10px;">
      {{ success }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const error = ref(null)
const success = ref(null)

async function testIGV() {
  error.value = null
  success.value = null

  try {
    console.log('Testing IGV...')
    const igv = await import('igv')
    console.log('IGV module loaded:', igv)
    console.log('IGV default:', igv.default)
    console.log('IGV createBrowser:', igv.createBrowser)

    const options = {
      locus: 'chr1:1000000-1100000',
      tracks: []
    }

    console.log('Creating IGV browser with options:', options)
    const container = document.getElementById('igv-test')
    container.innerHTML = ''

    const browser = igv.createBrowser(container, options)
    console.log('IGV browser created:', browser)

    success.value = 'IGV browser created successfully! Check console for details.'
    ElMessage.success('IGV test successful!')
  } catch (err) {
    console.error('IGV test failed:', err)
    error.value = 'IGV test failed: ' + err.message + '\nCheck console for details'
    ElMessage.error('IGV test failed')
  }
}

async function testWithData() {
  error.value = null
  success.value = null

  try {
    console.log('Testing IGV with sample data...')
    const igv = await import('igv')

    const tracks = [
      {
        id: 'test_gene',
        name: 'Test Gene',
        type: 'annotation',
        format: 'bed',
        features: [
          {
            chrom: 'chr1',
            start: 1000500,
            end: 1001000,
            name: 'GENE001',
            strand: '+'
          }
        ],
        color: 'blue',
        height: 120
      },
      {
        id: 'test_snps',
        name: 'Test SNPs',
        type: 'variant',
        format: 'bed',
        features: [
          {
            chrom: 'chr1',
            start: 1000700,
            end: 1000701,
            name: 'rs001',
            ref: 'A',
            alt: 'G'
          },
          {
            chrom: 'chr1',
            start: 1000800,
            end: 1000801,
            name: 'rs002',
            ref: 'C',
            alt: 'T'
          }
        ],
        color: 'red',
        height: 40
      }
    ]

    const options = {
      locus: 'chr1:1000000-1100000',
      tracks: tracks,
      genome: 'custom'
    }

    console.log('Creating IGV with sample data:', options)
    const container = document.getElementById('igv-test')
    container.innerHTML = ''

    const browser = igv.createBrowser(container, options)
    console.log('IGV browser created with data:', browser)

    success.value = 'IGV with sample data created successfully! Check console for details.'
    ElMessage.success('IGV test with data successful!')
  } catch (err) {
    console.error('IGV test with data failed:', err)
    error.value = 'Test failed: ' + err.message + '\nCheck console for details'
    ElMessage.error('Test failed')
  }
}
</script>

<style scoped>
.test-igv {
  padding: 20px;
}
</style>
