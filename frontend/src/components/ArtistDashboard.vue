<!-- components/ArtistDashboard.vue -->
<template>
  <div class="artist-dashboard">
    <div class="artist-header">
      <div class="avatar-wrapper">
        <img :src="authorAvatar" alt="avatar" class="avatar" @error="handleImageError" />
        <div class="avatar-ring"></div>
      </div>
      <div class="artist-info">
        <h1>{{ author.full_name }}</h1>
        <p class="bio">{{ author.bio || 'Автор не заполнил биографию' }}</p>
        <div class="stats">
          <div class="stat-item">
            <span class="stat-value">{{ formatNumber(author.followers_count || 0) }}</span>
            <span class="stat-label">подписчиков</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ formatNumber(author.total_earnings || 0) }} ₽</span>
            <span class="stat-label">выручка</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ author.tracks_count || 0 }}</span>
            <span class="stat-label">битов</span>
          </div>
        </div>
      </div>
    </div>

    <div class="sales-stats">
      <h2><i class="fas fa-chart-line"></i> Статистика продаж</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <i class="fas fa-shopping-cart"></i>
          <div>
            <span class="stat-card-value">{{ stats.sales_this_month || 0 }}</span>
            <span class="stat-card-label">продаж в этом месяце</span>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-wallet"></i>
          <div>
            <span class="stat-card-value">{{ stats.monthly_earnings || 0 }} ₽</span>
            <span class="stat-card-label">доход за месяц</span>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-star"></i>
          <div>
            <span class="stat-card-value">{{ stats.average_rating || 0 }}</span>
            <span class="stat-card-label">средний рейтинг</span>
          </div>
        </div>
      </div>
     
    </div>

    <div class="beats-section">
      
      <div class="beats-grid">
        <div v-for="beat in tracks" :key="beat.id" class="beat-card">
          <img :src="beat.cover_url" :alt="beat.title" class="beat-cover" @error="handleImageError" />
          <div class="beat-overlay">
            <button class="play-btn" @click="playTrack(beat)"><i class="fas fa-play"></i></button>
            <button class="like-btn" @click="toggleFavorite(beat.id)"><i class="far fa-heart"></i></button>
          </div>
          <div class="beat-info">
            <div>
              <h3>{{ beat.title }}</h3>
              <p class="beat-meta">{{ beat.plays || 0 }} прослушиваний · {{ beat.sales || 0 }} продаж</p>
            </div>
            <p class="beat-price">{{ beat.price }} ₽</p>
          </div>
        </div>
      </div>
    </div>

    <div class="upload-link">
      <router-link to="/profile?tab=upload" class="upload-trigger">
        <i class="fas fa-plus-circle"></i> Загрузить новый бит
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue';
import api from '../api';

const { playTrack } = inject('player', { playTrack: (t) => console.log('play', t) });

const author = ref({});
const tracks = ref([]);
const stats = ref({});
const salesChart = ref([40, 60, 30, 80, 50, 70, 90]);

const authorAvatar = computed(() => {
  if (!author.value.photo_url) return '/default-avatar.png';
  if (author.value.photo_url.startsWith('http')) return author.value.photo_url;
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  return `${baseUrl}${author.value.photo_url}`;
});

const formatNumber = (num) => {
  return new Intl.NumberFormat('ru-RU').format(num);
};

const fetchAuthorData = async () => {
  try {
    const { data: authorData } = await api.get('/authors/me');
    author.value = authorData;
    const { data: tracksData } = await api.get('/authors/me/tracks');
    tracks.value = tracksData;
    const { data: statsData } = await api.get('/authors/me/stats');
    stats.value = statsData;
    if (statsData.sales_chart) salesChart.value = statsData.sales_chart;
  } catch (err) {
    console.error('Ошибка загрузки данных автора', err);
  }
};

const handleImageError = (e) => {
  e.target.src = '/default-cover.jpg';
};

const toggleFavorite = (trackId) => {
  console.log('toggle favorite', trackId);
  // можно реализовать вызов API
};

onMounted(() => {
  fetchAuthorData();
});
</script>

<style scoped>
.artist-dashboard {
  max-width: 100%;
  margin: 0 auto;
}

.artist-header {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  align-items: center;
  background: linear-gradient(145deg, rgba(168,85,247,0.1), rgba(59,130,246,0.05));
  padding: 1.5rem;
  border-radius: 40px;
  border: 1px solid rgba(168,85,247,0.2);
  backdrop-filter: blur(10px);
}

.avatar-wrapper {
  position: relative;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  overflow: hidden;
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: relative;
  z-index: 2;
}

.avatar-ring {
  position: absolute;
  top: -5px;
  left: -5px;
  right: -5px;
  bottom: -5px;
  border-radius: 50%;
  background: linear-gradient(45deg, #a855f7, #3b82f6, #a855f7);
  animation: rotate 4s linear infinite;
  z-index: 1;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.artist-info {
  flex: 1;
}

.artist-info h1 {
  font-size: 2rem;
  background: linear-gradient(135deg, #fff, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}

.bio {
  color: #a0a0b0;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.stats {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #fff;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.8rem;
  color: #a0a0b0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sales-stats {
  margin-bottom: 2rem;
}

.sales-stats h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-card {
  background: rgba(255,255,255,0.03);
  padding: 1rem;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  border: 1px solid rgba(255,255,255,0.05);
}

.stat-card i {
  font-size: 2rem;
  color: #a855f7;
}

.stat-card-value {
  display: block;
  font-size: 1.2rem;
  font-weight: 700;
}

.stat-card-label {
  font-size: 0.8rem;
  color: #a0a0b0;
}

.mini-chart {
  display: flex;
  align-items: flex-end;
  gap: 0.3rem;
  height: 80px;
  background: rgba(0,0,0,0.2);
  border-radius: 12px;
  padding: 0.8rem;
}

.mini-chart .bar {
  flex: 1;
  background: linear-gradient(to top, #a855f7, #3b82f6);
  border-radius: 4px 4px 0 0;
  transition: height 0.3s;
}

.beats-section h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.beats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1rem;
}

.beat-card {
  background: rgba(255,255,255,0.02);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s;
  border: 1px solid rgba(255,255,255,0.05);
  position: relative;
}

.beat-card:hover {
  transform: translateY(-5px);
  border-color: #a855f7;
  box-shadow: 0 10px 20px rgba(168,85,247,0.2);
}

.beat-cover {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
}

.beat-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.8rem;
  opacity: 0;
  transition: opacity 0.3s;
}

.beat-card:hover .beat-overlay {
  opacity: 1;
}

.play-btn, .like-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: #a855f7;
  color: white;
  font-size: 1rem;
  cursor: pointer;
  transition: transform 0.2s;
}

.like-btn {
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(5px);
}

.play-btn:hover, .like-btn:hover {
  transform: scale(1.1);
}

.beat-info {
  padding: 0.8rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.beat-info h3 {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.2rem;
}

.beat-meta {
  font-size: 0.7rem;
  color: #a0a0b0;
}

.beat-price {
  color: #a855f7;
  font-weight: 700;
  font-size: 1rem;
}

.upload-link {
  text-align: center;
  margin-top: 2rem;
}

.upload-trigger {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  color: white;
  padding: 0.6rem 1.5rem;
  border-radius: 40px;
  text-decoration: none;
  font-weight: 600;
  transition: transform 0.2s;
}

.upload-trigger:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(168,85,247,0.4);
}

@media (max-width: 768px) {
  .artist-header {
    flex-direction: column;
    text-align: center;
  }
  .stats {
    justify-content: center;
  }
}
</style>