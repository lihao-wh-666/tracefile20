import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('@/views/Categories.vue')
  },
  {
    path: '/archives',
    name: 'Archives',
    component: () => import('@/views/Archives.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
