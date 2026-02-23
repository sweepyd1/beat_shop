<template>
  <div class="player">
    <div class="track-info">
      <img :src="track.cover" :alt="track.title" class="cover" />
      <div class="details">
        <div class="title">{{ track.title }}</div>
        <div class="artist">{{ track.artist }}</div>
      </div>
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
      <span class="time">{{ formatTime(track.duration) }}</span>
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
import { ref, computed, onMounted, onUnmounted, watch, inject } from "vue";

const props = defineProps(["track"]);

const { isPlaying, playTrack } = inject("player");
// Локальное состояние плеера
const currentTime = ref(0);
const duration = ref(props.track.duration);
const volume = ref(0.7);
const progressBar = ref(null);

let audio = null;
let interval = null;

// Инициализация аудио
onMounted(() => {
  audio = new Audio(props.track.audioSrc);
  audio.volume = volume.value;
  audio.addEventListener("loadedmetadata", () => {
    duration.value = audio.duration;
  });
  audio.addEventListener("timeupdate", updateTime);
  audio.addEventListener("ended", next);
});

onUnmounted(() => {
  if (audio) {
    audio.pause();
    audio.removeEventListener("timeupdate", updateTime);
    audio.removeEventListener("ended", next);
    audio = null;
  }
  if (interval) clearInterval(interval);
});

watch(isPlaying, (val) => {
  if (val) audio?.play();
  else audio?.pause();
});

watch(
  () => props.track,
  (newTrack) => {
    if (audio) {
      audio.pause();
      audio.src = newTrack.audioSrc;
      audio.load();
      if (isPlaying.value) audio.play();
    }
  }
);

const updateTime = () => {
  currentTime.value = audio.currentTime;
};

const togglePlay = () => {
  isPlaying.value = !isPlaying.value;
};

const formatTime = (sec) => {
  const minutes = Math.floor(sec / 60);
  const seconds = Math.floor(sec % 60)
    .toString()
    .padStart(2, "0");
  return `${minutes}:${seconds}`;
};

const progressPercent = computed(
  () => (currentTime.value / duration.value) * 100
);

const seek = (e) => {
  const rect = progressBar.value.getBoundingClientRect();
  const percent = (e.clientX - rect.left) / rect.width;
  audio.currentTime = percent * duration.value;
};

const updateVolume = () => {
  if (audio) audio.volume = volume.value;
};

const prev = () => {
  // в реальном приложении здесь переключение на предыдущий трек
};

const next = () => {
  // переключение на следующий
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
