<template>
  <el-config-provider :locale="epLocale">
    <div v-if="isLoginPage" class="login-wrapper">
      <router-view />
    </div>
    <el-container v-else class="layout-container">
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
          <span>{{ t('header.title') }}</span>
        </h1>
        <div class="header-right">
          <el-button 
            class="theme-toggle-btn" 
            :icon="isDark ? Sunny : Moon" 
            circle 
            @click="toggleTheme"
            :title="isDark ? t('header.lightMode') : t('header.darkMode')"
          />
          <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="notification-badge">
            <el-button 
              class="notification-btn" 
              :icon="Bell" 
              circle 
              @click="notificationVisible = true"
            />
          </el-badge>
          <el-dropdown @command="handleUserCommand" class="user-dropdown">
            <span class="user-info">
              <el-icon class="user-icon"><UserFilled /></el-icon>
              <span class="username">{{ userInfo?.username || t('common.unknown') }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  <span>{{ t('profile.username') }}：{{ userInfo?.username }}</span>
                </el-dropdown-item>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  {{ t('header.profile') }}
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  {{ t('header.logout') }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
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
            <span>{{ t('sidebar.dashboard') }}</span>
          </el-menu-item>
          <el-menu-item index="/categories">
            <el-icon><Folder /></el-icon>
            <span>{{ t('sidebar.categories') }}</span>
          </el-menu-item>
          <el-menu-item index="/archives">
            <el-icon><Files /></el-icon>
            <span>{{ t('sidebar.archives') }}</span>
          </el-menu-item>
          <el-menu-item index="/logs">
            <el-icon><Tickets /></el-icon>
            <span>{{ t('sidebar.logs') }}</span>
          </el-menu-item>
          <el-menu-item index="/todos">
            <el-icon><List /></el-icon>
            <span>{{ t('sidebar.todos') }}</span>
          </el-menu-item>
          <el-menu-item index="/profile">
            <el-icon><User /></el-icon>
            <span>{{ t('sidebar.profile') }}</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>

    <el-drawer
      v-model="notificationVisible"
      :title="t('header.notifications')"
      direction="rtl"
      size="400px"
      class="notification-drawer"
    >
      <div class="notification-header">
        <span>{{ t('header.totalTodos') }} {{ notificationList.length }} {{ t('header.totalTodosSuffix') }}</span>
        <el-button 
          type="primary" 
          link 
          size="small" 
          @click="handleMarkAllRead"
          :disabled="unreadCount === 0"
        >
          {{ t('header.markAllRead') }}
        </el-button>
      </div>
      <div class="notification-list">
        <div 
          v-for="item in notificationList" 
          :key="item.id" 
          class="notification-item"
          :class="{ 'is-read': item.is_read, 'is-completed': item.status === 'completed' }"
        >
          <div class="item-header">
            <el-tag 
              :type="getPriorityType(item.priority)" 
              size="small"
              class="priority-tag"
            >
              {{ item.priority_display }}
            </el-tag>
            <span class="item-time">{{ formatDate(item.created_at) }}</span>
          </div>
          <div class="item-title" @click="handleViewTodo(item)">{{ item.title }}</div>
          <div v-if="item.description" class="item-desc">{{ item.description }}</div>
          <div class="item-actions">
            <el-checkbox 
              :model-value="item.status === 'completed'" 
              @change="handleToggleStatus(item)"
            >
              {{ t('header.completed') }}
            </el-checkbox>
            <el-button type="primary" link size="small" @click="handleMarkRead(item)" v-if="!item.is_read">
              {{ t('header.markRead') }}
            </el-button>
          </div>
        </div>
        <el-empty v-if="notificationList.length === 0" :description="t('header.noNotifications')" />
      </div>
      <div class="notification-footer">
        <el-button type="primary" @click="goToTodoList" style="width: 100%">
          {{ t('header.viewAll') }}
        </el-button>
      </div>
    </el-drawer>

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
          <span>{{ t('sidebar.dashboard') }}</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <el-icon><Folder /></el-icon>
          <span>{{ t('sidebar.categories') }}</span>
        </el-menu-item>
        <el-menu-item index="/archives">
          <el-icon><Files /></el-icon>
          <span>{{ t('sidebar.archives') }}</span>
        </el-menu-item>
        <el-menu-item index="/logs">
          <el-icon><Tickets /></el-icon>
          <span>{{ t('sidebar.logs') }}</span>
        </el-menu-item>
        <el-menu-item index="/todos">
          <el-icon><List /></el-icon>
          <span>{{ t('sidebar.todos') }}</span>
        </el-menu-item>
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <span>{{ t('sidebar.profile') }}</span>
        </el-menu-item>
      </el-menu>
    </el-drawer>
  </el-container>
  </el-config-provider>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Menu, Bell, List, UserFilled, SwitchButton, User, Sunny, Moon, Tickets } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import en from 'element-plus/dist/locale/en.mjs'
import ja from 'element-plus/dist/locale/ja.mjs'
import { todoApi, authApi } from '@/api'
import { useTheme } from '@/composables/useTheme'
import { useLocale } from '@/composables/useLocale'

const { isDark, toggleTheme } = useTheme()
const { t, locale } = useLocale()

const elementPlusLocales = {
  'zh-CN': zhCn,
  'en': en,
  'ja': ja
}

const epLocale = computed(() => {
  return elementPlusLocales[locale.value] || zhCn
})

const route = useRoute()
const router = useRouter()
const activeMenu = computed(() => route.path)
const isLoginPage = computed(() => route.path === '/login')
const drawerVisible = ref(false)
const notificationVisible = ref(false)
const isMobile = ref(false)
const unreadCount = ref(0)
const notificationList = ref([])
const userInfo = ref(null)
let refreshInterval = null

const loadUserInfo = async () => {
  try {
    const res = await authApi.getUserInfo()
    userInfo.value = res.data
    localStorage.setItem('user', JSON.stringify(res.data))
  } catch (error) {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        userInfo.value = JSON.parse(userStr)
      } catch (e) {
        userInfo.value = null
      }
    }
  }
}

