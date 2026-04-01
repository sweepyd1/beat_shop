<template>
  <div class="app">
    <Header />
    <main class="main-content">
      <router-view />
    </main>

    <!-- Глобальный плеер всегда здесь, но он сам решит, показываться или нет -->
    <Player />
  </div>
</template>

<script setup>
import { ref, provide } from "vue";
import Player from "./components/Player.vue";
import Header from "./components/Header.vue";
import { usePlayer } from '@/composables/usePlayer';

// Инициализация плеера (один раз для всего приложения)
usePlayer();

// Глобальное состояние плеера
const currentTrack = ref(null);
const isPlaying = ref(false);
const playlist = ref([]);
const currentIndex = ref(0);

// Функция для воспроизведения трека
const playTrack = (track) => {
  console.log("playTrack called", track);
  currentTrack.value = track;
  isPlaying.value = true;
};

// Функция для добавления в плейлист
const addToPlaylist = (track) => {
  playlist.value.push(track);
};

// Функции для управления плеером
const nextTrack = () => {
  if (playlist.value.length > 0 && currentIndex.value < playlist.value.length - 1) {
    currentIndex.value++;
    currentTrack.value = playlist.value[currentIndex.value];
  }
};

const prevTrack = () => {
  if (playlist.value.length > 0 && currentIndex.value > 0) {
    currentIndex.value--;
    currentTrack.value = playlist.value[currentIndex.value];
  }
};

provide("player", {
  currentTrack,
  isPlaying,
  playlist,
  currentIndex,
  playTrack,
  addToPlaylist,
  nextTrack,
  prevTrack,
});
</script>
<style>
/* Глобальные стили */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, sans-serif;
  background: #0b0b0f;
  color: #fff;
  overflow-x: hidden;
}

/* Стили для скроллбара */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Анимации */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #0b0b0f 0%, #1a1a24 100%);
}

/* Навбар */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: rgba(10, 10, 15, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
  height: 70px;
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  cursor: pointer;
}

.nav-links {
  display: flex;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.03);
  padding: 0.25rem;
  border-radius: 12px;
}

.nav-links a {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  color: #a0a0b0;
  text-decoration: none;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.2s;
}

.nav-links a i {
  font-size: 1.1rem;
}

.nav-links a:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
}

.nav-links a.active {
  color: #fff;
  background: rgba(168, 85, 247, 0.15);
}

.nav-links a.active i {
  color: #a855f7;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.user-menu i {
  font-size: 1.3rem;
  color: #a0a0b0;
  cursor: pointer;
  transition: color 0.2s;
}

.user-menu i:hover {
  color: #fff;
}

.avatar i {
  font-size: 2rem;
  color: #a0a0b0;
}

.avatar i:hover {
  color: #fff;
}

.main-content {
  flex: 1;
  min-height: calc(100vh - 70px - 90px); /* вычитаем высоту навбара и плеера */
  padding: 0;
  margin: 0;
}

/* Медиа-запросы для мобилок */
@media (max-width: 768px) {
  .navbar {
    padding: 1rem;
  }

  .nav-links a span {
    display: none;
  }

  .nav-links a i {
    font-size: 1.3rem;
  }
}
</style>
