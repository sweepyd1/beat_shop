<template>
  <div v-if="track" class="player">
    <div class="track-info">
       <img :src="coverUrl" :alt="track.title" class="cover" />
      <div class="details">
        <div class="title">{{ track.title }}</div>
        <div class="artist">
          {{ track.author.full_name || "Unknown Artist" }}
        </div>
      </div>
      <button  @click="toggleFavorite" class="favorite-btn" :class="{ active: isFavorite }">
        <i :class="isFavorite ? 'fas fa-heart' : 'far fa-heart'"></i>
      </button>
    </div>

    <div class="player-controls">
      <button @click="prev" class="control-btn">
        <i class="fas fa-step-backward"></i>
      </button>
      <button @click="togglePlay" class="play-btn">
        <i :class="isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
      </button>
      <button @click="next" class="control-btn">
        <i class="fas fa-step-forward"></i>
      </button>
    </div>

    <div class="progress-area">
      <span class="time">{{ formatTime(currentTime) }}</span>
      <div class="progress-bar" ref="progressBar" @click="seek">
        <div
          class="progress-fill"
          :style="{ width: progressPercent + '%' }"
        ></div>
      </div>
      <span class="time">{{ formatTime(duration) }}</span>
    </div>

    <div class="volume-control">
      <i class="fas fa-volume-up"></i>
      <input
        type="range"
        min="0"
        max="1"
        step="0.01"
        v-model="volume"
        @input="updateVolume"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, watch, inject } from 'vue';
import { useRouter } from 'vue-router';

import api from '../api/index.js';
import { storeToRefs } from 'pinia';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const { isAuthenticated, user } = storeToRefs(authStore);

const router = useRouter();
const listenLoggedForTrack = ref(null);

/**
 * Отправляет событие прослушивания на бэкенд.
 * Вызывается один раз при начале воспроизведения трека.
 */
const logListen = async () => {
  // Не логируем, если: нет трека, пользователь не авторизован, или уже логировали этот трек
  if (!track.value?.id || !isLoggedIn.value || listenLoggedForTrack.value === track.value.id) {
    return;
  }

  try {
    await api.post(`/listen/${track.value.id}`);
    listenLoggedForTrack.value = track.value.id; // запоминаем, что залогировали
    // console.log(`✓ Listen logged for track ${track.value.id}`);
  } catch (error) {
    // Не блокируем плеер при ошибке логирования
    console.warn('Failed to log listen:', error?.response?.data || error.message);
  }
};

// Получаем глобальное состояние
const player = inject("player");
if (!player) {
  console.error("Player: no player injected");
}
const { currentTrack, isPlaying, nextTrack, prevTrack } = player || {};

// Локальный трек (реактивный)
const track = computed(() => currentTrack?.value);

// Состояние избранного
const isFavorite = ref(false);
const isLoggedIn = isAuthenticated;

// Проверка, добавлен ли трек в избранное
const checkFavorite = async () => {
  if (!track.value?.id || !isLoggedIn.value) return;
  try {
    const { data } = await api.get(`/favorites`);
    isFavorite.value = data.some(fav => fav.track_id === track.value.id);
  } catch (err) {
    console.error('Failed to check favorite', err);
  }
};

// Добавить/удалить из избранного
const toggleFavorite = async () => {
  if (!track.value?.id) return;
  if (!isLoggedIn.value) {
    router.push('/login');
    return;
  }
  window.dispatchEvent(new CustomEvent('favorites-updated'));
  try {
    if (isFavorite.value) {
      await api.delete(`/favorites/${track.value.id}`);
      isFavorite.value = false;
    } else {
      await api.post(`/favorites/${track.value.id}`);
      isFavorite.value = true;
    }
  } catch (err) {
    console.error('Failed to toggle favorite', err);
  }
};
// Локальное состояние
const currentTime = ref(0);
const duration = ref(0);
const volume = ref(0.7);
const progressBar = ref(null);

let audio = null;

// Инициализация аудио
const initAudio = () => {
  if (audio) {
    audio.pause();
    audio.removeEventListener("timeupdate", updateTime);
    audio.removeEventListener("ended", next);
  }
  if (!track.value) return;

  // Используем прямой URL к mp3 из трека
  const streamUrl = track.value.mp3_file_url;
  if (!streamUrl) {
    console.error("Player: no mp3_file_url for track", track.value);
    return;
  }
  console.log("Player: loading audio from", streamUrl);
  audio = new Audio(streamUrl);
  audio.volume = volume.value;
  audio.addEventListener("loadedmetadata", () => {
    duration.value = audio.duration;
    console.log("Player: duration", duration.value);
  });
  audio.addEventListener("timeupdate", updateTime);
  audio.addEventListener("ended", () => {
    console.log("Player: track ended");
    nextTrack();
  });
};

