<template>
  <div class="profile-page">
    <h2 class="page-title">个人中心</h2>

    <div class="profile-container">
      <div class="profile-header">
        <div class="avatar-section">
          <div class="avatar-wrapper">
            <el-avatar :size="100" class="user-avatar">
              <el-icon :size="50"><UserFilled /></el-icon>
            </el-avatar>
          </div>
          <div class="user-basic">
            <h3 class="user-name">{{ userInfo?.username || '用户' }}</h3>
            <p class="user-role">{{ userInfo?.is_staff ? '管理员' : '普通用户' }}</p>
            <p class="user-email">{{ userInfo?.email || '未设置邮箱' }}</p>
          </div>
        </div>
        <div class="stats-section">
          <div class="stat-item">
            <div class="stat-value">{{ stats.totalArchives }}</div>
            <div class="stat-label">案卷总数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.pendingTodos }}</div>
            <div class="stat-label">待办事项</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ formatDate(userInfo?.date_joined) }}</div>
            <div class="stat-label">加入时间</div>
          </div>
        </div>
      </div>

      <el-tabs v-model="activeTab" class="profile-tabs" type="border-card">
        <el-tab-pane label="基本信息" name="basic">
          <el-form
            ref="basicFormRef"
            :model="basicForm"
            :rules="basicRules"
            label-width="100px"
            class="profile-form"
            :disabled="!isEditing"
          >
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12" :md="12" :lg="12">
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="basicForm.username" disabled />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="12" :lg="12">
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="basicForm.email" placeholder="请输入邮箱" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12" :md="12" :lg="12">
                <el-form-item label="姓名" prop="first_name">
                  <el-input v-model="basicForm.first_name" placeholder="请输入姓名" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="12" :lg="12">
                <el-form-item label="性别" prop="gender">
                  <el-select v-model="basicForm.gender" placeholder="请选择性别" style="width: 100%">
                    <el-option label="男" value="male" />
                    <el-option label="女" value="female" />
                    <el-option label="其他" value="other" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12" :md="12" :lg="12">
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="basicForm.phone" placeholder="请输入手机号" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="12" :lg="12">
                <el-form-item label="部门" prop="department">
                  <el-input v-model="basicForm.department" placeholder="请输入部门" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="24" :md="24" :lg="24">
                <el-form-item label="职位" prop="position">
                  <el-input v-model="basicForm.position" placeholder="请输入职位" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="24" :md="24" :lg="24">
                <el-form-item label="个人简介" prop="bio">
                  <el-input
                    v-model="basicForm.bio"
                    type="textarea"
                    :rows="4"
                    placeholder="请输入个人简介"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
          <div class="form-actions">
            <el-button v-if="!isEditing" type="primary" @click="handleEdit">
              <el-icon><Edit /></el-icon>
              编辑资料
            </el-button>
            <template v-else>
              <el-button @click="handleCancelEdit">取消</el-button>
              <el-button type="primary" @click="handleSaveBasic" :loading="saving">
                保存修改
              </el-button>
            </template>
          </div>
        </el-tab-pane>

        <el-tab-pane label="安全设置" name="security">
          <div class="security-section">
            <div class="security-item">
              <div class="security-info">
                <div class="security-icon">
                  <el-icon :size="24"><Lock /></el-icon>
                </div>
                <div class="security-content">
                  <h4>登录密码</h4>
                  <p>定期修改密码可以提高账户安全性</p>
                </div>
              </div>
              <el-button type="primary" @click="passwordDialogVisible = true">
                修改密码
              </el-button>
            </div>

            <div class="security-item">
              <div class="security-info">
                <div class="security-icon warning">
                  <el-icon :size="24"><Warning /></el-icon>
                </div>
                <div class="security-content">
                  <h4>登录记录</h4>
                  <p>查看近期的登录活动，确保账户安全</p>
                </div>
              </div>
              <el-button @click="loadLoginInfo">查看详情</el-button>
            </div>

            <div class="security-item">
              <div class="security-info">
                <div class="security-icon success">
                  <el-icon :size="24"><CircleCheck /></el-icon>
                </div>
                <div class="security-content">
                  <h4>账户状态</h4>
                  <p>您的账户目前处于正常状态</p>
                </div>
              </div>
              <el-tag type="success">正常</el-tag>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="偏好设置" name="preferences">
          <el-form
            ref="prefFormRef"
            :model="preferencesForm"
            label-width="120px"
            class="preferences-form"
          >
            <el-form-item label="主题设置">
              <el-radio-group v-model="preferencesForm.theme">
                <el-radio value="light">
                  <el-icon><Sunny /></el-icon>
                  浅色主题
                </el-radio>
                <el-radio value="dark">
                  <el-icon><Moon /></el-icon>
                  深色主题
                </el-radio>
                <el-radio value="auto">
                  <el-icon><Monitor /></el-icon>
                  跟随系统
                </el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="语言设置">
              <el-select v-model="preferencesForm.language" style="width: 200px">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en" />
              </el-select>
            </el-form-item>

            <el-form-item label="每页条数">
              <el-select v-model="preferencesForm.page_size" style="width: 120px">
                <el-option :label="10" :value="10" />
                <el-option :label="20" :value="20" />
                <el-option :label="30" :value="30" />
                <el-option :label="50" :value="50" />
              </el-select>
            </el-form-item>

            <el-divider content-position="left">通知设置</el-divider>

            <el-form-item label="邮件通知">
              <el-switch v-model="preferencesForm.email_notification" />
              <span class="form-desc">接收系统邮件通知</span>
            </el-form-item>

            <el-form-item label="音效提醒">
              <el-switch v-model="preferencesForm.sound_effect" />
              <span class="form-desc">操作时播放提示音效</span>
            </el-form-item>

            <el-form-item label="自动保存">
              <el-switch v-model="preferencesForm.auto_save" />
              <span class="form-desc">自动保存表单内容</span>
            </el-form-item>

            <el-form-item label="侧边栏收起">
              <el-switch v-model="preferencesForm.sidebar_collapsed" />
              <span class="form-desc">默认收起侧边导航栏</span>
            </el-form-item>

            <div class="form-actions">
              <el-button @click="handleResetPreferences">重置默认</el-button>
              <el-button type="primary" @click="handleSavePreferences" :loading="savingPref">
                保存设置
              </el-button>
            </div>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="旧密码" prop="old_password">
          <el-input
            v-model="passwordForm.old_password"
            type="password"
            show-password
            placeholder="请输入旧密码"
          />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            show-password
            placeholder="请输入新密码"
          />
          <div class="password-tip">
            密码长度至少8位，包含字母和数字
          </div>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            show-password
            placeholder="请再次输入新密码"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleChangePassword" :loading="changingPassword">
          确认修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  UserFilled, Edit, Lock, Warning, CircleCheck,
  Sunny, Moon, Monitor
} from '@element-plus/icons-vue'
import { authApi, userApi, archiveApi, todoApi } from '@/api'

