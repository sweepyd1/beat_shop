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
            :src="genre.cover"
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

// Маппинг обложек (можно вынести в отдельный файл, пока копия из Home)
const genreCoverMap = {
  'hip-hop': 'https://images.unsplash.com/photo-1614680376408-81e91ffe3db7?w=300&h=300&fit=crop',
  'trap': 'https://images.unsplash.com/photo-1598387993281-cecf8b71a8f8?w=300&h=300&fit=crop',
  'electronic': 'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300&h=300&fit=crop',
  'house': 'https://images.unsplash.com/photo-1571330735066-03aaa9429d89?w=300&h=300&fit=crop',
  'techno': 'https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b?w=300&h=300&fit=crop',
  'rock': 'https://images.unsplash.com/photo-1498038432885-c6f3f1b912ee?w=300&h=300&fit=crop',
  'jazz': 'https://images.unsplash.com/photo-1415201364774-f6f0bb35f28f?w=300&h=300&fit=crop',
  'rnb': 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&h=300&fit=crop',
  'pop': 'https://images.unsplash.com/photo-1614149162883-504ce4d13909?w=300&h=300&fit=crop',
  'lo-fi': 'https://images.unsplash.com/photo-1487180144351-b8472da7d491?w=300&h=300&fit=crop',
  'classical': 'https://images.unsplash.com/photo-1507838153414-b4b713384a76?w=300&h=300&fit=crop',
  'reggae': 'https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=300&h=300&fit=crop',
  'metal': 'https://images.unsplash.com/photo-1510915361819-9bd2b4d2a2fb?w=300&h=300&fit=crop',
  'country': 'https://images.unsplash.com/photo-1516280440614-37939bbacd81?w=300&h=300&fit=crop',
  'blues': 'https://images.unsplash.com/photo-1509123777025-4be1efd6cce1?w=300&h=300&fit=crop'
};

const DEFAULT_GENRE_COVER = 'https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=300&h=300&fit=crop';

const getGenreCover = (name) => {
  if (!name) return DEFAULT_GENRE_COVER;
  const key = name.toLowerCase();
  return genreCoverMap[key] || DEFAULT_GENRE_COVER;
};

const handleImageError = (genre) => {
  genre.cover = DEFAULT_GENRE_COVER;
};

onMounted(async () => {
  try {
    const { data } = await api.get('/genres');
    genres.value = data.map(g => ({
      id: g.id,
      name: g.name,
      cover: getGenreCover(g.name),
      tracks_count: g.tracks_count || 0
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