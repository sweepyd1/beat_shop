<template>
  <div class="genres-page">
    <h1>Все жанры</h1>
    <div class="genre-grid">
      <div
        v-for="genre in genres"
        :key="genre.id"
        class="genre-card vinyl"
        @click="$router.push(`/genre/${genre.id}`)"
      >
        <div class="vinyl-record">
          <img
            :src="genre.displayImage"
            :alt="genre.name"
            class="genre-cover"
            @error="handleImageError(genre)"
          />
          <div class="vinyl-label">{{ genre.name.substring(0, 2) }}</div>
        </div>
        <div class="genre-info">
          <h3>{{ genre.name }}</h3>
          <p>{{ genre.tracks_count }} треков</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';

const genres = ref([]);
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const DEFAULT_GENRE_COVER = 'https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=300&h=300&fit=crop';

/**
 * Формирует полный URL изображения жанра
 */
const getGenreImageUrl = (genre) => {
  if (genre.image_url) {
    
    if (genre.image_url.startsWith('http')) {
      return genre.image_url;
    }
    
    return `${BASE_URL}${genre.image_url}`;
  }
  
  return DEFAULT_GENRE_COVER;
};

/**
 * Обработчик ошибки загрузки изображения
 */
const handleImageError = (genre) => {
  genre.displayImage = DEFAULT_GENRE_COVER;
};

onMounted(async () => {
  try {
    const { data } = await api.get('/genres');
    genres.value = data.map(g => ({
      id: g.id,
      name: g.name,
      image_url: g.image_url,
      tracks_count: g.tracks_count || 0,
      displayImage: getGenreImageUrl(g)
    }));
  } catch (error) {
    console.error('Ошибка загрузки жанров:', error);
  }
});
</script>

<style scoped>

.genres-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.genres-page h1 {
  font-size: 2.5rem;
  margin-bottom: 2rem;
  background: linear-gradient(135deg, #fff, #e0b0ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.genre-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 2rem;
}

.genre-card {
  cursor: pointer;
  transition: transform 0.3s;
  text-align: center;
}

.genre-card:hover {
  transform: translateY(-8px);
}

.vinyl-record {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  transition: transform 0.5s;
}

.genre-card:hover .vinyl-record {
  transform: rotate(20deg);
}

.genre-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  border: 3px solid #a855f7;
  box-sizing: border-box;
}

.vinyl-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 35%;
  height: 35%;
  background: radial-gradient(circle, #333, #111);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 1.5rem;
  border: 2px solid #a855f7;
  box-shadow: 0 0 15px rgba(168, 85, 247, 0.5);
}

.genre-info {
  margin-top: 1rem;
}

.genre-info h3 {
  font-size: 1.2rem;
  margin-bottom: 0.2rem;
}

.genre-info p {
  color: #a0a0b0;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .genre-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
  }
}
</style>