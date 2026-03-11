<!-- Файл: Home.vue (обновлённый) -->
<template>
  <div class="home">
    <!-- Hero-секция с анимированным градиентом -->
    <section class="hero">
      <div class="hero-content">
        <h1>Покупай биты напрямую у авторов</h1>
        <p>Тысячи эксклюзивных битов в разных жанрах. Лицензии без скрытых платежей.</p>
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
        <router-link to="/search?sort=popular" class="view-all">Все →</router-link>
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
        <router-link to="/search" class="view-all">Все жанры →</router-link>
      </div>
      <div class="genre-collections">
        <div
          v-for="collection in genreCollections"
          :key="collection.id"
          class="collection-card vinyl"
          @click="$router.push(`/collection/${collection.id}`)"
        >
          <div class="vinyl-record">
            <img
              :src="collection.cover"
              :alt="collection.genre"
              class="collection-cover"
              @error="handleImageError"
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
        <router-link to="/search?sort=newest" class="view-all">Все новинки →</router-link>
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

const fetchPopular = async () => {
  const { data } = await api.get('/tracks/popular?limit=4');
  popularTracks.value = data;
};

const fetchNew = async () => {
  const { data } = await api.get('/tracks/new?limit=4');
  newReleases.value = data;
};

const fetchGenres = async () => {
  const { data } = await api.get('/genres');
  // Преобразуем в формат коллекций (можно взять первые 4 жанра с картинками)
  genreCollections.value = data.slice(0, 4).map(g => ({
    id: g.id,
    genre: g.name,
    cover: `https://picsum.photos/300/300?random=${g.id}`, // временно, позже можно добавить поле обложки жанра
    tracks: g.tracks_count
  }));
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
  background: radial-gradient(circle at 30% 40%, rgba(168, 85, 247, 0.3) 0%, transparent 60%),
              radial-gradient(circle at 70% 60%, rgba(59, 130, 246, 0.3) 0%, transparent 60%),
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
  0% { box-shadow: 0 0 0 0 var(--accent-glow); }
  70% { box-shadow: 0 0 0 15px rgba(168, 85, 247, 0); }
  100% { box-shadow: 0 0 0 0 rgba(168, 85, 247, 0); }
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
  .hero h1 { font-size: 2.5rem; }
  .track-grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 1rem; }
  .genre-collections { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 1rem; }
}
</style>