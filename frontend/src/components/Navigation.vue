<template>
  <el-menu
    :default-active="activeMenu"
    mode="horizontal"
    :ellipsis="false"
    class="navigation-menu"
    router
  >
    <div class="logo">
      <el-icon><Collection /></el-icon>
      <span>CattleVarDB</span>
    </div>
    <div class="menu-items">
      <el-menu-item index="/">
        <el-icon><HomeFilled /></el-icon>
        <span>Home</span>
      </el-menu-item>
      <el-sub-menu index="activity-diff">
        <template #title>
          <el-icon><Grid /></el-icon>
          <span>Search Activity Difference</span>
        </template>
        <el-menu-item index="/snps">SNPs</el-menu-item>
        <el-menu-item index="/indels">Indels</el-menu-item>
        <el-menu-item index="/svs">SVs</el-menu-item>
      </el-sub-menu>
      <el-sub-menu index="expression-diff">
        <template #title>
          <el-icon><Operation /></el-icon>
          <span>Search Expression Difference</span>
        </template>
        <el-menu-item index="/exp-snps">SNPs</el-menu-item>
        <el-menu-item index="/exp-indels">Indels</el-menu-item>
        <el-menu-item index="/exp-svs">SVs</el-menu-item>
      </el-sub-menu>
      <el-menu-item index="/prediction">
        <el-icon><TrendCharts /></el-icon>
        <span>Prediction</span>
      </el-menu-item>
      <el-menu-item index="/download">
        <el-icon><Download /></el-icon>
        <span>Download</span>
      </el-menu-item>
      <el-menu-item index="/help">
        <el-icon><QuestionFilled /></el-icon>
        <span>Help</span>
      </el-menu-item>
    </div>
  </el-menu>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const activeMenu = computed(() => route.path)
</script>

<style scoped>
.navigation-menu {
  border-bottom: 2px solid #409EFF;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
  margin-right: 40px;
  padding: 0 10px;
}

.logo .el-icon {
  font-size: 24px;
}

.menu-items {
  flex: 1;
  display: flex;
}

.navigation-menu .el-menu-item {
  font-size: 16px;
  font-weight: 500;
  padding: 0 20px;
}

.navigation-menu .el-icon {
  margin-right: 5px;
}

/* 加粗子菜单标题 */
.navigation-menu .el-sub-menu__title span {
  font-weight: bold;
}

@media (max-width: 768px) {
  .logo {
    margin-right: 20px;
  }

  .logo span {
    display: none;
  }

  .navigation-menu .el-menu-item {
    padding: 0 10px;
  }

  .navigation-menu .el-menu-item span {
    font-size: 14px;
  }
}
</style>
