<template>
  <div class="genre-detail" :style="{ '--cover-url': `url(${genreCover})` }">
    <div class="genre-header">
      <img :src="genreCover" :alt="genre.name" class="genre-cover" @error="handleImageError" />
      <div class="genre-info">
        <span class="type"><i class="fas fa-guitar"></i> Жанр</span>
        <h1>{{ genre.name }}</h1>
        <p class="description">{{ description }}</p>
        <div class="meta">
          <span><i class="fas fa-user"></i> BeatHub</span>
          <span><i class="fas fa-clock"></i> {{ totalDuration }}</span>
          <span><i class="fas fa-music"></i> {{ tracks.length }} треков</span>
        </div>
      </div>
    </div>

    <div class="track-list">
      <!-- Заголовок (без лайков) -->
      <div class="track-list-header">
        <span class="index">#</span>
        <span class="cover-placeholder"></span>
        <div class="track-details-placeholder">Название</div>
        <span class="plays">Прослушивания</span>
        <span class="duration">Длительность</span>
        <button class="more" disabled style="visibility: hidden;"></button>
      </div>

      <div
        v-for="(track, index) in tracks"
        :key="track.id"
        class="track-item"
        @click="playTrack(track)"
      >
        <span class="index">{{ index + 1 }}</span>
        <img :src="track.cover_url" :alt="track.title" class="track-cover" @error="handleImageError" />
        <div class="track-details">
          <h3>{{ track.title }}</h3>
          <p>{{ track.author?.full_name || 'Неизвестен' }}</p>
        </div>
        <span class="plays">{{ formatPlays(track.plays) }}</span>
        <span class="duration">{{ formatTime(track.duration_seconds) }}</span>
        <button class="more" @click.stop><i class="fas fa-ellipsis-h"></i></button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue';
import { useRoute } from 'vue-router';
import api from '../api';

const route = useRoute();
const player = inject("player", null);
const playTrack = player?.playTrack || ((track) => console.warn("player not provided", track));

const genre = ref({ id: null, name: 'Загрузка...' });
const tracks = ref([]);
const genreCover = ref('');

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const DEFAULT_GENRE_COVER = 'https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=500&h=500&fit=crop';

const genreCoverMap = {
  'hip-hop': 'https://images.unsplash.com/photo-1614680376408-81e91ffe3db7?w=500&h=500&fit=crop',
  'trap': 'https://images.unsplash.com/photo-1598387993281-cecf8b71a8f8?w=500&h=500&fit=crop',
  'electronic': 'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=500&h=500&fit=crop',
  'house': 'https://images.unsplash.com/photo-1571330735066-03aaa9429d89?w=500&h=500&fit=crop',
  'techno': 'https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b?w=500&h=500&fit=crop',
  'rock': 'https://images.unsplash.com/photo-1498038432885-c6f3f1b912ee?w=500&h=500&fit=crop',
  'jazz': 'https://images.unsplash.com/photo-1415201364774-f6f0bb35f28f?w=500&h=500&fit=crop',
  'rnb': 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=500&h=500&fit=crop',
  'pop': 'https://images.unsplash.com/photo-1614149162883-504ce4d13909?w=500&h=500&fit=crop',
  'lo-fi': 'https://images.unsplash.com/photo-1487180144351-b8472da7d491?w=500&h=500&fit=crop',
  'classical': 'https://images.unsplash.com/photo-1507838153414-b4b713384a76?w=500&h=500&fit=crop',
  'reggae': 'https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=500&h=500&fit=crop',
  'metal': 'https://images.unsplash.com/photo-1510915361819-9bd2b4d2a2fb?w=500&h=500&fit=crop',
  'country': 'https://images.unsplash.com/photo-1516280440614-37939bbacd81?w=500&h=500&fit=crop',
  'blues': 'https://images.unsplash.com/photo-1509123777025-4be1efd6cce1?w=500&h=500&fit=crop'
};

const getGenreImageUrl = (genreData) => {
  if (genreData.image_url) {
    if (genreData.image_url.startsWith('http')) return genreData.image_url;
    return `${BASE_URL}${genreData.image_url}`;
  }
  const key = genreData.name?.toLowerCase() || '';
  return genreCoverMap[key] || DEFAULT_GENRE_COVER;
};

const description = computed(() => {
  return `Лучшие биты и треки в стиле ${genre.value.name}. Наслаждайтесь музыкой напрямую от авторов.`;
});

const totalDuration = computed(() => {
  const totalSec = tracks.value.reduce((acc, t) => acc + (t.duration_seconds || 0), 0);
  const hours = Math.floor(totalSec / 3600);
  const minutes = Math.floor((totalSec % 3600) / 60);
  return hours > 0 ? `${hours} ч ${minutes} мин` : `${minutes} мин`;
});