const activeTab = ref('basic')
const isEditing = ref(false)
const saving = ref(false)
const savingPref = ref(false)
const changingPassword = ref(false)
const passwordDialogVisible = ref(false)

const userInfo = ref(null)
const stats = reactive({
  totalArchives: 0,
  pendingTodos: 0
})

const basicForm = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
  gender: '',
  department: '',
  position: '',
  bio: ''
})

const basicRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateNewPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入新密码'))
  } else if (value.length < 8) {
    callback(new Error('密码长度至少8位'))
  } else if (!/[a-zA-Z]/.test(value) || !/[0-9]/.test(value)) {
    callback(new Error('密码需要包含字母和数字'))
  } else {
    callback()
  }
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入旧密码', trigger: 'blur' }
  ],
  new_password: [
    { validator: validateNewPassword, trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const preferencesForm = reactive({
  theme: 'light',
  language: 'zh-CN',
  email_notification: true,
  sound_effect: false,
  auto_save: true,
  page_size: 10,
  sidebar_collapsed: false
})

const basicFormRef = ref(null)
const passwordFormRef = ref(null)
const prefFormRef = ref(null)

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const loadUserInfo = async () => {
  try {
    const res = await authApi.getUserInfo()
    userInfo.value = res.data
    basicForm.username = res.data.username || ''
    basicForm.email = res.data.email || ''
    basicForm.first_name = res.data.first_name || ''
    basicForm.last_name = res.data.last_name || ''
    if (res.data.profile) {
      basicForm.phone = res.data.profile.phone || ''
      basicForm.gender = res.data.profile.gender || ''
      basicForm.department = res.data.profile.department || ''
      basicForm.position = res.data.profile.position || ''
      basicForm.bio = res.data.profile.bio || ''
    }
    if (res.data.preferences) {
      Object.assign(preferencesForm, res.data.preferences)
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    ElMessage.error('加载用户信息失败')
  }
}

const loadStats = async () => {
  try {
    const [archivesRes, todosRes] = await Promise.all([
      archiveApi.getAll({ page_size: 1000 }),
      todoApi.getAll({ status: 'pending', page_size: 1000 })
    ])
    const archives = archivesRes.data.results || archivesRes.data
    const todos = todosRes.data.results || todosRes.data
    stats.totalArchives = archives.length
    stats.pendingTodos = todos.length
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadLoginInfo = () => {
  ElMessageBox.alert(
    '登录记录功能将在后续版本中开放，敬请期待。',
    '登录记录',
    {
      confirmButtonText: '知道了',
      type: 'info'
    }
  )
}

const handleEdit = () => {
  isEditing.value = true
}

const handleCancelEdit = () => {
  isEditing.value = false
  loadUserInfo()
}

const handleSaveBasic = async () => {
  if (!basicFormRef.value) return
  try {
    await basicFormRef.value.validate()
  } catch (e) {
    return
  }

  saving.value = true
  try {
    const data = {
      email: basicForm.email,
      first_name: basicForm.first_name,
      last_name: basicForm.last_name,
      profile: {
        phone: basicForm.phone,
        gender: basicForm.gender,
        department: basicForm.department,
        position: basicForm.position,
        bio: basicForm.bio
      }
    }
    const res = await authApi.updateUserInfo(data)
    userInfo.value = res.data
    isEditing.value = false
    ElMessage.success('保存成功')
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        const user = JSON.parse(userStr)
        user.email = res.data.email
        user.username = res.data.username
        localStorage.setItem('user', JSON.stringify(user))
      } catch (e) {}
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  try {
    await passwordFormRef.value.validate()
  } catch (e) {
    return
  }

  changingPassword.value = true
  try {
    await authApi.changePassword(passwordForm)
    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
  } catch (error) {
    console.error('密码修改失败:', error)
    const errors = error.response?.data
    if (errors && typeof errors === 'object') {
      const firstError = Object.values(errors)[0]
      ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError)
    } else {
      ElMessage.error('密码修改失败')
    }
  } finally {
    changingPassword.value = false
  }
}

const handleSavePreferences = async () => {
  savingPref.value = true
  try {
    const res = await userApi.updatePreferences(preferencesForm)
    Object.assign(preferencesForm, res.data)
    ElMessage.success('偏好设置已保存')
  } catch (error) {
    console.error('保存偏好设置失败:', error)
    ElMessage.error('保存失败')
  } finally {
    savingPref.value = false
  }
}

const handleResetPreferences = () => {
  ElMessageBox.confirm('确定要重置为默认设置吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    preferencesForm.theme = 'light'
    preferencesForm.language = 'zh-CN'
    preferencesForm.email_notification = true
    preferencesForm.sound_effect = false
    preferencesForm.auto_save = true
    preferencesForm.page_size = 10
    preferencesForm.sidebar_collapsed = false
    ElMessage.success('已重置为默认设置')
  }).catch(() => {})
}

onMounted(() => {
  loadUserInfo()
  loadStats()
})
</script>

<style scoped>
.profile-page {
  padding: 0;
}

.page-title {
  margin-bottom: 20px;
  color: #303133;
  font-size: 22px;
  font-weight: 600;
}

.profile-container {
  max-width: 1000px;
  margin: 0 auto;
}

.profile-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 20px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar-wrapper {
  flex-shrink: 0;
}

.user-avatar {
  background: rgba(255, 255, 255, 0.3);
  border: 3px solid rgba(255, 255, 255, 0.5);
}

.user-basic {
  min-width: 0;
}

.user-name {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 6px 0;
}

.user-role {
  font-size: 14px;
  opacity: 0.9;
  margin: 0 0 4px 0;
}

.user-email {
  font-size: 13px;
  opacity: 0.8;
  margin: 0;
}

.stats-section {
  display: flex;
  gap: 30px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  opacity: 0.8;
}

.profile-tabs {
  background: white;
  border-radius: 8px;
}

.profile-form {
  padding: 20px 10px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
  margin-top: 10px;
}

.security-section {
  padding: 10px 0;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 16px;
  transition: all 0.3s;
}

.security-item:hover {
  background: #ecf5ff;
}

.security-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.security-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: #ecf5ff;
  color: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.security-icon.warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.security-icon.success {
  background: #f0f9eb;
  color: #67c23a;
}

.security-content h4 {
  margin: 0 0 4px 0;
  font-size: 15px;
  color: #303133;
}

.security-content p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.preferences-form {
  padding: 20px 10px;
}

.form-desc {
  margin-left: 10px;
  font-size: 13px;
  color: #909399;
}

.password-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
}

@media (max-width: 768px) {
  .page-title {
    font-size: 18px;
    margin-bottom: 16px;
  }

  .profile-header {
    padding: 20px;
    flex-direction: column;
    align-items: flex-start;
  }

  .avatar-section {
    width: 100%;
  }

  .user-name {
    font-size: 20px;
  }

  .stats-section {
    width: 100%;
    justify-content: space-between;
    gap: 0;
  }

  .stat-value {
    font-size: 20px;
  }

  .security-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .security-item .el-button,
  .security-item .el-tag {
    align-self: flex-end;
  }

  .profile-form :deep(.el-form-item__label) {
    width: 80px !important;
  }
}

@media (max-width: 480px) {
  .profile-header {
    padding: 16px;
  }

  .avatar-section {
    flex-direction: column;
    text-align: center;
    width: 100%;
  }

  .stats-section {
    flex-direction: column;
    gap: 12px;
  }

  .stat-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  }

  .stat-item:last-child {
    border-bottom: none;
  }
}
</style>
