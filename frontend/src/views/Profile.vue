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
            <el-divider content-position="left">
              <span class="divider-title">
                <el-icon><Brush /></el-icon>
                主题设置
              </span>
            </el-divider>

            <div class="theme-section">
              <div class="section-label">选择主题模式</div>
              <div class="theme-mode-cards">
                <div
                  v-for="mode in themeModes"
                  :key="mode.value"
                  class="theme-mode-card"
                  :class="{ active: themeMode === mode.value }"
                  @click="selectThemeMode(mode.value)"
                >
                  <div class="mode-icon">
                    <el-icon :size="28"><component :is="mode.icon" /></el-icon>
                  </div>
                  <div class="mode-info">
                    <div class="mode-name">{{ mode.label }}</div>
                    <div class="mode-desc">{{ mode.desc }}</div>
                  </div>
                  <div class="mode-check" v-if="themeMode === mode.value">
                    <el-icon :size="20" color="#409eff"><CircleCheckFilled /></el-icon>
                  </div>
                </div>
              </div>
            </div>

            <div class="theme-section">
              <div class="section-label">主题预览</div>
              <div class="theme-preview-container">
                <div class="preview-device">
                  <div class="preview-header">
                    <div class="preview-dots">
                      <span class="dot dot-red"></span>
                      <span class="dot dot-yellow"></span>
                      <span class="dot dot-green"></span>
                    </div>
                    <div class="preview-title">预览效果</div>
                  </div>
                  <div class="preview-body" :class="'preview-' + effectiveTheme">
                    <div class="preview-top-bar"></div>
                    <div class="preview-layout">
                      <div class="preview-sidebar"></div>
                      <div class="preview-content">
                        <div class="preview-card card-1"></div>
                        <div class="preview-card card-2"></div>
                        <div class="preview-card card-3"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="theme-section">
              <div class="section-header">
                <div class="section-label">自定义主题色</div>
                <el-switch
                  v-model="customThemeEnabled"
                  size="small"
                  active-text="开启"
                  inactive-text="关闭"
                />
              </div>
              <div class="custom-theme-editor" v-show="customThemeEnabled">
                <el-row :gutter="20">
                  <el-col :xs="24" :sm="12" :md="8">
                    <div class="color-picker-item">
                      <label>主色调</label>
                      <el-color-picker
                        v-model="localCustomTheme.primaryColor"
                        show-alpha
                        size="large"
                        @change="handleCustomColorChange"
                      />
                    </div>
                  </el-col>
                  <el-col :xs="24" :sm="12" :md="8">
                    <div class="color-picker-item">
                      <label>顶部渐变起点</label>
                      <el-color-picker
                        v-model="localCustomTheme.headerStart"
                        show-alpha
                        size="large"
                        @change="handleCustomColorChange"
                      />
                    </div>
                  </el-col>
                  <el-col :xs="24" :sm="12" :md="8">
                    <div class="color-picker-item">
                      <label>顶部渐变终点</label>
                      <el-color-picker
                        v-model="localCustomTheme.headerEnd"
                        show-alpha
                        size="large"
                        @change="handleCustomColorChange"
                      />
                    </div>
                  </el-col>
                </el-row>
                <el-row :gutter="20" style="margin-top: 16px">
                  <el-col :xs="24" :sm="12" :md="8">
                    <div class="color-picker-item">
                      <label>侧边栏背景</label>
                      <el-color-picker
                        v-model="localCustomTheme.sidebarBg"
                        show-alpha
                        size="large"
                        @change="handleCustomColorChange"
                      />
                    </div>
                  </el-col>
                  <el-col :xs="24" :sm="12" :md="8">
                    <div class="color-picker-item">
                      <label>侧边栏激活色</label>
                      <el-color-picker
                        v-model="localCustomTheme.sidebarActive"
                        show-alpha
                        size="large"
                        @change="handleCustomColorChange"
                      />
                    </div>
                  </el-col>
                </el-row>
                <div class="preset-themes">
                  <div class="preset-label">推荐配色方案</div>
                  <div class="preset-list">
                    <div
                      v-for="preset in presetThemes"
                      :key="preset.name"
                      class="preset-item"
                      :style="{ background: preset.gradient }"
                      @click="applyPresetTheme(preset)"
                      :title="preset.name"
                    >
                      <span class="preset-name">{{ preset.name }}</span>
                    </div>
                  </div>
                </div>
                <div class="custom-actions">
                  <el-button size="small" @click="resetCustomTheme">恢复默认</el-button>
                  <el-button type="primary" size="small" @click="applyCustomTheme">
                    应用自定义主题
                  </el-button>
                </div>
              </div>
            </div>

            <el-divider content-position="left">通用设置</el-divider>

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
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  UserFilled, Edit, Lock, Warning, CircleCheck,
  Sunny, Moon, Monitor, Brush, CircleCheckFilled
} from '@element-plus/icons-vue'
import { authApi, userApi, archiveApi, todoApi } from '@/api'
import { useTheme } from '@/composables/useTheme'

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

