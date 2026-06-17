<template>
  <div>
    <header class="app-header">
      <div class="container">
        <div class="logo" @click="$router.push('/')">
          <span class="logo-icon">🎵</span>
          <span class="logo-text">BeatMarket</span>
        </div>

        <nav :class="['nav-menu', { active: menuOpen }]">
          <router-link to="/" exact-active-class="active">Главная</router-link>
          <router-link to="/search" active-class="active">Поиск</router-link>
          <router-link to="/trends" active-class="active">Тренды</router-link>
          <router-link to="/about" active-class="active">О нас</router-link>
          <router-link to="/contacts" active-class="active"
            >Контакты</router-link
          >
          <router-link to="/profile" active-class="active">Профиль</router-link>

          <template v-if="isAdmin">
            <router-link to="/admin" class="admin-link">
              <i class="fas fa-crown"></i> Админ панель
            </router-link>
          </template>
        </nav>

        <div class="user-actions">
          <template v-if="user">
            <button
              class="ai-recommend-btn"
              @click="openRecommendationModal"
              title="AI рекомендации"
            >
              🤖
            </button>
            <div class="profile-link" @click.stop="toggleDropdown">
              <div class="avatar-wrapper">
                <div class="avatar-circle">
                  <img
                    v-if="avatarUrl"
                    :src="avatarUrl"
                    :alt="user.name || 'Avatar'"
                    @error="onAvatarError"
                  />
                  <span v-else>{{ userInitial }}</span>
                </div>
                <div class="dropdown-menu" :class="{ active: isDropdownOpen }">
                  <router-link to="/profile" class="dropdown-item">
                    <i class="fas fa-user"></i> Профиль
                  </router-link>
                  <button
                    @click="handleLogout"
                    class="dropdown-item logout-btn"
                  >
                    <i class="fas fa-sign-out-alt"></i> Выйти
                  </button>
                </div>
              </div>
            </div>
          </template>

          <template v-else>
            <router-link to="/login" class="btn-login">Войти</router-link>
            <router-link to="/register" class="btn-register"
              >Регистрация</router-link
            >
          </template>

          <button
            class="menu-toggle"
            @click="menuOpen = !menuOpen"
            v-if="isMobile"
          >
            <i :class="menuOpen ? 'fas fa-times' : 'fas fa-bars'"></i>
          </button>
        </div>
      </div>
    </header>
    <RecommendationModal
      :visible="showRecommendationModal"
      @close="showRecommendationModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import { storeToRefs } from "pinia";
import { useRouter } from "vue-router";
import RecommendationModal from "@/components/RecommendationModal.vue";


const showRecommendationModal = ref(false);
const openRecommendationModal = () => {
  showRecommendationModal.value = true;
};


const menuOpen = ref(false);
const isMobile = ref(window.innerWidth <= 768);


const isDropdownOpen = ref(false);


const authStore = useAuthStore();
const { user } = storeToRefs(authStore);
const router = useRouter();


const avatarUrl = computed(() => {
  if (!user.value?.avatar_url) return "default-avatar.png"; 
  if (user.value.avatar_url.startsWith("http")) return user.value.avatar_url;
  const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
  return `${baseUrl}${user.value.avatar_url}`;
});

const onAvatarError = (event) => {
  
  event.target.style.display = "none";
};

const userInitial = computed(() => {
  if (!user.value) return "?";
  return user.value.name ? user.value.name.charAt(0).toUpperCase() : "U";
});


const isAdmin = computed(() => user.value && user.value.role === "admin");


const handleLogout = async () => {
  await authStore.logout();
  router.push("/login");
};


const toggleDropdown = (event) => {
  if (isMobile.value) {
    isDropdownOpen.value = !isDropdownOpen.value;
  }
};

const closeDropdown = () => {
  if (isMobile.value) {
    isDropdownOpen.value = false;
  }
};

const handleClickOutside = (event) => {
  const profileLink = document.querySelector(".profile-link");
  if (profileLink && !profileLink.contains(event.target)) {
    closeDropdown();
  }
};


const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768;
  if (!isMobile.value) {
    menuOpen.value = false;
    closeDropdown(); 
  }
};


onMounted(() => {
  window.addEventListener("resize", checkMobile);
  document.addEventListener("click", handleClickOutside);
});

onUnmounted(() => {
  window.removeEventListener("resize", checkMobile);
  document.removeEventListener("click", handleClickOutside);
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
  content: "";
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


.btn-login,
.btn-register {
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1.2rem;
  border-radius: 30px;
  transition: all 0.2s;
  font-size: 0.95rem;
}

.btn-login {
  background: transparent;
  border: 1px solid #a855f7;
  color: #fff;
}

.btn-login:hover {
  background: rgba(168, 85, 247, 0.1);
  border-color: #c084fc;
}

.btn-register {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border: none;
  color: #fff;
  box-shadow: 0 2px 8px rgba(168, 85, 247, 0.3);
}

.btn-register:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(168, 85, 247, 0.5);
}


.avatar-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 1rem;
  transition: transform 0.2s;
  overflow: hidden;
}

.avatar-circle:hover {
  transform: scale(1.05);
}

.avatar-circle img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-wrapper {
  position: relative;
  cursor: pointer;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: rgba(20, 20, 30, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(168, 85, 247, 0.3);
  border-radius: 12px;
  padding: 0.5rem 0;
  min-width: 160px;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}


@media (min-width: 769px) {
  .avatar-wrapper:hover .dropdown-menu {
    opacity: 1;
    visibility: visible;
  }
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 1rem;
  color: #e0e0e0;
  text-decoration: none;
  font-size: 0.9rem;
  transition: background 0.2s;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  cursor: pointer;
}

.dropdown-item i {
  width: 18px;
  font-size: 0.9rem;
}

.dropdown-item:hover {
  background: rgba(168, 85, 247, 0.2);
  color: white;
}

.logout-btn {
  color: #ff6b6b;
}

.logout-btn:hover {
  background: rgba(255, 107, 107, 0.2);
  color: #ff8e8e;
}


.ai-recommend-btn {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border: none;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  font-size: 1.3rem;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.ai-recommend-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 0 12px rgba(168, 85, 247, 0.6);
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
  .app-header {
    padding: 0.8rem 1rem;
  }

  .menu-toggle {
    display: block;
  }

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
    z-index: 999;
  }

  .nav-menu.active {
    transform: translateY(0);
  }

  .user-actions {
    gap: 0.8rem;
  }

  .btn-login,
  .btn-register {
    padding: 0.4rem 1rem;
    font-size: 0.85rem;
  }

  .avatar-circle {
    width: 32px;
    height: 32px;
    font-size: 0.9rem;
  }

  
  .avatar-wrapper:hover .dropdown-menu {
    opacity: 0;
    visibility: hidden;
  }

  
  .dropdown-menu.active {
    opacity: 1;
    visibility: visible;
  }

  
  .dropdown-menu {
    min-width: 170px;
    right: 0;
    left: auto;
  }

  .dropdown-item {
    padding: 0.75rem 1rem;
    font-size: 1rem;
  }
}
</style>
