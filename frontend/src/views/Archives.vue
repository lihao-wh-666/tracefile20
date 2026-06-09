<template>
  <div class="archives">
    <div class="page-header">
      <h2 class="page-title">{{ t('archives.title') }}</h2>
      <div class="header-actions">
        <el-dropdown
          @command="handleExportCommand"
          class="export-dropdown"
          :disabled="selectedIds.length === 0"
          trigger="click"
          placement="bottom-end"
        >
          <el-button type="success">
            <el-icon><Download /></el-icon>
            <span class="btn-text">导出{{ selectedIds.length > 0 ? `(${selectedIds.length})` : '' }}</span>
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="excel">导出 Excel (.xlsx)</el-dropdown-item>
              <el-dropdown-item command="pdf">导出 PDF</el-dropdown-item>
              <el-dropdown-item command="word">导出 Word (.docx)</el-dropdown-item>
              <el-dropdown-item command="csv">导出 CSV</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="primary" @click="handleAdd" class="add-btn">
          <el-icon><Plus /></el-icon>
          <span class="btn-text">{{ t('common.add') + t('archives.archiveTitle').slice(0, 2) }}</span>
        </el-button>
      </div>
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
        <el-table :data="archives" stripe border class="responsive-table" @selection-change="handleSelectionChange">
          <el-table-column type="selection" width="55" />
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
          <el-table-column :label="t('common.operation')" fixed="right" width="280">
            <template #default="scope">
              <div class="action-buttons">
                <el-button type="primary" link size="small" @click="handleView(scope.row)">{{ t('common.view') }}</el-button>
                <el-button 
                  v-if="canEdit(scope.row)" 
                  type="success" 
                  link 
                  size="small" 
                  @click="handleEdit(scope.row)"
                >{{ t('common.edit') }}</el-button>
                <el-button 
                  v-if="canSubmit(scope.row)" 
                  type="warning" 
                  link 
                  size="small" 
                  @click="handleSubmitReview(scope.row)"
                >提交审核</el-button>
                <el-button 
                  v-if="canReview(scope.row)" 
                  type="success" 
                  link 
                  size="small" 
                  @click="handleApprove(scope.row)"
                >审核通过</el-button>
                <el-button 
                  v-if="canReview(scope.row)" 
                  type="danger" 
                  link 
                  size="small" 
                  @click="handleReject(scope.row)"
                >审核驳回</el-button>
                <el-button 
                  v-if="canDelete(scope.row)" 
                  type="danger" 
                  link 
                  size="small" 
                  @click="handleDelete(scope.row)"
                >{{ t('common.delete') }}</el-button>
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
          <span>{{ form.created_by_username || form.created_by }}</span>
        </el-form-item>
        <el-form-item v-if="isView" :label="t('archives.createdAt')">
          <span>{{ formatDate(form.created_at) }}</span>
        </el-form-item>
        <el-form-item v-if="isView && form.submitted_at" :label="提交时间">
          <span>{{ formatDate(form.submitted_at) }}</span>
        </el-form-item>
        <el-form-item v-if="isView && form.reviewed_by_username" :label="审核人">
          <span>{{ form.reviewed_by_username }}</span>
        </el-form-item>
        <el-form-item v-if="isView && form.reviewed_at" :label="审核时间">
          <span>{{ formatDate(form.reviewed_at) }}</span>
        </el-form-item>
        <el-form-item v-if="isView && form.review_comment" :label="审核意见">
          <span>{{ form.review_comment }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.close') }}</el-button>
        <el-button v-if="!isView" type="primary" @click="handleSubmit">{{ t('common.confirm') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="rejectDialogVisible"
      title="审核驳回"
      width="500px"
    >
      <el-form :model="rejectForm" :rules="rejectRules" ref="rejectFormRef" label-width="80px">
        <el-form-item label="案卷标题">
          <span>{{ currentArchive?.title }}</span>
        </el-form-item>
        <el-form-item label="案卷编号">
          <span>{{ currentArchive?.archive_number }}</span>
        </el-form-item>
        <el-form-item label="审核意见" prop="comment">
          <el-input
            v-model="rejectForm.comment"
            type="textarea"
            :rows="4"
            placeholder="请填写审核意见（必填）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmReject">确认驳回</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download, ArrowDown } from '@element-plus/icons-vue'
import { archiveApi, categoryApi, authApi } from '@/api'
import { useLocale } from '@/composables/useLocale'

const { t, locale } = useLocale()

const archives = ref([])
const categories = ref([])
const dialogVisible = ref(false)
const selectedIds = ref([])
const selectedRows = ref([])
const isEdit = ref(false)
const isView = ref(false)
const formRef = ref(null)
const isMobile = ref(false)
const userInfo = ref(null)

const rejectDialogVisible = ref(false)
const rejectFormRef = ref(null)
const currentArchive = ref(null)
const rejectForm = reactive({
  comment: ''
})

const rejectRules = {
  comment: [{ required: true, message: '请填写审核意见', trigger: 'blur' }]
}

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

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
  selectedIds.value = selection.map(item => item.id)
}

const downloadFile = (blob, filename) => {
  const url = window.URL.createObjectURL(new Blob([blob]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

const getFilenameFromContentDisposition = (contentDisposition, fallbackName) => {
  if (!contentDisposition) return fallbackName
  const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition)
  if (matches && matches[1]) {
    let filename = matches[1].replace(/['"]/g, '')
    try {
      filename = decodeURIComponent(filename)
    } catch (e) {
      // keep original
    }
    return filename
  }
  return fallbackName
}

const handleExportCommand = async (format) => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择要导出的案卷')
    return
  }

  const formatNames = {
    excel: 'Excel',
    pdf: 'PDF',
    word: 'Word',
    csv: 'CSV'
  }

  try {
    const res = await archiveApi.export({
      ids: selectedIds.value,
      format: format
    })

    const contentDisposition = res.headers['content-disposition']
    const fallbackName = `archives_export_${new Date().toISOString().slice(0, 10)}.${format === 'excel' ? 'xlsx' : format === 'word' ? 'docx' : format}`
    const filename = getFilenameFromContentDisposition(contentDisposition, fallbackName)

    downloadFile(res.data, filename)
    ElMessage.success(`导出${formatNames[format] || format}成功`)
  } catch (error) {
    console.error('导出失败:', error)
    if (error.response && error.response.data && error.response.data instanceof Blob) {
      const reader = new FileReader()
      reader.onload = () => {
        try {
          const err = JSON.parse(reader.result)
          ElMessage.error(err.detail || '导出失败')
        } catch (e) {
          ElMessage.error('导出失败')
        }
      }
      reader.readAsText(error.response.data)
    } else {
      ElMessage.error(error?.response?.data?.detail || '导出失败')
    }
  }
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
    delete data.created_by_username
    delete data.reviewed_by
    delete data.reviewed_by_username
    delete data.reviewed_at
    delete data.review_comment
    delete data.submitted_at

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

const isAdmin = () => {
  return userInfo.value?.is_staff || false
}

const isEntryUser = () => {
  return userInfo.value?.is_archive_entry || false
}

const isReviewUser = () => {
  return userInfo.value?.is_archive_review || false
}

const canEdit = (row) => {
  if (isAdmin()) return true
  if (isReviewUser()) return false
  if (isEntryUser()) {
    return row.status === 'draft' || row.status === 'rejected'
  }
  return false
}

const canSubmit = (row) => {
  if (isAdmin()) return true
  if (isEntryUser()) {
    return row.status === 'draft' || row.status === 'rejected'
  }
  return false
}

const canReview = (row) => {
  if (isAdmin()) return true
  if (isReviewUser()) {
    return row.status === 'pending'
  }
  return false
}

const canDelete = (row) => {
  return isAdmin()
}

const handleSubmitReview = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要提交案卷「${row.title}」进行审核吗？`,
      '提交审核',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await archiveApi.submitForReview(row.id)
    ElMessage.success('提交审核成功')
    loadArchives()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('提交审核失败:', error)
      ElMessage.error('提交审核失败')
    }
  }
}

const handleApprove = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要通过案卷「${row.title}」的审核吗？`,
      '审核通过',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'success'
      }
    )
    await archiveApi.approve(row.id, { comment: '' })
    ElMessage.success('审核通过成功')
    loadArchives()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('审核通过失败:', error)
      ElMessage.error(error?.response?.data?.detail || '审核通过失败')
    }
  }
}

const handleReject = (row) => {
  currentArchive.value = row
  rejectForm.comment = ''
  rejectDialogVisible.value = true
}

const confirmReject = async () => {
  try {
    await rejectFormRef.value.validate()
    await archiveApi.reject(currentArchive.value.id, { comment: rejectForm.comment })
    ElMessage.success('审核驳回成功')
    rejectDialogVisible.value = false
    loadArchives()
  } catch (error) {
    if (error !== false) {
      console.error('审核驳回失败:', error)
      ElMessage.error(error?.response?.data?.detail || '审核驳回失败')
    }
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  loadUserInfo()
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

.header-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.export-dropdown {
  flex-shrink: 0;
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

  .header-actions {
    width: 100%;
  }

  .export-dropdown,
  .add-btn {
    flex: 1;
    justify-content: center;
  }

  .export-dropdown .el-button {
    width: 100%;
    justify-content: center;
  }

  .btn-text {
    display: inline;
  }
}
</style>