const handleUserCommand = async (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    try {
      await ElMessageBox.confirm(t('header.logoutConfirm'), t('common.warning'), {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      })
      try {
        await authApi.logout()
      } catch (e) {
      }
      localStorage.removeItem('user')
      userInfo.value = null
      ElMessage.success(t('header.loggedOut'))
      router.push('/login')
    } catch (e) {
    }
  }
}

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

const getPriorityType = (priority) => {
  const map = { high: 'danger', medium: 'warning', low: 'info' }
  return map[priority] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return t('header.justNow')
  if (diff < 3600000) return `${Math.floor(diff / 60000)}${t('header.minutesAgo')}`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}${t('header.hoursAgo')}`
  return date.toLocaleDateString(locale.value)
}

const loadUnreadCount = async () => {
  try {
    const res = await todoApi.getUnreadCount()
    unreadCount.value = res.data.count
  } catch (error) {
    console.error('加载未读数量失败:', error)
  }
}

const loadNotificationList = async () => {
  try {
    const res = await todoApi.getAll({ page_size: 10, ordering: '-created_at' })
    notificationList.value = res.data.results || res.data
  } catch (error) {
    console.error('加载待办列表失败:', error)
  }
}

const handleMarkAllRead = async () => {
  try {
    await todoApi.markAllRead()
    notificationList.value.forEach(item => item.is_read = true)
    unreadCount.value = 0
    ElMessage.success(t('header.allMarkedRead'))
  } catch (error) {
    console.error('标记全部已读失败:', error)
  }
}

const handleMarkRead = async (item) => {
  try {
    await todoApi.update(item.id, { ...item, is_read: true })
    item.is_read = true
    if (unreadCount.value > 0) unreadCount.value--
  } catch (error) {
    console.error('标记已读失败:', error)
  }
}

const handleToggleStatus = async (item) => {
  try {
    const res = await todoApi.toggleStatus(item.id)
    Object.assign(item, res.data)
    ElMessage.success(item.status === 'completed' ? t('header.statusCompleted') : t('header.statusPending'))
  } catch (error) {
    console.error('切换状态失败:', error)
  }
}

const handleViewTodo = (item) => {
  if (!item.is_read) handleMarkRead(item)
}

const goToTodoList = () => {
  notificationVisible.value = false
  router.push('/todos')
}

onMounted(() => {
  loadUserInfo()
  checkMobile()
  window.addEventListener('resize', checkMobile)
  loadUnreadCount()
  loadNotificationList()
  refreshInterval = setInterval(loadUnreadCount, 60000)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
  if (refreshInterval) clearInterval(refreshInterval)
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

body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  transition: background-color 0.3s ease, color 0.3s ease;
}

.login-wrapper {
  height: 100%;
}

.layout-container {
  height: 100%;
}

.header {
  background: var(--gradient-primary);
  color: var(--header-text);
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 60px !important;
  transition: background 0.3s ease;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.header-right {
  display: flex;
  align-items: center;
}

.theme-toggle-btn,
.notification-btn,
.menu-toggle {
  background: var(--header-btn-bg);
  border: none;
  color: var(--header-text);
  transition: background-color 0.3s ease, color 0.3s ease;
}

.theme-toggle-btn:hover,
.notification-btn:hover,
.menu-toggle:hover {
  background: var(--header-btn-hover-bg);
  color: var(--header-text);
}

.theme-toggle-btn {
  margin-right: 8px;
}

.notification-badge :deep(.el-badge__content) {
  background-color: var(--danger-color);
}

.user-dropdown {
  margin-left: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  color: var(--header-text);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.3s;
}

.user-info:hover {
  background: var(--header-btn-bg);
}

.user-icon {
  margin-right: 6px;
  font-size: 18px;
}

.username {
  font-size: 14px;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-tertiary);
  margin-bottom: 12px;
}

.notification-list {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.notification-item {
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  background-color: var(--bg-tertiary);
  cursor: pointer;
  transition: all 0.3s;
}

.notification-item:hover {
  background-color: var(--bg-hover);
}

.notification-item.is-read {
  opacity: 0.7;
}

.notification-item.is-completed {
  opacity: 0.5;
}

.notification-item.is-completed .item-title {
  text-decoration: line-through;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.priority-tag {
  margin-right: 8px;
}

.item-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.item-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 6px;
  line-height: 1.4;
}

.item-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notification-footer {
  padding-top: 16px;
  border-top: 1px solid var(--border-tertiary);
  margin-top: 16px;
}

.menu-toggle {
  display: none;
  margin-right: 12px;
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
  background-color: var(--sidebar-bg);
  height: calc(100vh - 60px);
  overflow-y: auto;
  transition: width 0.3s ease, background-color 0.3s ease;
}

.sidebar-menu {
  border-right: none;
  --el-menu-bg-color: var(--sidebar-bg);
  --el-menu-text-color: var(--sidebar-text);
  --el-menu-active-color: var(--sidebar-active-text);
  --el-menu-hover-bg-color: var(--sidebar-hover-bg);
}

.sidebar-menu .el-menu-item,
.drawer-menu .el-menu-item {
  transition: background-color 0.3s ease, color 0.3s ease;
}

.main {
  background-color: var(--bg-primary);
  padding: 20px;
  overflow-x: hidden;
  transition: background-color 0.3s ease;
}

.mobile-drawer :deep(.el-drawer__header) {
  display: none;
}

.mobile-drawer :deep(.el-drawer__body) {
  padding: 0;
  background-color: var(--sidebar-bg);
}

.drawer-menu {
  border-right: none;
  height: 100%;
  --el-menu-bg-color: var(--sidebar-bg);
  --el-menu-text-color: var(--sidebar-text);
  --el-menu-active-color: var(--sidebar-active-text);
  --el-menu-hover-bg-color: var(--sidebar-hover-bg);
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
