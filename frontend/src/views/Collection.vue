<template>
  <div class="collection">
    <div class="collection-header">
      <img
        :src="collection.cover"
        :alt="collection.title"
        class="collection-cover"
      />
      <div class="collection-info">
        <span class="type">Плейлист</span>
        <h1>{{ collection.title }}</h1>
        <p class="description">{{ collection.description }}</p>
        <div class="meta">
          <span><i class="fas fa-user"></i> {{ collection.creator }}</span>
          <span><i class="fas fa-clock"></i> {{ totalDuration }}</span>
          <span
            ><i class="fas fa-music"></i>
            {{ collection.tracks.length }} треков</span
          >
        </div>
        <button class="play-all" @click="playAll">
          <i class="fas fa-play"></i> Слушать все
        </button>
      </div>
    </div>

    <div class="track-list">
      <div
        v-for="(track, index) in collection.tracks"
        :key="track.id"
        class="track-item"
        @click="playTrack(track)"
      >
        <span class="index">{{ index + 1 }}</span>
        <img :src="track.cover" :alt="track.title" class="track-cover" />
        <div class="track-details">
          <h3>{{ track.title }}</h3>
          <p>{{ track.artist }}</p>
        </div>
        <span class="duration">{{ formatTime(track.duration) }}</span>
        <button class="more"><i class="fas fa-ellipsis-h"></i></button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, inject } from "vue";

const { playTrack } = inject("player");

// Мок-данные коллекции
const collection = {
  id: 1,
  title: "Chill Vibes",
  cover: "https://via.placeholder.com/300",
  description: "Идеальный плейлист для расслабления и медитации.",
  creator: "Admin",
  tracks: [
    {
      id: 1,
      title: "Neon Dreams",
      artist: "Arctica",
      cover: "https://via.placeholder.com/200",
      duration: 210,
      audioSrc: "",
    },
    {
      id: 2,
      title: "Lost in Space",
      artist: "Cosmic",
      cover: "https://via.placeholder.com/200",
      duration: 185,
      audioSrc: "",
    },
    {
      id: 4,
      title: "Midnight",
      artist: "Luna",
      cover: "https://via.placeholder.com/200",
      duration: 200,
      audioSrc: "",
    },
  ],
};

const totalDuration = computed(() => {
  const totalSec = collection.tracks.reduce((acc, t) => acc + t.duration, 0);
  const hours = Math.floor(totalSec / 3600);
  const minutes = Math.floor((totalSec % 3600) / 60);
  return hours > 0 ? `${hours} ч ${minutes} мин` : `${minutes} мин`;
});

const formatTime = (sec) => {
  const minutes = Math.floor(sec / 60);
  const seconds = Math.floor(sec % 60)
    .toString()
    .padStart(2, "0");
  return `${minutes}:${seconds}`;
};

const playAll = () => {
  if (collection.tracks.length) playTrack(collection.tracks[0]);
};
</script>

<style scoped>
.collection {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
}

.collection-header {
  display: flex;
  gap: 3rem;
  margin-bottom: 3rem;
  align-items: flex-end;
}

.collection-cover {
  width: 250px;
  height: 250px;
  border-radius: 16px;
  object-fit: cover;
  box-shadow: 0 20px 30px rgba(0, 0, 0, 0.5);
}

.collection-info .type {
  color: #a855f7;
  text-transform: uppercase;
  font-size: 0.9rem;
  letter-spacing: 1px;
  font-weight: 600;
}

.collection-info h1 {
  font-size: 3rem;
  margin: 0.5rem 0;
}

.description {
  color: #a0a0b0;
  margin-bottom: 1rem;
}

.meta {
  display: flex;
  gap: 1.5rem;
  color: #a0a0b0;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

.meta i {
  margin-right: 0.5rem;
  color: #a855f7;
}

.play-all {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border: none;
  color: white;
  padding: 0.8rem 2rem;
  border-radius: 30px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: transform 0.2s;
}

.play-all:hover {
  transform: scale(1.05);
}

.track-list {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 20px;
  padding: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.track-item {
  display: flex;
  align-items: center;
  padding: 0.8rem 1rem;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.track-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.index {
  width: 30px;
  color: #a0a0b0;
  font-size: 0.9rem;
}

.track-cover {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  object-fit: cover;
  margin-right: 1rem;
}

.track-details {
  flex: 1;
}

.track-details h3 {
  font-size: 1rem;
  margin-bottom: 0.2rem;
}

.track-details p {
  font-size: 0.85rem;
  color: #a0a0b0;
}

.duration {
  color: #a0a0b0;
  font-size: 0.9rem;
  margin-right: 1.5rem;
}

.more {
  background: none;
  border: none;
  color: #a0a0b0;
  font-size: 1.2rem;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
}

.track-item:hover .more {
  opacity: 1;
}
</style>
