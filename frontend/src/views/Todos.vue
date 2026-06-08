<template>
  <div class="todos">
    <div class="page-header">
      <h2 class="page-title">{{ t('todos.title') }}</h2>
      <el-button type="primary" :icon="Plus" @click="handleAdd">
        {{ t('common.add') + t('todos.todoTitle').slice(0, 2) }}
      </el-button>
    </div>

    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item :label="t('todos.status')">
          <el-select v-model="filterForm.status" :placeholder="t('common.all') + t('todos.status')" clearable @change="loadData">
            <el-option :label="t('todos.pending')" value="pending" />
            <el-option :label="t('todos.completed')" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('todos.priority')">
          <el-select v-model="filterForm.priority" :placeholder="t('common.all') + t('todos.priority')" clearable @change="loadData">
            <el-option :label="t('todos.high')" value="high" />
            <el-option :label="t('todos.medium')" value="medium" />
            <el-option :label="t('todos.low')" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('common.search')">
          <el-input v-model="filterForm.search" :placeholder="t('common.search') + '...'" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">{{ t('common.search') }}</el-button>
          <el-button @click="resetFilter">{{ t('common.reset') }}</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <el-table :data="tableData" stripe class="responsive-table" v-loading="loading">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="title" :label="t('todos.todoTitle')" min-width="180" show-overflow-tooltip />
        <el-table-column prop="description" :label="t('todos.description')" min-width="200" show-overflow-tooltip />
        <el-table-column prop="priority_display" :label="t('todos.priority')" width="100">
          <template #default="scope">
            <el-tag :type="getPriorityType(scope.row.priority)" size="small">
              {{ scope.row.priority_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status_display" :label="t('todos.status')" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'completed' ? 'success' : 'warning'" size="small">
              {{ scope.row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="due_date" :label="t('todos.dueDate')" width="170">
          <template #default="scope">
            {{ formatDateTime(scope.row.due_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="is_read" :label="t('todos.isRead')" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_read ? 'info' : 'danger'" size="small">
              {{ scope.row.is_read ? t('common.view') : t('common.info') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" :label="t('todos.createdAt')" width="170">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column :label="t('common.view')" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" link size="small" @click="handleToggleStatus(scope.row)">
              {{ scope.row.status === 'completed' ? t('common.reset') : t('todos.completed') }}
            </el-button>
            <el-button type="primary" link size="small" @click="handleEdit(scope.row)">
              {{ t('common.edit') }}
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(scope.row)">
              {{ t('common.delete') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        class="pagination"
      />
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? t('common.edit') + t('todos.todoTitle') : t('common.add') + t('todos.todoTitle')"
      width="500px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item :label="t('todos.todoTitle')" prop="title">
          <el-input v-model="form.title" :placeholder="t('validation.required')" />
        </el-form-item>
        <el-form-item :label="t('todos.description')">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            :placeholder="t('common.input') + t('todos.description')"
          />
        </el-form-item>
        <el-form-item :label="t('todos.priority')" prop="priority">
          <el-select v-model="form.priority" :placeholder="t('common.select') + t('todos.priority')">
            <el-option :label="t('todos.high')" value="high" />
            <el-option :label="t('todos.medium')" value="medium" />
            <el-option :label="t('todos.low')" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('todos.dueDate')">
          <el-date-picker
            v-model="form.due_date"
            type="datetime"
            :placeholder="t('common.select') + t('todos.dueDate')"
            style="width: 100%"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item :label="t('todos.status')" prop="status">
          <el-select v-model="form.status" :placeholder="t('common.select') + t('todos.status')">
            <el-option :label="t('todos.pending')" value="pending" />
            <el-option :label="t('todos.completed')" value="completed" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleSubmit">{{ t('common.confirm') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { todoApi } from '@/api'
import { useLocale } from '@/composables/useLocale'

const { t, locale } = useLocale()

const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const filterForm = reactive({
  status: '',
  priority: '',
  search: ''
})

const form = reactive({
  id: null,
  title: '',
  description: '',
  priority: 'medium',
  status: 'pending',
  due_date: null,
  is_read: false
})

const rules = {
  title: [{ required: true, message: t('validation.required'), trigger: 'blur' }],
  priority: [{ required: true, message: t('validation.required'), trigger: 'change' }],
  status: [{ required: true, message: t('validation.required'), trigger: 'change' }]
}

const getPriorityType = (priority) => {
  const map = { high: 'danger', medium: 'warning', low: 'info' }
  return map[priority] || 'info'
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString(locale.value, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ordering: '-created_at'
    }
    if (filterForm.status) params.status = filterForm.status
    if (filterForm.priority) params.priority = filterForm.priority
    if (filterForm.search) params.search = filterForm.search

    const res = await todoApi.getAll(params)
    tableData.value = res.data.results || res.data
    total.value = res.data.count || tableData.value.length
  } catch (error) {
    console.error('加载待办列表失败:', error)
    ElMessage.error(t('errors.loadFailed'))
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.status = ''
  filterForm.priority = ''
  filterForm.search = ''
  currentPage.value = 1
  loadData()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadData()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadData()
}

const handleAdd = () => {
  isEdit.value = false
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, row)
  dialogVisible.value = true
}

const resetForm = () => {
  form.id = null
  form.title = ''
  form.description = ''
  form.priority = 'medium'
  form.status = 'pending'
  form.due_date = null
  form.is_read = false
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await todoApi.update(form.id, form)
          ElMessage.success(t('common.success'))
        } else {
          await todoApi.create(form)
          ElMessage.success(t('common.success'))
        }
        dialogVisible.value = false
        loadData()
      } catch (error) {
        console.error('提交失败:', error)
        ElMessage.error(t('errors.saveFailed'))
      }
    }
  })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(t('common.delete') + '?', t('common.warning'), {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning'
    })
    await todoApi.delete(row.id)
    ElMessage.success(t('common.success'))
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(t('errors.deleteFailed'))
    }
  }
}

const handleToggleStatus = async (row) => {
  try {
    const res = await todoApi.toggleStatus(row.id)
    Object.assign(row, res.data)
    ElMessage.success(row.status === 'completed' ? t('common.success') : t('common.success'))
  } catch (error) {
    console.error('切换状态失败:', error)
    ElMessage.error(t('errors.updateFailed'))
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  color: #303133;
  font-size: 22px;
  font-weight: 600;
}

.filter-card {
  margin-bottom: 16px;
}

.filter-form {
  margin-bottom: 0;
}

.table-card {
  margin-bottom: 16px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.responsive-table {
  min-width: 100%;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .page-title {
    font-size: 18px;
  }

  .filter-form :deep(.el-form-item) {
    margin-bottom: 12px;
  }
}
</style>
