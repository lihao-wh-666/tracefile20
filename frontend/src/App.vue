<template>
  <el-container class="layout-container">
    <el-header class="header">
      <div class="header-content">
        <el-button 
          class="menu-toggle" 
          :icon="Menu" 
          circle 
          @click="drawerVisible = true"
        />
        <h1 class="header-title">
          <el-icon size="24" class="header-icon"><Document /></el-icon>
          <span>案卷管理系统</span>
        </h1>
      </div>
    </el-header>
    <el-container>
      <el-aside :width="isMobile ? '0px' : '220px'" class="aside">
        <el-menu
          :default-active="activeMenu"
          router
          background-color="#545c64"
          text-color="#fff"
          active-text-color="#ffd04b"
          class="sidebar-menu"
        >
          <el-menu-item index="/dashboard">
            <el-icon><HomeFilled /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/categories">
            <el-icon><Folder /></el-icon>
            <span>分类管理</span>
          </el-menu-item>
          <el-menu-item index="/archives">
            <el-icon><Files /></el-icon>
            <span>案卷管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>

    <el-drawer
      v-model="drawerVisible"
      direction="ltr"
      size="240px"
      class="mobile-drawer"
    >
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#545c64"
        text-color="#fff"
        active-text-color="#ffd04b"
        class="drawer-menu"
        @select="drawerVisible = false"
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <el-icon><Folder /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="/archives">
          <el-icon><Files /></el-icon>
          <span>案卷管理</span>
        </el-menu-item>
      </el-menu>
    </el-drawer>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { Menu } from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = computed(() => route.path)
const drawerVisible = ref(false)
const isMobile = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
}

.layout-container {
  height: 100%;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 60px !important;
}

.header-content {
  display: flex;
  align-items: center;
  width: 100%;
}

.menu-toggle {
  display: none;
  margin-right: 12px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
}

.menu-toggle:hover {
  background: rgba(255, 255, 255, 0.3);
  color: white;
}

.header-title {
  margin: 0;
  font-size: 22px;
  display: flex;
  align-items: center;
  font-weight: 600;
}

.header-icon {
  margin-right: 10px;
}

.aside {
  background-color: #545c64;
  height: calc(100vh - 60px);
  overflow-y: auto;
  transition: width 0.3s ease;
}

.sidebar-menu {
  border-right: none;
}

.main {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-x: hidden;
}

.mobile-drawer :deep(.el-drawer__header) {
  display: none;
}

.mobile-drawer :deep(.el-drawer__body) {
  padding: 0;
  background-color: #545c64;
}

.drawer-menu {
  border-right: none;
  height: 100%;
}

@media (max-width: 768px) {
  .menu-toggle {
    display: inline-flex;
  }

  .header-title span {
    font-size: 18px;
  }

  .main {
    padding: 12px;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .main {
    padding: 16px;
  }

  .aside {
    width: 200px;
  }
}

@media (min-width: 1025px) {
  .aside {
    width: 220px;
  }
}
</style>