const formatTime = (sec) => {
  if (!sec) return '0:00';
  const minutes = Math.floor(sec / 60);
  const seconds = Math.floor(sec % 60).toString().padStart(2, "0");
  return `${minutes}:${seconds}`;
};

const formatPlays = (plays) => {
  if (!plays) return '0';
  if (plays >= 1000) return `${(plays / 1000).toFixed(1)}K`;
  return plays.toString();
};

const handleImageError = (event) => {
  event.target.src = DEFAULT_GENRE_COVER;
};

onMounted(async () => {
  const genreId = Number(route.params.id);
  try {
    const { data: genres } = await api.get('/genres');
    const found = genres.find(g => g.id === genreId);
    if (found) {
      genre.value = found;
      genreCover.value = getGenreImageUrl(found);
    } else {
      genre.value = { id: genreId, name: 'Неизвестный жанр', image_url: null };
      genreCover.value = DEFAULT_GENRE_COVER;
    }

    const { data: searchResult } = await api.get('/tracks/search', {
      params: { genre_ids: [genreId], limit: 50, sort_by: 'popular' }
    });
    tracks.value = searchResult;
  } catch (error) {
    console.error('Ошибка загрузки данных жанра:', error);
    genreCover.value = DEFAULT_GENRE_COVER;
  }
});
</script>

<style scoped>
/* Базовые стили (десктоп) */
.track-list-header,
.track-item {
  display: grid;
  grid-template-columns: 40px 60px 1fr 130px 80px 50px;
  align-items: center;
  gap: 1rem;
  padding: 0.8rem 1rem;
}

.track-list-header {
  color: #a0a0b0;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  margin-bottom: 0.5rem;
}

.plays, .duration {
  white-space: nowrap;
}

.cover-placeholder {
  width: 40px;
  height: 40px;
}

.track-details-placeholder {
  font-weight: 600;
}

.track-item {
  cursor: pointer;
  border-radius: 12px;
  transition: background 0.2s;
  border-bottom: 1px solid rgba(255, 255, 255, 0.02);
}

.track-item:hover {
  background: rgba(168, 85, 247, 0.1);
}

.index {
  color: #a0a0b0;
  font-size: 0.9rem;
  text-align: center;
}

.track-cover {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  object-fit: cover;
}

.track-details h3 {
  font-size: 1rem;
  margin-bottom: 0.2rem;
}

.track-details p {
  font-size: 0.85rem;
  color: #a0a0b0;
}

.plays, .duration {
  color: #a0a0b0;
  font-size: 0.9rem;
  text-align: left;
}

.more {
  background: none;
  border: none;
  color: #a0a0b0;
  font-size: 1.2rem;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
  justify-self: end;
}

.track-item:hover .more {
  opacity: 1;
}

.genre-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  position: relative;
  isolation: isolate;
}
.genre-detail::before {
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
.genre-header {
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
.genre-cover {
  width: 250px;
  height: 250px;
  border-radius: 24px;
  object-fit: cover;
  box-shadow: 0 20px 30px rgba(0, 0, 0, 0.5), 0 0 0 2px rgba(168, 85, 247, 0.3);
}
.genre-info .type {
  color: #a855f7;
  text-transform: uppercase;
  font-size: 0.9rem;
  letter-spacing: 1px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.genre-info h1 {
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
}
.meta i {
  margin-right: 0.5rem;
  color: #a855f7;
}

/* Адаптивность для телефонов */
@media (max-width: 768px) {
  .genre-detail {
    padding: 1rem;
  }
  
  .genre-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 1.5rem;
    padding: 1.5rem;
  }
  
  .genre-cover {
    width: 180px;
    height: 180px;
  }
  
  .genre-info h1 {
    font-size: 2rem;
  }
  
  .description {
    font-size: 0.9rem;
  }
  
  .meta {
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
  }
  
  /* Горизонтальная прокрутка для таблицы треков */
  .track-list {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .track-list-header,
  .track-item {
    min-width: 500px; /* фиксируем минимальную ширину, чтобы не сжимались слишком сильно */
    gap: 0.8rem;
    padding: 0.6rem 0.8rem;
  }
  
  /* Скрываем колонку "Прослушивания" на телефонах (опционально) */
  .track-list-header .plays,
  .track-item .plays {
    display: none;
  }
  
  /* Переопределяем грид без колонки plays (она скрыта) */
  .track-list-header,
  .track-item {
    grid-template-columns: 30px 50px 1fr 70px 40px;
  }
  
  .index {
    width: auto;
  }
  
  .track-cover {
    width: 35px;
    height: 35px;
  }
  
  .track-details h3 {
    font-size: 0.9rem;
  }
  
  .track-details p {
    font-size: 0.75rem;
  }
  
  .duration {
    font-size: 0.8rem;
  }
  
  .more {
    font-size: 1rem;
  }
}
</style>