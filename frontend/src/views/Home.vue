<template>
  <div class="home">
    <!-- Hero-секция с анимированным градиентом -->
    <section class="hero">
      <div class="hero-content">
        <h1>Покупай биты напрямую у авторов</h1>
        <p>
          Тысячи эксклюзивных битов в разных жанрах. Лицензии без скрытых
          платежей.
        </p>
        <button class="cta-btn pulse" @click="$router.push('/search')">
          Начать поиск
        </button>
      </div>
      <div class="hero-wave"></div>
    </section>

    <!-- Популярные биты -->
    <section class="section">
      <div class="section-header">
        <h2>Популярные биты</h2>
        <router-link to="/genres" class="view-all">Все жанры →</router-link>
      </div>
      <div class="track-grid">
        <TrackCard
          v-for="track in popularTracks"
          :key="track.id"
          :track="track"
          @image-error="handleImageError"
        />
      </div>
    </section>

    <!-- Коллекции по жанрам (виниловые пластинки) -->
    <section class="section">
    <div class="section-header">
      <h2>Подборки по жанрам</h2>
      <router-link to="/genres" class="view-all">Все жанры →</router-link>
    </div>
    <div class="genre-collections">
      <div
        v-for="collection in genreCollections"
        :key="collection.id"
        class="collection-card vinyl"
        @click="$router.push(`/genre/${collection.id}`)"
      >
        <div class="vinyl-record">
          <img
            :src="collection.cover"
            :alt="collection.genre"
            class="collection-cover"
            @error="handleGenreImageError(collection)"
          />
          <div class="vinyl-label">{{ collection.genre.substring(0, 2) }}</div>
        </div>
        <div class="collection-info">
          <h3>{{ collection.genre }}</h3>
          <p>{{ collection.tracks }} битов</p>
        </div>
      </div>
    </div>
  </section>

    <!-- Новые релизы -->
    <section class="section">
      <div class="section-header">
        <h2>Новые релизы</h2>
        <router-link to="/search?sort=newest" class="view-all"
          >Все новинки →</router-link
        >
      </div>
      <div class="track-grid">
        <TrackCard
          v-for="track in newReleases"
          :key="track.id"
          :track="track"
          is-new
          @image-error="handleImageError"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import TrackCard from '../components/TrackCard.vue';
import api from '../api';

const popularTracks = ref([]);
const newReleases = ref([]);
const genreCollections = ref([]);

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Маппинг жанров на красивые обложки (fallback, если image_url не задан)
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

/**
 * Формирует полный URL обложки жанра:
 * - если есть image_url – используем его (поддерживаем абсолютные и относительные пути)
 * - иначе fallback по названию из genreCoverMap
 * - иначе дефолтная картинка
 */
const getGenreImageUrl = (genre) => {
  // Приоритет: image_url с бэкенда
  if (genre.image_url) {
    if (genre.image_url.startsWith('http')) {
      return genre.image_url;
    }
    return `${BASE_URL}${genre.image_url}`;
  }
  // Fallback по названию
  const key = genre.name?.toLowerCase() || '';
  return genreCoverMap[key] || DEFAULT_GENRE_COVER;
};

// Обработчик ошибки загрузки изображения жанра
const handleGenreImageError = (collection) => {
  collection.cover = DEFAULT_GENRE_COVER;
};

// Обработчик ошибок для треков
const handleImageError = (event) => {
  event.target.src = 'https://via.placeholder.com/300x300?text=No+Image';
};

const fetchPopular = async () => {
  try {
    const { data } = await api.get('/tracks/popular?limit=4');
    popularTracks.value = data;
  } catch (error) {
    console.error('Ошибка загрузки популярных треков:', error);
  }
};

const fetchNew = async () => {
  try {
    const { data } = await api.get('/tracks/new?limit=4');
    newReleases.value = data;
  } catch (error) {
    console.error('Ошибка загрузки новых треков:', error);
  }
};

