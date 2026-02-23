<template>
  <header class="app-header">
    <div class="container">
      <div class="logo" @click="$router.push('/')">
        <span class="logo-icon">🎵</span>
        <span class="logo-text">BeatMarket</span>
      </div>

      <nav :class="['nav-menu', { 'active': menuOpen }]">
        <router-link to="/" exact-active-class="active">Главная</router-link>
        <router-link to="/search" active-class="active">Поиск</router-link>
        <router-link to="/trends" active-class="active">Тренды</router-link>
        <router-link to="/about" active-class="active">О нас</router-link>
        <router-link to="/contacts" active-class="active">Контакты</router-link>
      </nav>

      <div class="user-actions">
        <router-link to="/cart" class="cart-icon">
          <i class="fas fa-shopping-cart"></i>
          <span v-if="cartCount > 0" class="badge">{{ cartCount }}</span>
        </router-link>
        <router-link to="/profile" class="profile-icon">
          <i class="fas fa-user-circle"></i>
        </router-link>
        <button class="menu-toggle" @click="menuOpen = !menuOpen" v-if="isMobile">
          <i :class="menuOpen ? 'fas fa-times' : 'fas fa-bars'"></i>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const menuOpen = ref(false);
const isMobile = ref(window.innerWidth <= 768);
const cartCount = ref(2); // пример, позже можно получать из стора

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768;
  if (!isMobile.value) menuOpen.value = false;
};

onMounted(() => {
  window.addEventListener('resize', checkMobile);
});

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile);
});
</script>

<style scoped>
.app-header {
  background: rgba(10, 10, 15, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(168, 85, 247, 0.2);
  position: sticky;
  top: 0;
  z-index: 1000;
  padding: 0.8rem 2rem;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 1.5rem;
  font-weight: 700;
}

.logo-icon {
  font-size: 2rem;
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.logo-text {
  background: linear-gradient(45deg, #fff, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-menu {
  display: flex;
  gap: 2rem;
}

.nav-menu a {
  color: #a0a0b0;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
  position: relative;
  padding: 0.5rem 0;
}

.nav-menu a:hover,
.nav-menu a.active {
  color: #fff;
}

.nav-menu a::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  transition: width 0.2s;
}

.nav-menu a:hover::after,
.nav-menu a.active::after {
  width: 100%;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 1.2rem;
}

.cart-icon, .profile-icon {
  color: #a0a0b0;
  font-size: 1.3rem;
  position: relative;
  transition: color 0.2s;
}

.cart-icon:hover, .profile-icon:hover {
  color: #a855f7;
}

.badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #a855f7;
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

.menu-toggle {
  display: none;
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
}

@media (max-width: 768px) {
  .app-header { padding: 0.8rem 1rem; }
  .menu-toggle { display: block; }
  .nav-menu {
    position: fixed;
    top: 70px;
    left: 0;
    width: 100%;
    background: rgba(10, 10, 15, 0.95);
    backdrop-filter: blur(10px);
    flex-direction: column;
    align-items: center;
    padding: 2rem;
    gap: 1.5rem;
    transform: translateY(-150%);
    transition: transform 0.3s;
    border-bottom: 1px solid rgba(168, 85, 247, 0.2);
  }
  .nav-menu.active {
    transform: translateY(0);
  }
}
</style>