const updateTime = () => {
  if (audio) currentTime.value = audio.currentTime;
};
const coverUrl = computed(() => {
  const url = track.value?.cover_url;
  if (!url) return '/default-cover.jpg';
  if (url.startsWith('http')) return url;
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  return `${baseUrl}${url}`;
});
// Следим за сменой трека
// Следим за сменой трека
watch(track, (newTrack, oldTrack) => {
  console.log("Player: track changed", newTrack);
  
  // Сбрасываем флаг логирования при смене трека
  if (newTrack?.id !== oldTrack?.id) {
    listenLoggedForTrack.value = null;
  }
  
  if (newTrack) {
    initAudio();
    checkFavorite(); // ✅ Добавлено: проверяем избранное при смене трека
    if (isPlaying?.value) {
      audio?.play().catch((e) => {
        console.error("Play error:", e);
        if (isPlaying) isPlaying.value = false;
      });
    }
  } else {
    if (audio) {
      audio.pause();
      audio = null;
    }
  }
});

// Следим за состоянием воспроизведения
watch(isPlaying, async (playing) => {
  if (!audio) return;
  if (playing) {
    try {
      await audio.play();
      // ✅ Успешно начали играть — логируем прослушивание
      logListen();
    } catch (e) {
      console.error("Play error:", e);
      // Если play() упал (например, автоплей заблокирован), не логируем
      if (isPlaying) isPlaying.value = false;
    }
  } else {
    audio.pause();
  }
});

// Очистка
onUnmounted(() => {
  if (audio) {
    audio.pause();
    audio.removeEventListener("timeupdate", updateTime);
    audio.removeEventListener("ended", next);
    audio = null;
  }
});

const togglePlay = () => {
  if (isPlaying) isPlaying.value = !isPlaying.value;
};

const formatTime = (sec) => {
  if (isNaN(sec)) return "0:00";
  const minutes = Math.floor(sec / 60);
  const seconds = Math.floor(sec % 60)
    .toString()
    .padStart(2, "0");
  return `${minutes}:${seconds}`;
};

const progressPercent = computed(() => {
  if (!duration.value) return 0;
  return (currentTime.value / duration.value) * 100;
});

const seek = (e) => {
  if (!progressBar.value) return;
  const rect = progressBar.value.getBoundingClientRect();
  const percent = (e.clientX - rect.left) / rect.width;
  if (audio) audio.currentTime = percent * duration.value;
};

const updateVolume = () => {
  if (audio) audio.volume = volume.value;
};

const next = () => {
  console.log('Next button clicked');
  console.log('player object:', player);
  console.log('nextTrack function:', nextTrack);
  if (nextTrack) {
    nextTrack();
  } else {
    console.error('nextTrack is not defined');
  }
};
const prev = () => {
  console.log('Prev button clicked');
  if (prevTrack) prevTrack();
  else console.error('prevTrack is not defined');
};
</script>

<style scoped>
/* Стили из вашего оригинального Player.vue (скопируйте их сюда) */
.player {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(20, 20, 30, 0.95);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 200;
}
.track-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 250px;
}
.cover {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  object-fit: cover;
}
.details .title {
  font-weight: 600;
  margin-bottom: 0.2rem;
}
.details .artist {
  font-size: 0.85rem;
  color: #a0a0b0;
}
.favorite-btn {
  background: none;
  border: none;
  color: #a0a0b0;
  font-size: 1.2rem;
  cursor: pointer;
  transition: color 0.2s;
  margin-left: 0.5rem;
}
.favorite-btn.active {
  color: #ff4d4d;
}
.favorite-btn:hover {
  color: #ff4d4d;
}
.player-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.control-btn {
  background: none;
  border: none;
  color: #a0a0b0;
  font-size: 1.2rem;
  cursor: pointer;
  transition: color 0.2s;
}
.control-btn:hover {
  color: #fff;
}
.play-btn {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}
.play-btn:hover {
  transform: scale(1.05);
}
.progress-area {
  flex: 1;
  max-width: 500px;
  display: flex;
  align-items: center;
  gap: 1rem;
}
.time {
  font-size: 0.85rem;
  color: #a0a0b0;
  min-width: 40px;
}
.progress-bar {
  flex: 1;
  height: 5px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  cursor: pointer;
  position: relative;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #a855f7, #3b82f6);
  border-radius: 5px;
  width: 0%;
}
.volume-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #a0a0b0;
}
.volume-control input {
  width: 80px;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  height: 5px;
}
</style>
