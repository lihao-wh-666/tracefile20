<template>
  <div class="dashboard">
    <h2 class="page-title">{{ t('dashboard.title') }}</h2>
    
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon size="36" color="#409EFF" class="stat-icon"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalArchives }}</div>
              <div class="stat-label">{{ t('profile.totalArchives') }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon size="36" color="#67C23A" class="stat-icon"><FolderOpened /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalCategories }}</div>
              <div class="stat-label">{{ t('categories.title') }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon size="36" color="#E6A23C" class="stat-icon"><CircleCheck /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.approvedArchives }}</div>
              <div class="stat-label">{{ t('archives.approved') }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon size="36" color="#F56C6C" class="stat-icon"><Clock /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pendingArchives }}</div>
              <div class="stat-label">{{ t('archives.pending') }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="tables-row">
      <el-col :xs="24" :sm="24" :md="24" :lg="12">
        <el-card class="table-card">
          <template #header>
            <span class="card-title">{{ t('dashboard.recentActivity') }}</span>
          </template>
          <div class="table-container">
            <el-table :data="recentArchives" stripe class="responsive-table">
              <el-table-column prop="archive_number" :label="t('archives.archiveNumber')" min-width="100" />
              <el-table-column prop="title" :label="t('archives.archiveTitle')" min-width="120" show-overflow-tooltip />
              <el-table-column prop="status_display" :label="t('archives.status')" width="90">
                <template #default="scope">
                  <el-tag :type="getStatusType(scope.row.status)" size="small">
                    {{ scope.row.status_display }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="24" :lg="12">
        <el-card class="table-card">
          <template #header>
            <span class="card-title">{{ t('categories.title') }}</span>
          </template>
          <div class="table-container">
            <el-table :data="categoryStats" stripe class="responsive-table">
              <el-table-column prop="name" :label="t('categories.categoryName')" min-width="120" show-overflow-tooltip />
              <el-table-column prop="count" :label="t('dashboard.totalArchives', '案卷数量')" width="100" />
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { archiveApi, categoryApi } from '@/api'
import { useLocale } from '@/composables/useLocale'

const { t } = useLocale()

const stats = ref({
  totalArchives: 0,
  totalCategories: 0,
  approvedArchives: 0,
  pendingArchives: 0
})

const recentArchives = ref([])
const categoryStats = ref([])

const getStatusType = (status) => {
  const statusMap = {
    draft: 'info',
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return statusMap[status] || 'info'
}

const loadData = async () => {
  try {
    const [archivesRes, categoriesRes] = await Promise.all([
      archiveApi.getAll({ page_size: 100 }),
      categoryApi.getAll()
    ])

    const archives = archivesRes.data.results || archivesRes.data
    const categories = categoriesRes.data.results || categoriesRes.data

    stats.value.totalArchives = archives.length
    stats.value.totalCategories = categories.length
    stats.value.approvedArchives = archives.filter(a => a.status === 'approved').length
    stats.value.pendingArchives = archives.filter(a => a.status === 'pending').length

    recentArchives.value = archives.slice(0, 5)

    const categoryCount = {}
    archives.forEach(a => {
      const catName = a.category_name || '未分类'
      categoryCount[catName] = (categoryCount[catName] || 0) + 1
    })
    
    categoryStats.value = Object.entries(categoryCount).map(([name, count]) => ({
      name,
      count
    }))
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.page-title {
  margin-bottom: 20px;
  color: #303133;
  font-size: 22px;
  font-weight: 600;
}

.stats-row {
  margin-bottom: 16px;
}

.stat-card {
  height: 110px;
  margin-bottom: 16px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  flex-shrink: 0;
}

.stat-info {
  margin-left: 16px;
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 26px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 6px;
}

.tables-row {
  margin-top: 0;
}

.table-card {
  margin-bottom: 16px;
}

.card-title {
  font-weight: 600;
  color: #303133;
}

.table-container {
  overflow-x: auto;
}

.responsive-table {
  min-width: 100%;
}

@media (max-width: 768px) {
  .page-title {
    font-size: 18px;
    margin-bottom: 16px;
  }

  .stat-card {
    height: 95px;
  }

  .stat-icon {
    font-size: 32px !important;
  }

  .stat-info {
    margin-left: 12px;
  }

  .stat-value {
    font-size: 22px;
  }

  .stat-label {
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .stat-icon {
    font-size: 28px !important;
  }

  .stat-info {
    margin-left: 10px;
  }

  .stat-value {
    font-size: 20px;
  }

  .stat-label {
    font-size: 12px;
  }
}
</style>
