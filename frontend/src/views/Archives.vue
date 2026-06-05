<template>
  <div class="archives">
    <div class="page-header">
      <h2>案卷管理</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>新增案卷
      </el-button>
    </div>

    <el-card style="margin-top: 20px;">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.search" placeholder="标题/编号/描述" clearable style="width: 200px;" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="searchForm.category" placeholder="请选择" clearable style="width: 150px;">
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable style="width: 120px;">
            <el-option label="草稿" value="draft" />
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="archives" stripe border style="margin-top: 20px;">
        <el-table-column prop="archive_number" label="案卷编号" width="150" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="category_name" label="分类" width="120" />
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="small">
              {{ scope.row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by" label="创建人" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">查看</el-button>
            <el-button type="success" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; text-align: right;"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="案卷编号" prop="archive_number">
          <el-input v-model="form.archive_number" :disabled="isView" />
        </el-form-item>
        <el-form-item label="案卷标题" prop="title">
          <el-input v-model="form.title" :disabled="isView" />
        </el-form-item>
        <el-form-item label="所属分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择分类" :disabled="isView" style="width: 100%;">
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" :disabled="isView" style="width: 100%;">
            <el-option label="草稿" value="draft" />
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="案卷描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="4" :disabled="isView" />
        </el-form-item>
        <el-form-item v-if="isView" label="创建人">
          <span>{{ form.created_by }}</span>
        </el-form-item>
        <el-form-item v-if="isView" label="创建时间">
          <span>{{ formatDate(form.created_at) }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
        <el-button v-if="!isView" type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { archiveApi, categoryApi } from '@/api'

const archives = ref([])
const categories = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const isView = ref(false)
const formRef = ref(null)

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
  archive_number: [{ required: true, message: '请输入案卷编号', trigger: 'blur' }],
  title: [{ required: true, message: '请输入案卷标题', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }]
}

const dialogTitle = computed(() => {
  if (isView.value) return '查看案卷'
  return isEdit.value ? '编辑案卷' : '新增案卷'
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
  return new Date(dateStr).toLocaleString('zh-CN')
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
    ElMessage.error('加载案卷失败')
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
  ElMessageBox.confirm('确定要删除该案卷吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await archiveApi.delete(row.id)
      ElMessage.success('删除成功')
      loadArchives()
    } catch (error) {
      ElMessage.error('删除失败')
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
      ElMessage.success('更新成功')
    } else {
      await archiveApi.create(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadArchives()
  } catch (error) {
    if (error !== false) {
      ElMessage.error('操作失败')
    }
  }
}

onMounted(() => {
  loadCategories()
  loadArchives()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.search-form {
  margin-bottom: 20px;
}
</style>
