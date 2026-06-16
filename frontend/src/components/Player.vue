<template>
  <div v-if="track && isPlayerVisible" class="player">
    <!-- Кнопка закрытия (крестик) -->
    <button class="close-btn" @click="closePlayer">
      <i class="fas fa-times"></i>
    </button>

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

    <!-- Остальная часть шаблона без изменений -->
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

const logListen = async () => {
  if (!track.value?.id || !isLoggedIn.value || listenLoggedForTrack.value === track.value.id) {
    return;
  }
  try {
    await api.post(`/listen/${track.value.id}`);
    listenLoggedForTrack.value = track.value.id;
  } catch (error) {
    console.warn('Failed to log listen:', error?.response?.data || error.message);
  }
};

// Глобальное состояние плеера
const player = inject("player");
if (!player) {
  console.error("Player: no player injected");
}
const { currentTrack, isPlaying, nextTrack, prevTrack, togglePlay: globalTogglePlay } = player || {};

// Локальный трек
const track = computed(() => currentTrack?.value);

// Управление видимостью плеера
const isPlayerVisible = ref(true); // показываем по умолчанию

// Закрыть плеер
const closePlayer = () => {
  isPlayerVisible.value = false;
  // Остановить воспроизведение
  if (audio) {
    audio.pause();
    audio.currentTime = 0;
  }
  if (isPlaying) isPlaying.value = false;
  // Сбросить текущий трек, чтобы избежать фонового проигрывания при повторном открытии
  if (currentTrack) currentTrack.value = null;
};

// Избранное
const isFavorite = ref(false);
const isLoggedIn = isAuthenticated;

const checkFavorite = async () => {
  if (!track.value?.id || !isLoggedIn.value) return;
  try {
    const { data } = await api.get(`/favorites`);
    isFavorite.value = data.some(fav => fav.track_id === track.value.id);
  } catch (err) {
    console.error('Failed to check favorite', err);
  }
};

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

const currentTime = ref(0);
const duration = ref(0);
const volume = ref(0.7);
const progressBar = ref(null);
let audio = null;

const initAudio = () => {
  if (audio) {
    audio.pause();
    audio.removeEventListener("timeupdate", updateTime);
    audio.removeEventListener("ended", next);
  }
  if (!track.value) return;

  const streamUrl = track.value.mp3_file_url;
  if (!streamUrl) {
    console.log(streamUrl)
    console.error("Player: no mp3_file_url for track", track.value);
    return;
  }

  audio = new Audio(streamUrl);
  audio.volume = volume.value;
  audio.addEventListener("loadedmetadata", () => {
    duration.value = audio.duration;
  });
  audio.addEventListener("timeupdate", updateTime);
  audio.addEventListener("ended", () => {
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

watch(track, (newTrack, oldTrack) => {
  if (newTrack?.id !== oldTrack?.id) {
    listenLoggedForTrack.value = null;
  }
  if (newTrack) {
    isPlayerVisible.value = true; // показываем плеер при смене трека
    initAudio();
    checkFavorite();
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

watch(isPlaying, async (playing) => {
  if (!audio) return;
  if (playing) {
    try {
      await audio.play();
      logListen();
    } catch (e) {
      console.error("Play error:", e);
      if (isPlaying) isPlaying.value = false;
    }
  } else {
    audio.pause();
  }
});

onUnmounted(() => {
  if (audio) {
    audio.pause();
    audio.removeEventListener("timeupdate", updateTime);
    audio.removeEventListener("ended", next);
    audio = null;
  }
});

const togglePlay = () => {
  if (globalTogglePlay) globalTogglePlay();
};

const formatTime = (sec) => {
  if (isNaN(sec)) return "0:00";
  const minutes = Math.floor(sec / 60);
  const seconds = Math.floor(sec % 60).toString().padStart(2, "0");
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
  if (nextTrack) nextTrack();
  else console.error('nextTrack is not defined');
};

const prev = () => {
  if (prevTrack) prevTrack();
  else console.error('prevTrack is not defined');
};
</script>

<style scoped>
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

/* Стили кнопки закрытия */
.close-btn {
  position: absolute;
  top: 10px;
  right: 15px;
  background: transparent;
  border: none;
  color: #a0a0b0;
  font-size: 1.2rem;
  cursor: pointer;
  transition: color 0.2s;
  z-index: 10;
}
.close-btn:hover {
  color: #ffffff;
}

/* Остальные стили */
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

/* ===== АДАПТИВНЫЕ СТИЛИ ===== */

/* Планшеты и небольшие десктопы */
@media (max-width: 768px) {
  .player {
    padding: 0.75rem 1rem;
    flex-wrap: wrap;
    gap: 0.75rem;
  }

  .close-btn {
    top: 8px;
    right: 12px;
    font-size: 1rem;
  }

  .track-info {
    width: 100%;
    justify-content: space-between;
    gap: 0.75rem;
  }

  .details {
    flex: 1;
    min-width: 0; /* позволяет обрезать текст */
  }

  .details .title,
  .details .artist {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .player-controls {
    order: 2;
    margin: 0 auto;
  }

  .progress-area {
    order: 3;
    width: 100%;
    max-width: none;
    gap: 0.75rem;
  }

  .volume-control {
    order: 4;
    margin-left: auto;
  }

  .volume-control input {
    width: 70px;
  }

  .play-btn {
    width: 36px;
    height: 36px;
    font-size: 0.9rem;
  }

  .control-btn {
    font-size: 1rem;
  }
}

/* Мобильные телефоны (до 480px) */
@media (max-width: 480px) {
  .player {
    padding: 0.5rem 0.75rem;
    gap: 0.5rem;
  }

  .close-btn {
    top: 6px;
    right: 8px;
    font-size: 0.9rem;
  }

  .track-info {
    gap: 0.5rem;
  }

  .cover {
    width: 40px;
    height: 40px;
  }

  .details .title {
    font-size: 0.9rem;
  }

  .details .artist {
    font-size: 0.75rem;
  }

  .favorite-btn {
    font-size: 1rem;
    margin-left: 0;
  }

  .player-controls {
    gap: 0.75rem;
  }

  .play-btn {
    width: 32px;
    height: 32px;
    font-size: 0.8rem;
  }

  .control-btn {
    font-size: 0.9rem;
  }

  .progress-area {
    gap: 0.5rem;
  }

  .time {
    font-size: 0.75rem;
    min-width: 32px;
  }

  .volume-control {
    gap: 0.3rem;
  }

  .volume-control input {
    display: none; /* скрываем ползунок, оставляем только иконку */
  }

  .volume-control i {
    font-size: 0.9rem;
  }
}

/* Для устройств без hover (touch) — делаем кнопки всегда видимыми/активными */
@media (hover: none) {
  .close-btn:active {
    color: white;
  }
  .control-btn:active {
    color: white;
  }
  .play-btn:active {
    transform: scale(0.98);
  }
  .favorite-btn:active {
    color: #ff4d4d;
  }
}
</style>