const fetchGenres = async () => {
  try {
    const { data } = await api.get('/genres');
    // Берём первые 4 жанра и преобразуем в формат коллекций
    genreCollections.value = data.slice(0, 4).map(g => ({
      id: g.id,
      genre: g.name,
      cover: getGenreImageUrl(g),   // ← теперь используется image_url (если есть)
      tracks: g.tracks_count || 0
    }));
  } catch (error) {
    console.error('Ошибка загрузки жанров:', error);
    // Fallback: демо-данные (на случай, если API не отвечает)
    const fallbackGenres = [
      { id: 1, name: 'Hip-Hop', image_url: null },
      { id: 2, name: 'Electronic', image_url: null },
      { id: 3, name: 'Lo-Fi', image_url: null },
      { id: 4, name: 'Trap', image_url: null }
    ];
    genreCollections.value = fallbackGenres.map(g => ({
      id: g.id,
      genre: g.name,
      cover: getGenreImageUrl(g),
      tracks: Math.floor(Math.random() * 200) + 20
    }));
  }
};

onMounted(() => {
  fetchPopular();
  fetchNew();
  fetchGenres();
});
</script>


<style scoped>
/* Глобальные переменные (можно вынести в отдельный файл) */
:root {
  --bg-primary: #0a0a0f;
  --bg-secondary: #14141f;
  --accent: #a855f7;
  --accent-glow: rgba(168, 85, 247, 0.4);
  --text-primary: #ffffff;
  --text-secondary: #a0a0b0;
  --card-bg: rgba(255, 255, 255, 0.02);
  --border-color: rgba(255, 255, 255, 0.05);
}

.home {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

/* Hero секция */
.hero {
  position: relative;
  text-align: center;
  padding: 6rem 2rem;
  border-radius: 40px;
  margin-bottom: 4rem;
  background: radial-gradient(
      circle at 30% 40%,
      rgba(168, 85, 247, 0.3) 0%,
      transparent 60%
    ),
    radial-gradient(
      circle at 70% 60%,
      rgba(59, 130, 246, 0.3) 0%,
      transparent 60%
    ),
    #0a0a0f;
  overflow: hidden;
  isolation: isolate;
}

.hero-content {
  position: relative;
  z-index: 2;
}

.hero h1 {
  font-size: 4rem;
  font-weight: 800;
  background: linear-gradient(135deg, #fff, #e0b0ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 1rem;
  line-height: 1.2;
  text-shadow: 0 0 30px rgba(168, 85, 247, 0.5);
}

.hero p {
  font-size: 1.2rem;
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto 2rem;
}

.cta-btn {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border: none;
  color: white;
  padding: 1rem 3rem;
  font-size: 1.2rem;
  font-weight: 600;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 5px 20px rgba(168, 85, 247, 0.4);
}

.cta-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 15px 30px rgba(168, 85, 247, 0.6);
}

.pulse {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 var(--accent-glow);
  }
  70% {
    box-shadow: 0 0 0 15px rgba(168, 85, 247, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(168, 85, 247, 0);
  }
}

.hero-wave {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100px;
  background: url('data:image/svg+xml;utf8,<svg viewBox="0 0 1200 120" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none"><path d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" opacity=".25" fill="%23a855f7"></path><path d="M0,0V15.81C13,21.25,27.93,25.67,44.24,28.45c69.76,11.53,139.59-6.72,208.56-3.11,55.62,2.91,110.37,14.68,166.48,17.38,107.68,5.18,215.73-19.42,323.17-5.49,47.49,6.15,92.74,19.89,138.86,28.93,27.68,5.42,55.55,9.19,83.69,9.19,0,0,0-46.29,0-46.29Z" opacity=".5" fill="%233b82f6"></path></svg>');
  background-size: cover;
  background-repeat: no-repeat;
  z-index: 1;
}

/* Заголовки секций */
.section {
  margin-bottom: 4rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.section-header h2 {
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #fff, #a0a0b0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.view-all {
  color: var(--accent);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
}

.view-all:hover {
  color: #c084fc;
  transform: translateX(3px);
}

/* Сетка треков */
.track-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 2rem;
}

/* Коллекции (винил) */
.genre-collections {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 2rem;
}

.collection-card {
  cursor: pointer;
  transition: transform 0.3s;
  text-align: center;
}

.collection-card:hover {
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

.collection-card:hover .vinyl-record {
  transform: rotate(20deg);
}

.collection-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  border: 3px solid var(--accent);
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

.collection-info {
  margin-top: 1rem;
}

.collection-info h3 {
  font-size: 1.2rem;
  margin-bottom: 0.2rem;
}

.collection-info p {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* Адаптивность */
@media (max-width: 768px) {
  .hero h1 {
    font-size: 2.5rem;
  }
  .track-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
  }
  .genre-collections {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
  }
}
</style>
