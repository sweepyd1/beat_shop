import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Search from '../views/Search.vue'
import Artist from '../views/Artist.vue'
import Collection from '../views/Collection.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home
  },
  {
    path: '/search',
    name: 'search',
    component: Search
  },
  {
    path: '/artist/:id',
    name: 'artist',
    component: Artist
  },
  {
    path: '/collection/:id',
    name: 'collection',
    component: Collection
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router