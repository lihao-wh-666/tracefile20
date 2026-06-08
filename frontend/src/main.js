import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import './styles/responsive.css'
import './styles/theme.css'
import { useTheme } from './composables/useTheme'
import { useLocale } from './composables/useLocale'

const app = createApp(App)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

const { t, locale, setLocale } = useLocale()

app.config.globalProperties.$t = t
app.config.globalProperties.$locale = locale
app.config.globalProperties.$setLocale = setLocale

app.provide('i18n', { t, locale, setLocale })

app.use(ElementPlus)
app.use(router)

useTheme()

app.mount('#app')
