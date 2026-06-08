<template>
  <div class="logs">
    <div class="page-header">
      <h2 class="page-title">{{ t('logs.title') }}</h2>
    </div>

    <el-card class="main-card">
      <el-form :model="searchForm" class="search-form">
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item :label="t('common.search')" class="form-item">
              <el-input v-model="searchForm.search" :placeholder="searchPlaceholder" clearable class="full-width" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item :label="t('logs.actionType')" class="form-item">
              <el-select v-model="searchForm.action_type" :placeholder="t('common.select')" clearable class="full-width">
                <el-option :label="t('logs.create')" value="create" />
                <el-option :label="t('logs.update')" value="update" />
                <el-option :label="t('logs.delete')" value="delete" />
                <el-option :label="t('logs.view')" value="view" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item :label="t('logs.operator')" class="form-item">
              <el-input v-model="searchForm.operator" :placeholder="t('logs.operator')" clearable class="full-width" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="24" :lg="6">
            <el-form-item class="form-item action-btns">
              <el-button type="primary" @click="handleSearch" class="search-btn">{{ t('common.search') }}</el-button>
              <el-button @click="handleReset" class="reset-btn">{{ t('common.reset') }}</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <div class="table-container">
        <el-table :data="logs" stripe border class="responsive-table">
          <el-table-column prop="id" :label="t('logs.id')" width="80" />
          <el-table-column prop="action_type_display" :label="t('logs.actionType')" width="90">
            <template #default="scope">
              <el-tag :type="getActionType(scope.row.action_type)" size="small">
                {{ scope.row.action_type_display }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="archive_number" :label="t('logs.archiveNumber')" min-width="120" />
          <el-table-column prop="archive_title" :label="t('logs.archiveTitle')" min-width="150" show-overflow-tooltip />
          <el-table-column prop="operator" :label="t('logs.operator')" width="100" />
          <el-table-column prop="ip_address" :label="t('logs.ipAddress')" width="130" />
          <el-table-column prop="created_at" :label="t('logs.operationTime')" min-width="160">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column :label="t('common.view')" fixed="right" width="100">
            <template #default="scope">
              <el-button type="primary" link size="small" @click="handleView(scope.row)">{{ t('common.view') }}</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="detailVisible" :title="t('logs.logDetail')" :width="dialogWidth" class="detail-dialog">
      <el-descriptions :column="1" border v-if="currentLog">
        <el-descriptions-item :label="t('logs.id')">{{ currentLog.id }}</el-descriptions-item>
        <el-descriptions-item :label="t('logs.actionType')">
          <el-tag :type="getActionType(currentLog.action_type)" size="small">
            {{ currentLog.action_type_display }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item :label="t('logs.archiveNumber')">{{ currentLog.archive_number || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="t('logs.archiveTitle')">{{ currentLog.archive_title || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="t('logs.operator')">{{ currentLog.operator }}</el-descriptions-item>
        <el-descriptions-item :label="t('logs.ipAddress')">{{ currentLog.ip_address }}</el-descriptions-item>
        <el-descriptions-item :label="t('logs.operationTime')">{{ formatDate(currentLog.created_at) }}</el-descriptions-item>
        <el-descriptions-item :label="t('logs.changeContent')" v-if="currentLog.change_content">
          <div class="change-content">
            <div class="change-section" v-if="currentLog.change_content.old">
              <div class="change-label">{{ t('logs.beforeChange') }}:</div>
              <pre class="change-json old">{{ formatJson(currentLog.change_content.old) }}</pre>
            </div>
            <div class="change-section" v-if="currentLog.change_content.new">
              <div class="change-label">{{ t('logs.afterChange') }}:</div>
              <pre class="change-json new">{{ formatJson(currentLog.change_content.new) }}</pre>
            </div>
          </div>
        </el-descriptions-item>
        <el-descriptions-item :label="t('logs.changeContent')" v-else>
          {{ t('logs.noChangeContent') }}
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailVisible = false">{{ t('common.close') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { archiveLogApi } from '@/api'
import { useLocale } from '@/composables/useLocale'

const { t, locale } = useLocale()

const logs = ref([])
const detailVisible = ref(false)
const currentLog = ref(null)
const isMobile = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

const dialogWidth = computed(() => {
  if (isMobile.value) return '95%'
  return '700px'
})

const searchForm = reactive({
  search: '',
  action_type: '',
  operator: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const searchPlaceholder = computed(() => `${t('common.search')}...`)

const getActionType = (type) => {
  const typeMap = {
    create: 'success',
    update: 'warning',
    delete: 'danger',
    view: 'info'
  }
  return typeMap[type] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString(locale.value)
}

const formatJson = (obj) => {
  if (!obj) return ''
  return JSON.stringify(obj, null, 2)
}

const loadLogs = async () => {
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm
    }
    if (!params.search) delete params.search
    if (!params.action_type) delete params.action_type
    if (!params.operator) delete params.operator

    const res = await archiveLogApi.getAll(params)
    logs.value = res.data.results || res.data
    pagination.total = res.data.count || logs.value.length
  } catch (error) {
    ElMessage.error(t('errors.loadFailed'))
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadLogs()
}

const handleReset = () => {
  searchForm.search = ''
  searchForm.action_type = ''
  searchForm.operator = ''
  pagination.page = 1
  loadLogs()
}

const handlePageChange = () => loadLogs()
const handleSizeChange = () => {
  pagination.page = 1
  loadLogs()
}

const handleView = (row) => {
  currentLog.value = row
  detailVisible.value = true
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  loadLogs()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.page-title {
  margin: 0;
  color: #303133;
  font-size: 22px;
  font-weight: 600;
}

.main-card {
  margin-top: 0;
}

.search-form {
  margin-bottom: 16px;
}

.form-item {
  margin-bottom: 12px;
}

.full-width {
  width: 100%;
}

.action-btns {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.search-btn,
.reset-btn {
  margin-bottom: 18px;
}

.table-container {
  overflow-x: auto;
  margin-bottom: 16px;
}

.responsive-table {
  min-width: 800px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 8px;
}

.change-content {
  width: 100%;
}

.change-section {
  margin-bottom: 12px;
}

.change-section:last-child {
  margin-bottom: 0;
}

.change-label {
  font-weight: 500;
  margin-bottom: 6px;
  color: #606266;
}

.change-json {
  margin: 0;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.5;
  max-height: 300px;
  overflow: auto;
  background-color: #f5f7fa;
}

.change-json.old {
  background-color: #fef0f0;
  border: 1px solid #fbc4c4;
}

.change-json.new {
  background-color: #f0f9eb;
  border: 1px solid #c2e7b0;
}

@media (max-width: 768px) {
  .page-title {
    font-size: 18px;
  }

  .search-form {
    margin-bottom: 8px;
  }

  .form-item {
    margin-bottom: 8px;
  }

  .search-btn,
  .reset-btn {
    margin-bottom: 18px;
    flex: 1;
  }

  .action-btns {
    width: 100%;
  }

  .pagination-wrapper {
    justify-content: center;
  }

  .detail-dialog :deep(.el-dialog__body) {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
