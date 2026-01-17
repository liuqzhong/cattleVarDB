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
      <el-menu-item index="/snps">
        <el-icon><Grid /></el-icon>
        <span>SNP Database</span>
      </el-menu-item>
      <el-menu-item index="/sv">
        <el-icon><Operation /></el-icon>
        <span>SV</span>
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
