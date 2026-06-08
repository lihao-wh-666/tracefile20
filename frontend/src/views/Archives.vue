<template>
  <div class="archives">
    <div class="page-header">
      <h2 class="page-title">{{ t('archives.title') }}</h2>
      <el-button type="primary" @click="handleAdd" class="add-btn">
        <el-icon><Plus /></el-icon>
        <span class="btn-text">{{ t('common.add') + t('archives.archiveTitle').slice(0, 2) }}</span>
      </el-button>
    </div>

    <el-card class="main-card">
      <el-form :model="searchForm" class="search-form">
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item :label="t('common.search')" class="form-item">
              <el-input v-model="searchForm.search" :placeholder="t('common.search') + '...'" clearable class="full-width" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item :label="t('archives.category')" class="form-item">
              <el-select v-model="searchForm.category" :placeholder="t('common.select')" clearable class="full-width">
                <el-option
                  v-for="cat in categories"
                  :key="cat.id"
                  :label="cat.name"
                  :value="cat.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item :label="t('archives.status')" class="form-item">
              <el-select v-model="searchForm.status" :placeholder="t('common.select')" clearable class="full-width">
                <el-option :label="t('archives.draft')" value="draft" />
                <el-option :label="t('archives.pending')" value="pending" />
                <el-option :label="t('archives.approved')" value="approved" />
                <el-option :label="t('archives.rejected')" value="rejected" />
              </el-select>
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
        <el-table :data="archives" stripe border class="responsive-table">
          <el-table-column prop="archive_number" :label="t('archives.archiveNumber')" min-width="110" />
          <el-table-column prop="title" :label="t('archives.archiveTitle')" min-width="150" show-overflow-tooltip />
          <el-table-column prop="category_name" :label="t('archives.category')" min-width="90" />
          <el-table-column prop="status_display" :label="t('archives.status')" width="90">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)" size="small">
                {{ scope.row.status_display }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_by" :label="t('archives.createdBy')" width="90" />
          <el-table-column prop="created_at" :label="t('archives.createdAt')" min-width="150">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column :label="t('common.view')" fixed="right" width="150">
            <template #default="scope">
              <div class="action-buttons">
                <el-button type="primary" link size="small" @click="handleView(scope.row)">{{ t('common.view') }}</el-button>
                <el-button type="success" link size="small" @click="handleEdit(scope.row)">{{ t('common.edit') }}</el-button>
                <el-button type="danger" link size="small" @click="handleDelete(scope.row)">{{ t('common.delete') }}</el-button>
              </div>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" :width="dialogWidth" class="form-dialog">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="90px" class="dialog-form">
        <el-form-item :label="t('archives.archiveNumber')" prop="archive_number">
          <el-input v-model="form.archive_number" :disabled="isView" />
        </el-form-item>
        <el-form-item :label="t('archives.archiveTitle')" prop="title">
          <el-input v-model="form.title" :disabled="isView" />
        </el-form-item>
        <el-form-item :label="t('archives.category')" prop="category">
          <el-select v-model="form.category" :placeholder="t('common.select') + t('archives.category')" :disabled="isView" class="full-width">
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('archives.status')" prop="status">
          <el-select v-model="form.status" :disabled="isView" class="full-width">
            <el-option :label="t('archives.draft')" value="draft" />
            <el-option :label="t('archives.pending')" value="pending" />
            <el-option :label="t('archives.approved')" value="approved" />
            <el-option :label="t('archives.rejected')" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('archives.description')" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="4" :disabled="isView" />
        </el-form-item>
        <el-form-item v-if="isView" :label="t('archives.createdBy')">
          <span>{{ form.created_by }}</span>
        </el-form-item>
        <el-form-item v-if="isView" :label="t('archives.createdAt')">
          <span>{{ formatDate(form.created_at) }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.close') }}</el-button>
        <el-button v-if="!isView" type="primary" @click="handleSubmit">{{ t('common.confirm') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { archiveApi, categoryApi } from '@/api'
import { useLocale } from '@/composables/useLocale'

const { t, locale } = useLocale()

const archives = ref([])
const categories = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const isView = ref(false)
const formRef = ref(null)
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
  category: null,
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const form = reactive({
  id: null,
  archive_number: '',
  title: '',
  description: '',
  category: null,
  status: 'draft',
  created_by: '',
  created_at: ''
})

const rules = {
  archive_number: [{ required: true, message: t('validation.required'), trigger: 'blur' }],
  title: [{ required: true, message: t('validation.required'), trigger: 'blur' }],
  category: [{ required: true, message: t('validation.required'), trigger: 'change' }]
}

const dialogTitle = computed(() => {
  if (isView.value) return t('common.view') + t('archives.archiveTitle').slice(0, 2)
  return isEdit.value ? t('common.edit') + t('archives.archiveTitle').slice(0, 2) : t('common.add') + t('archives.archiveTitle').slice(0, 2)
})

const getStatusType = (status) => {
  const statusMap = {
    draft: 'info',
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return statusMap[status] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString(locale.value)
}

const loadCategories = async () => {
  try {
    const res = await categoryApi.getSimple()
    categories.value = res.data
  } catch (error) {
    console.error('加载分类失败:', error)
  }
}

const loadArchives = async () => {
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm
    }
    if (!params.search) delete params.search
    if (!params.category) delete params.category
    if (!params.status) delete params.status

    const res = await archiveApi.getAll(params)
    archives.value = res.data.results || res.data
    pagination.total = res.data.count || archives.value.length
  } catch (error) {
    ElMessage.error(t('errors.loadFailed'))
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadArchives()
}

const handleReset = () => {
  searchForm.search = ''
  searchForm.category = null
  searchForm.status = ''
  pagination.page = 1
  loadArchives()
}

const handlePageChange = () => loadArchives()
const handleSizeChange = () => {
  pagination.page = 1
  loadArchives()
}

const handleAdd = () => {
  isEdit.value = false
  isView.value = false
  Object.assign(form, {
    id: null,
    archive_number: '',
    title: '',
    description: '',
    category: null,
    status: 'draft',
    created_by: '',
    created_at: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  isView.value = false
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

const handleView = (row) => {
  isEdit.value = false
  isView.value = true
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(t('common.delete') + '?', t('common.warning'), {
    confirmButtonText: t('common.confirm'),
    cancelButtonText: t('common.cancel'),
    type: 'warning'
  }).then(async () => {
    try {
      await archiveApi.delete(row.id)
      ElMessage.success(t('common.success'))
      loadArchives()
    } catch (error) {
      ElMessage.error(t('errors.deleteFailed'))
    }
  })
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    const data = { ...form }
    delete data.created_by
    delete data.created_at

    if (isEdit.value) {
      await archiveApi.update(form.id, data)
      ElMessage.success(t('common.success'))
    } else {
      await archiveApi.create(data)
      ElMessage.success(t('common.success'))
    }
    dialogVisible.value = false
    loadArchives()
  } catch (error) {
    if (error !== false) {
      ElMessage.error(t('errors.saveFailed'))
    }
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  loadCategories()
  loadArchives()
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

.add-btn {
  flex-shrink: 0;
}

.btn-text {
  display: inline;
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

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 8px;
}

.dialog-form {
  padding-right: 10px;
}

@media (max-width: 768px) {
  .page-title {
    font-size: 18px;
  }

  .btn-text {
    display: none;
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

  .form-dialog :deep(.el-dialog__body) {
    padding: 16px;
  }

  .dialog-form :deep(.el-form-item__label) {
    width: 70px !important;
  }
}

@media (max-width: 480px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .add-btn {
    width: 100%;
    justify-content: center;
  }

  .btn-text {
    display: inline;
  }
}
</style>
