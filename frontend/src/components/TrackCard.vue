<template>
  <div class="track-card" @click="handleClick">
    <div class="cover-wrapper">
      <img :src="track.cover" @error="$emit('image-error', $event)" />
      <button class="play-overlay" @click.stop="play">
        <i class="fas fa-play"></i>
      </button>
    </div>
    <div class="track-info">
      <h3>{{ track.title }}</h3>
      <p>{{ track.artist }}</p>
    </div>
  </div>
</template>

<script setup>
import { inject } from "vue";

const props = defineProps(["track"]);
const { playTrack } = inject("player");

const play = () => {
  playTrack(props.track);
};

const handleClick = () => {
  // можно перейти на страницу трека, но для простоты просто воспроизводим
  play();
};
</script>

<style scoped>
.track-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.track-card:hover {
  transform: translateY(-5px);
}

.cover-wrapper {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 0.8rem;
  aspect-ratio: 1;
}

.cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.track-card:hover .cover {
  transform: scale(1.05);
}

.play-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  cursor: pointer;
}

.track-card:hover .play-overlay {
  opacity: 1;
}

.play-overlay:hover {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border-color: transparent;
}

.track-info h3 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.2rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-info p {
  font-size: 0.85rem;
  color: #a0a0b0;
}
</style>
