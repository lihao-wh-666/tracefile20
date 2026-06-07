import { ref, computed, watch } from 'vue'

const STORAGE_KEY_MODE = 'app_theme_mode'
const STORAGE_KEY_CUSTOM = 'app_custom_theme'
const STORAGE_KEY_CUSTOM_ENABLED = 'app_custom_theme_enabled'

export const THEME_MODES = {
  LIGHT: 'light',
  DARK: 'dark',
  AUTO: 'auto'
}

const defaultCustomTheme = {
  primaryColor: '#409eff',
  headerStart: '#667eea',
  headerEnd: '#764ba2',
  sidebarBg: '#545c64',
  sidebarActive: '#ffd04b'
}

let themeModeRef = null
let customThemeRef = null
let customEnabledRef = null
let systemDarkMedia = null
let initialized = false

const getSystemDark = () => {
  if (typeof window === 'undefined' || !window.matchMedia) return false
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

const applyThemeClass = (isDark) => {
  const html = document.documentElement
  html.classList.add('theme-transition')
  html.classList.remove('theme-light', 'theme-dark')
  html.classList.add(isDark ? 'theme-dark' : 'theme-light')
  requestAnimationFrame(() => {
    setTimeout(() => {
      html.classList.remove('theme-transition')
    }, 300)
  })
}

const applyCustomVariables = (custom) => {
  if (!custom) return
  const root = document.documentElement.style
  if (custom.primaryColor) {
    root.setProperty('--primary-color', custom.primaryColor)
  }
  if (custom.headerStart && custom.headerEnd) {
    root.setProperty('--header-bg-start', custom.headerStart)
    root.setProperty('--header-bg-end', custom.headerEnd)
    root.setProperty('--gradient-primary', `linear-gradient(135deg, ${custom.headerStart} 0%, ${custom.headerEnd} 100%)`)
  }
  if (custom.sidebarBg) {
    root.setProperty('--sidebar-bg', custom.sidebarBg)
  }
  if (custom.sidebarActive) {
    root.setProperty('--sidebar-active-text', custom.sidebarActive)
  }
}

const clearCustomVariables = () => {
  const root = document.documentElement.style
  root.removeProperty('--primary-color')
  root.removeProperty('--header-bg-start')
  root.removeProperty('--header-bg-end')
  root.removeProperty('--gradient-primary')
  root.removeProperty('--sidebar-bg')
  root.removeProperty('--sidebar-active-text')
}

export const useTheme = () => {
  if (!initialized) {
    initialized = true
    themeModeRef = ref(THEME_MODES.LIGHT)
    customThemeRef = ref({ ...defaultCustomTheme })
    customEnabledRef = ref(false)

    const savedMode = localStorage.getItem(STORAGE_KEY_MODE)
    if (savedMode && Object.values(THEME_MODES).includes(savedMode)) {
      themeModeRef.value = savedMode
    }

    const savedEnabled = localStorage.getItem(STORAGE_KEY_CUSTOM_ENABLED)
    customEnabledRef.value = savedEnabled === 'true'

    try {
      const savedCustom = localStorage.getItem(STORAGE_KEY_CUSTOM)
      if (savedCustom) {
        customThemeRef.value = { ...defaultCustomTheme, ...JSON.parse(savedCustom) }
      }
    } catch (e) {
      console.warn('Failed to parse custom theme:', e)
    }

    const isDark = computed(() => {
      if (themeModeRef.value === THEME_MODES.AUTO) {
        return getSystemDark()
      }
      return themeModeRef.value === THEME_MODES.DARK
    })

    applyThemeClass(isDark.value)
    if (customEnabledRef.value) {
      applyCustomVariables(customThemeRef.value)
    }

    watch(isDark, (newIsDark) => {
      applyThemeClass(newIsDark)
    })

    watch(customThemeRef, (newCustom) => {
      if (customEnabledRef.value) {
        applyCustomVariables(newCustom)
      }
      localStorage.setItem(STORAGE_KEY_CUSTOM, JSON.stringify(newCustom))
    }, { deep: true })

    watch(customEnabledRef, (enabled) => {
      localStorage.setItem(STORAGE_KEY_CUSTOM_ENABLED, String(enabled))
      if (enabled) {
        applyCustomVariables(customThemeRef.value)
      } else {
        clearCustomVariables()
      }
    })

    if (typeof window !== 'undefined' && window.matchMedia) {
      systemDarkMedia = window.matchMedia('(prefers-color-scheme: dark)')
      const handleSystemChange = () => {
        if (themeModeRef.value === THEME_MODES.AUTO) {
          applyThemeClass(getSystemDark())
        }
      }
      if (systemDarkMedia.addEventListener) {
        systemDarkMedia.addEventListener('change', handleSystemChange)
      } else if (systemDarkMedia.addListener) {
        systemDarkMedia.addListener(handleSystemChange)
      }
    }
  }

  const isDark = computed(() => {
    if (themeModeRef.value === THEME_MODES.AUTO) {
      return getSystemDark()
    }
    return themeModeRef.value === THEME_MODES.DARK
  })

  const themeMode = computed(() => themeModeRef.value)
  const customTheme = computed(() => customThemeRef.value)
  const customEnabled = computed(() => customEnabledRef.value)

  const setThemeMode = (mode) => {
    if (!Object.values(THEME_MODES).includes(mode)) return
    themeModeRef.value = mode
    localStorage.setItem(STORAGE_KEY_MODE, mode)
  }

  const setCustomTheme = (custom) => {
    customThemeRef.value = { ...customThemeRef.value, ...custom }
  }

  const enableCustomTheme = (enabled) => {
    customEnabledRef.value = enabled
  }

  const resetCustomTheme = () => {
    customThemeRef.value = { ...defaultCustomTheme }
    customEnabledRef.value = false
    localStorage.removeItem(STORAGE_KEY_CUSTOM)
    localStorage.removeItem(STORAGE_KEY_CUSTOM_ENABLED)
    clearCustomVariables()
  }

  const toggleTheme = () => {
    if (themeModeRef.value === THEME_MODES.LIGHT) {
      setThemeMode(THEME_MODES.DARK)
    } else {
      setThemeMode(THEME_MODES.LIGHT)
    }
  }

  return {
    themeMode,
    isDark,
    customTheme,
    customEnabled,
    setThemeMode,
    setCustomTheme,
    enableCustomTheme,
    resetCustomTheme,
    toggleTheme,
    THEME_MODES
  }
}

export const initThemeBeforeMount = () => {
  if (typeof document === 'undefined') return
  try {
    const savedMode = localStorage.getItem(STORAGE_KEY_MODE) || THEME_MODES.LIGHT
    let isDark = false
    if (savedMode === THEME_MODES.DARK) {
      isDark = true
    } else if (savedMode === THEME_MODES.AUTO) {
      isDark = getSystemDark()
    }
    const html = document.documentElement
    html.classList.remove('theme-light', 'theme-dark')
    html.classList.add(isDark ? 'theme-dark' : 'theme-light')
  } catch (e) {
    console.warn('Theme init failed:', e)
  }
}
