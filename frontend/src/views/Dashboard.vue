<template>
  <div class="dashboard">
    <h2>仪表盘</h2>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon size="40" color="#409EFF"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalArchives }}</div>
              <div class="stat-label">案卷总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon size="40" color="#67C23A"><FolderOpened /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalCategories }}</div>
              <div class="stat-label">分类总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon size="40" color="#E6A23C"><CircleCheck /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.approvedArchives }}</div>
              <div class="stat-label">已通过</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon size="40" color="#F56C6C"><Clock /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pendingArchives }}</div>
              <div class="stat-label">待审核</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近案卷</span>
          </template>
          <el-table :data="recentArchives" stripe>
            <el-table-column prop="archive_number" label="案卷编号" />
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="status_display" label="状态">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ scope.row.status_display }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>分类统计</span>
          </template>
          <el-table :data="categoryStats" stripe>
            <el-table-column prop="name" label="分类名称" />
            <el-table-column prop="count" label="案卷数量" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { archiveApi, categoryApi } from '@/api'

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
.dashboard h2 {
  margin-bottom: 20px;
  color: #303133;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-info {
  margin-left: 20px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}
</style>
