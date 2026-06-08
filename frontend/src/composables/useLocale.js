import { ref, computed } from 'vue'
import zhCN from '@/locales/zh-CN'
import en from '@/locales/en'
import ja from '@/locales/ja'

const STORAGE_KEY = 'app_locale'

export const LANGUAGES = {
  ZH_CN: 'zh-CN',
  EN: 'en',
  JA: 'ja'
}

export const LANGUAGE_LIST = [
  { value: LANGUAGES.ZH_CN, label: '简体中文', nativeName: '简体中文', flag: '🇨🇳' },
  { value: LANGUAGES.EN, label: 'English', nativeName: 'English', flag: '🇺🇸' },
  { value: LANGUAGES.JA, label: '日本語', nativeName: '日本語', flag: '🇯🇵' }
]

const messages = {
  'zh-CN': zhCN,
  'en': en,
  'ja': ja
}

let localeRef = null
let initialized = false

const getBrowserLocale = () => {
  if (typeof navigator === 'undefined') return LANGUAGES.ZH_CN
  const lang = navigator.language || navigator.userLanguage || LANGUAGES.ZH_CN
  if (lang.startsWith('zh')) return LANGUAGES.ZH_CN
  if (lang.startsWith('ja')) return LANGUAGES.JA
  if (lang.startsWith('en')) return LANGUAGES.EN
  return LANGUAGES.ZH_CN
}

const getNestedValue = (obj, path) => {
  if (!path) return undefined
  const keys = path.split('.')
  let result = obj
  for (const key of keys) {
    if (result == null) return undefined
    result = result[key]
  }
  return result
}

const formatMessage = (message, params) => {
  if (!message || !params) return message
  return message.replace(/\{(\w+)\}/g, (match, key) => {
    return params[key] !== undefined ? params[key] : match
  })
}

const applyHtmlLang = (locale) => {
  if (typeof document !== 'undefined' && document.documentElement) {
    document.documentElement.setAttribute('lang', locale)
  }
}

export const useLocale = () => {
  if (!initialized) {
    initialized = true
    let savedLocale = null
    
    if (typeof localStorage !== 'undefined') {
      savedLocale = localStorage.getItem(STORAGE_KEY)
    }

    const initialLocale = savedLocale && messages[savedLocale] 
      ? savedLocale 
      : getBrowserLocale()

    localeRef = ref(initialLocale)
    applyHtmlLang(initialLocale)
  }

  const locale = computed(() => localeRef.value)

  const currentLanguage = computed(() => {
    return LANGUAGE_LIST.find(l => l.value === localeRef.value) || LANGUAGE_LIST[0]
  })

  const setLocale = (newLocale) => {
    if (!messages[newLocale]) {
      console.warn(`Locale "${newLocale}" not found, falling back to default`)
      newLocale = LANGUAGES.ZH_CN
    }
    localeRef.value = newLocale
    applyHtmlLang(newLocale)
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, newLocale)
    }
  }

  const t = (key, params) => {
    const localeValue = localeRef.value
    const localeMessages = messages[localeValue] || messages[LANGUAGES.ZH_CN]
    const message = getNestedValue(localeMessages, key)
    
    if (message === undefined) {
      const fallbackMessages = messages[LANGUAGES.ZH_CN]
      const fallbackMessage = getNestedValue(fallbackMessages, key)
      if (fallbackMessage !== undefined) {
        return formatMessage(fallbackMessage, params)
      }
      return key
    }
    
    return formatMessage(message, params)
  }

  const switchLanguage = async (newLocale) => {
    if (!messages[newLocale]) {
      return false
    }
    setLocale(newLocale)
    return true
  }

  const resetLocale = () => {
    const browserLocale = getBrowserLocale()
    setLocale(browserLocale)
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem(STORAGE_KEY)
    }
  }

  return {
    locale,
    currentLanguage,
    setLocale,
    t,
    switchLanguage,
    resetLocale,
    LANGUAGES,
    LANGUAGE_LIST
  }
}

export const initLocaleBeforeMount = () => {
  if (typeof document === 'undefined') return
  try {
    let savedLocale = localStorage.getItem(STORAGE_KEY)
    if (!savedLocale || !messages[savedLocale]) {
      savedLocale = getBrowserLocale()
    }
    applyHtmlLang(savedLocale)
  } catch (e) {
    console.warn('Locale init failed:', e)
  }
}

export const createI18n = () => {
  const { t, locale, setLocale } = useLocale()
  return {
    t,
    locale,
    setLocale,
    install(app) {
      app.config.globalProperties.$t = t
      app.config.globalProperties.$locale = locale
      app.provide('i18n', { t, locale, setLocale })
    }
  }
}
