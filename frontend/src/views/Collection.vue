<!-- Файл: Collection.vue (обновлённый) -->
<template>
  <div class="collection" :style="{ '--cover-url': `url(${collection.cover})` }">
    <div class="collection-header parallax">
      <img
        :src="collection.cover"
        :alt="collection.title"
        class="collection-cover"
        @error="handleImageError"
      />
      <div class="collection-info">
        <span class="type"><i class="fas fa-album"></i> Плейлист</span>
        <h1>{{ collection.title }}</h1>
        <p class="description">{{ collection.description }}</p>
        <div class="meta">
          <span><i class="fas fa-user"></i> {{ collection.creator }}</span>
          <span><i class="fas fa-clock"></i> {{ totalDuration }}</span>
          <span><i class="fas fa-music"></i> {{ collection.tracks.length }} треков</span>
          <span><i class="fas fa-heart"></i> 1.2K</span>
        </div>
        <div class="actions">
          <button class="play-all" @click="playAll">
            <i class="fas fa-play"></i> Слушать все
          </button>
          <button class="save-btn"><i class="fas fa-bookmark"></i> Сохранить</button>
          <button class="share-btn"><i class="fas fa-share-alt"></i></button>
        </div>
      </div>
    </div>

    <div class="track-list">
      <div class="track-list-header">
        <span class="index">#</span>
        <span class="cover"></span>
        <span class="title">Название</span>
        <span class="plays">Прослушивания</span>
        <span class="likes">Лайки</span>
        <span class="duration">Длительность</span>
        <span class="actions"></span>
      </div>
      <div
        v-for="(track, index) in collection.tracks"
        :key="track.id"
        class="track-item"
        @click="playTrack(track)"
      >
        <span class="index">{{ index + 1 }}</span>
        <img :src="track.cover" :alt="track.title" class="track-cover" @error="handleImageError" />
        <div class="track-details">
          <h3>{{ track.title }}</h3>
          <p>{{ track.artist }}</p>
        </div>
        <span class="plays">{{ track.plays || '2.1K' }}</span>
        <span class="likes">{{ track.likes || 234 }}</span>
        <span class="duration">{{ formatTime(track.duration) }}</span>
        <button class="more" @click.stop><i class="fas fa-ellipsis-h"></i></button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, inject } from "vue";

const { playTrack } = inject("player", { playTrack: (t) => console.log("play", t) });

const collection = {
  id: 1,
  title: "Chill Vibes",
  cover: "https://picsum.photos/500/500?random=100",
  description: "Идеальный плейлист для расслабления и медитации. 2 часа плавных битов.",
  creator: "Admin",
  tracks: [
    { id: 1, title: "Neon Dreams", artist: "Arctica", cover: "https://picsum.photos/200/200?random=1", duration: 210, plays: 12400, likes: 543 },
    { id: 2, title: "Lost in Space", artist: "Cosmic", cover: "https://picsum.photos/200/200?random=2", duration: 185, plays: 8700, likes: 321 },
    { id: 4, title: "Midnight", artist: "Luna", cover: "https://picsum.photos/200/200?random=4", duration: 200, plays: 3200, likes: 187 },
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
  const seconds = Math.floor(sec % 60).toString().padStart(2, "0");
  return `${minutes}:${seconds}`;
};

const playAll = () => {
  if (collection.tracks.length) playTrack(collection.tracks[0]);
};

const handleImageError = (e) => {
  e.target.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200' viewBox='0 0 24 24' fill='%23cccccc'%3E%3Cpath d='M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z'/%3E%3C/svg%3E";
};
</script>

<style scoped>
.collection {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  position: relative;
  isolation: isolate;
}

/* Параллакс-фон из обложки */
.collection::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: var(--cover-url) center/cover no-repeat fixed;
  filter: blur(60px) brightness(0.3);
  z-index: -1;
  pointer-events: none;
}

.collection-header {
  display: flex;
  gap: 3rem;
  margin-bottom: 3rem;
  align-items: flex-end;
  background: rgba(10, 10, 15, 0.7);
  backdrop-filter: blur(20px);
  border-radius: 30px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
}

.collection-cover {
  width: 250px;
  height: 250px;
  border-radius: 24px;
  object-fit: cover;
  box-shadow: 0 20px 30px rgba(0, 0, 0, 0.5), 0 0 0 2px rgba(168, 85, 247, 0.3);
  transition: transform 0.3s;
}

.collection-cover:hover {
  transform: scale(1.02);
}

.collection-info {
  flex: 1;
}

.collection-info .type {
  color: #a855f7;
  text-transform: uppercase;
  font-size: 0.9rem;
  letter-spacing: 1px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.collection-info h1 {
  font-size: 3.5rem;
  margin: 0.5rem 0;
  background: linear-gradient(135deg, #fff, #e0b0ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.description {
  color: #a0a0b0;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.meta {
  display: flex;
  gap: 1.5rem;
  color: #a0a0b0;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
  flex-wrap: wrap;
}

.meta i {
  margin-right: 0.5rem;
  color: #a855f7;
}

.actions {
  display: flex;
  gap: 1rem;
  align-items: center;
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
  transition: all 0.2s;
}

.play-all:hover {
  transform: scale(1.05);
  box-shadow: 0 10px 20px rgba(168, 85, 247, 0.4);
}

.save-btn, .share-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  padding: 0.8rem 1.5rem;
  border-radius: 30px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.share-btn {
  padding: 0.8rem 1.2rem;
}

.save-btn:hover, .share-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: #a855f7;
}

/* Таблица треков */
.track-list {
  background: rgba(10, 10, 15, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.track-list-header {
  display: flex;
  align-items: center;
  padding: 0.8rem 1rem;
  color: #a0a0b0;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  margin-bottom: 0.5rem;
}

.track-item {
  display: flex;
  align-items: center;
  padding: 0.8rem 1rem;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid rgba(255, 255, 255, 0.02);
}

.track-item:hover {
  background: rgba(168, 85, 247, 0.1);
}

.index {
  width: 40px;
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
  flex: 2;
}

.track-details h3 {
  font-size: 1rem;
  margin-bottom: 0.2rem;
}

.track-details p {
  font-size: 0.85rem;
  color: #a0a0b0;
}

.plays, .likes, .duration {
  flex: 1;
  color: #a0a0b0;
  font-size: 0.9rem;
  text-align: right;
}

.plays, .likes {
  text-align: left;
}

.duration {
  margin-right: 1rem;
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

@media (max-width: 768px) {
  .collection-header { flex-direction: column; align-items: center; text-align: center; }
  .meta { justify-content: center; }
  .actions { justify-content: center; }
  .track-list-header .plays, .track-list-header .likes { display: none; }
  .plays, .likes { display: none; }
}
</style>