const { themeMode, isDark, customTheme, customEnabled, setThemeMode, setCustomTheme, enableCustomTheme, resetCustomTheme: resetThemeToDefault, THEME_MODES } = useTheme()

const customThemeEnabled = ref(customEnabled.value)

const themeModes = [
  { value: THEME_MODES.LIGHT, label: '浅色主题', desc: '明亮清爽，适合日间使用', icon: Sunny },
  { value: THEME_MODES.DARK, label: '深色主题', desc: '护眼省电，适合夜间使用', icon: Moon },
  { value: THEME_MODES.AUTO, label: '跟随系统', desc: '根据系统设置自动切换', icon: Monitor }
]

const effectiveTheme = computed(() => {
  if (themeMode.value === THEME_MODES.AUTO) {
    return isDark.value ? 'dark' : 'light'
  }
  return themeMode.value
})

const localCustomTheme = reactive({
  primaryColor: '#409eff',
  headerStart: '#667eea',
  headerEnd: '#764ba2',
  sidebarBg: '#545c64',
  sidebarActive: '#ffd04b'
})

const presetThemes = [
  {
    name: '经典紫',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    primaryColor: '#667eea',
    headerStart: '#667eea',
    headerEnd: '#764ba2',
    sidebarBg: '#545c64',
    sidebarActive: '#ffd04b'
  },
  {
    name: '海洋蓝',
    gradient: 'linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%)',
    primaryColor: '#2193b0',
    headerStart: '#2193b0',
    headerEnd: '#6dd5ed',
    sidebarBg: '#2c3e50',
    sidebarActive: '#6dd5ed'
  },
  {
    name: '森林绿',
    gradient: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
    primaryColor: '#11998e',
    headerStart: '#11998e',
    headerEnd: '#38ef7d',
    sidebarBg: '#2d4a3e',
    sidebarActive: '#38ef7d'
  },
  {
    name: '落日橙',
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    primaryColor: '#f5576c',
    headerStart: '#f093fb',
    headerEnd: '#f5576c',
    sidebarBg: '#4a3f55',
    sidebarActive: '#ffd93d'
  },
  {
    name: '深空灰',
    gradient: 'linear-gradient(135deg, #232526 0%, #414345 100%)',
    primaryColor: '#606266',
    headerStart: '#232526',
    headerEnd: '#414345',
    sidebarBg: '#1a1a1a',
    sidebarActive: '#c0c4cc'
  },
  {
    name: '玫瑰金',
    gradient: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
    primaryColor: '#ff9a9e',
    headerStart: '#ff9a9e',
    headerEnd: '#fecfef',
    sidebarBg: '#5c4a52',
    sidebarActive: '#ffecd2'
  }
]

const selectThemeMode = (mode) => {
  setThemeMode(mode)
  preferencesForm.theme = mode
}

const handleCustomColorChange = () => {
}

const applyPresetTheme = (preset) => {
  localCustomTheme.primaryColor = preset.primaryColor
  localCustomTheme.headerStart = preset.headerStart
  localCustomTheme.headerEnd = preset.headerEnd
  localCustomTheme.sidebarBg = preset.sidebarBg
  localCustomTheme.sidebarActive = preset.sidebarActive
  applyCustomTheme()
}

const applyCustomTheme = () => {
  setCustomTheme(localCustomTheme)
  enableCustomTheme(true)
  customThemeEnabled.value = true
  ElMessage.success('自定义主题已应用')
}

