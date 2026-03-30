import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Search from '../views/Search.vue'
import Collection from '../views/Collection.vue'
import Artist from '../views/Artist.vue'
import Cart from '../views/Cart.vue'
import Checkout from '../views/Checkout.vue'
import Profile from '../views/Profile.vue'
import Trends from '../views/Trends.vue'
import About from '../views/About.vue'
import Contacts from '../views/Contacts.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import TrackDetail from '../views/TrackDetail.vue'; // новый импорт
const routes = [
  { path: '/', component: Home },
  { path: '/search', component: Search },
  { path: '/collection/:id', component: Collection },
  { path: '/artist/:id', component: Artist },

  { path: '/cart', component: Cart },
  { path: '/checkout', component: Checkout },
  { path: '/profile', component: Profile },
  { path: '/trends', component: Trends },
  { path: '/about', component: About },
  { path: '/contacts', component: Contacts },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  {path: '/admin/tracks',name: 'AdminTracks',
  component: () => import('@/views/AdminTracks.vue'),
  meta: { requiresAuth: true, role: 'admin' }
},
 { path: '/track/:id', component: TrackDetail, name: 'track' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router