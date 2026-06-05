<template>
  <div class="categories">
    <div class="page-header">
      <h2 class="page-title">分类管理</h2>
      <el-button type="primary" @click="handleAdd" class="add-btn">
        <el-icon><Plus /></el-icon>
        <span class="btn-text">新增分类</span>
      </el-button>
    </div>

    <el-card class="main-card">
      <div class="table-container">
        <el-table :data="categories" stripe border class="responsive-table">
          <el-table-column prop="name" label="分类名称" min-width="120" />
          <el-table-column prop="parent_name" label="父分类" min-width="100">
            <template #default="scope">
              {{ scope.row.parent_name || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
          <el-table-column prop="created_at" label="创建时间" min-width="150">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" fixed="right" width="130">
            <template #default="scope">
              <div class="action-buttons">
                <el-button type="primary" link size="small" @click="handleEdit(scope.row)">编辑</el-button>
                <el-button type="danger" link size="small" @click="handleDelete(scope.row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑分类' : '新增分类'" :width="dialogWidth" class="form-dialog">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" class="dialog-form">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="父分类" prop="parent">
          <el-select v-model="form.parent" placeholder="请选择父分类" clearable class="full-width">
            <el-option
              v-for="cat in parentCategories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { categoryApi } from '@/api'

const categories = ref([])
const parentCategories = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const isMobile = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

const dialogWidth = computed(() => {
  if (isMobile.value) return '95%'
  return '500px'
})

const form = reactive({
  id: null,
  name: '',
  parent: null,
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }]
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadCategories = async () => {
  try {
    const res = await categoryApi.getAll()
    categories.value = res.data.results || res.data
    parentCategories.value = categories.value
  } catch (error) {
    ElMessage.error('加载分类失败')
  }
}

const handleAdd = () => {
  isEdit.value = false
  Object.assign(form, { id: null, name: '', parent: null, description: '' })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    name: row.name,
    parent: row.parent,
    description: row.description
  })
  parentCategories.value = categories.value.filter(c => c.id !== row.id)
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该分类吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await categoryApi.delete(row.id)
      ElMessage.success('删除成功')
      loadCategories()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    const data = { ...form }
    if (!data.parent) delete data.parent

    if (isEdit.value) {
      await categoryApi.update(form.id, data)
      ElMessage.success('更新成功')
    } else {
      await categoryApi.create(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadCategories()
  } catch (error) {
    if (error !== false) {
      ElMessage.error('操作失败')
    }
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  loadCategories()
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

.table-container {
  overflow-x: auto;
}

.responsive-table {
  min-width: 600px;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.full-width {
  width: 100%;
}

@media (max-width: 768px) {
  .page-title {
    font-size: 18px;
  }

  .btn-text {
    display: none;
  }

  .form-dialog :deep(.el-dialog__body) {
    padding: 16px;
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