const resetCustomTheme = () => {
  resetThemeToDefault()
  customThemeEnabled.value = false
  localCustomTheme.primaryColor = customTheme.value.primaryColor
  localCustomTheme.headerStart = customTheme.value.headerStart
  localCustomTheme.headerEnd = customTheme.value.headerEnd
  localCustomTheme.sidebarBg = customTheme.value.sidebarBg
  localCustomTheme.sidebarActive = customTheme.value.sidebarActive
  ElMessage.success('已恢复默认主题色')
}

watch(customThemeEnabled, (enabled) => {
  enableCustomTheme(enabled)
})

if (customEnabled.value) {
  localCustomTheme.primaryColor = customTheme.value.primaryColor
  localCustomTheme.headerStart = customTheme.value.headerStart
  localCustomTheme.headerEnd = customTheme.value.headerEnd
  localCustomTheme.sidebarBg = customTheme.value.sidebarBg
  localCustomTheme.sidebarActive = customTheme.value.sidebarActive
}

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
      const savedTheme = localStorage.getItem('app_theme_mode')
      if (!savedTheme && res.data.preferences.theme) {
        setThemeMode(res.data.preferences.theme)
      }
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
    preferencesForm.theme = themeMode.value
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
  background: var(--gradient-primary);
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 20px;
  color: var(--header-text);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  transition: background 0.3s ease, color 0.3s ease;
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

.divider-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.theme-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.section-header .section-label {
  margin-bottom: 0;
}

.theme-mode-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.theme-mode-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 2px solid var(--border-primary);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--bg-card);
  position: relative;
}

.theme-mode-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.theme-mode-card.active {
  border-color: var(--primary-color);
  background: var(--primary-light);
}

.mode-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--text-primary);
}

.theme-mode-card.active .mode-icon {
  background: var(--primary-color);
  color: white;
}

.mode-info {
  flex: 1;
  min-width: 0;
}

.mode-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.mode-desc {
  font-size: 12px;
  color: var(--text-tertiary);
}

.mode-check {
  position: absolute;
  top: 8px;
  right: 8px;
}

.theme-preview-container {
  display: flex;
  justify-content: center;
  padding: 10px 0;
}

.preview-device {
  width: 100%;
  max-width: 480px;
  border: 1px solid var(--border-primary);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

.preview-header {
  background: var(--bg-tertiary);
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid var(--border-primary);
}

.preview-dots {
  display: flex;
  gap: 6px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot-red { background: #ff5f57; }
.dot-yellow { background: #febc2e; }
.dot-green { background: #28c840; }

.preview-title {
  font-size: 12px;
  color: var(--text-tertiary);
}

.preview-body {
  height: 200px;
  transition: background-color 0.3s ease;
}

.preview-light {
  background-color: #f5f7fa;
}

.preview-dark {
  background-color: #1a1a1a;
}

.preview-top-bar {
  height: 32px;
  background: linear-gradient(135deg, var(--header-bg-start, #667eea) 0%, var(--header-bg-end, #764ba2) 100%);
}

.preview-layout {
  display: flex;
  height: calc(100% - 32px);
}

.preview-sidebar {
  width: 60px;
  background-color: var(--sidebar-bg, #545c64);
  flex-shrink: 0;
}

.preview-content {
  flex: 1;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-card {
  height: 24px;
  border-radius: 4px;
  background: var(--bg-card, #fff);
}

.preview-light .preview-card {
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.preview-dark .preview-card {
  background: #2a2a2a;
}

.card-1 { width: 70%; }
.card-2 { width: 85%; }
.card-3 { width: 60%; }

.custom-theme-editor {
  background: var(--bg-tertiary);
  border-radius: 10px;
  padding: 20px;
  margin-top: 8px;
}

.color-picker-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 8px;
}

.color-picker-item label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.preset-themes {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border-secondary);
}

.preset-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 10px;
  font-weight: 500;
}

.preset-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
}

.preset-item {
  height: 48px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  position: relative;
  overflow: hidden;
}

.preset-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.preset-name {
  color: white;
  font-size: 12px;
  font-weight: 500;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  z-index: 1;
}

.custom-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border-secondary);
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
