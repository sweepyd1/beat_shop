<template>
  <div class="track-detail" v-if="track">
    <div class="track-detail-container">
      
      <div class="track-cover-section">
        <div class="cover-large">
          <img :src="coverUrl" alt="cover" @error="handleImageError" />
          <div class="play-button-large" @click="playTrack(track)">
            <i class="fas fa-play"></i>
          </div>
        </div>
        <div class="track-stats">
          <div class="stat">
            <i class="fas fa-headphones"></i>
            <span>{{ track.plays || 0 }} прослушиваний</span>
          </div>
          <div class="stat">
            <i class="fas fa-calendar-alt"></i>
            <span>{{ formatDate(track.added_date) }}</span>
          </div>
        </div>
      </div>

      
      <div class="track-info-section">
        <h1>{{ track.title }}</h1>
        <div class="author">
          <router-link :to="`/artist/${track.author?.id || track.author_id}`" class="author-link">
            {{ track.author?.full_name || 'Неизвестный автор' }}
          </router-link>
        </div>

        <div class="track-meta">
          <div class="meta-item">
            <i class="fas fa-tag"></i>
            <span>{{ track.genre?.name || 'Без жанра' }}</span>
          </div>
          <div class="meta-item">
            <i class="fas fa-clock"></i>
            <span>{{ formatDuration(track.duration_seconds) }}</span>
          </div>
          <div class="meta-item" v-if="track.bpm">
            <i class="fas fa-waveform"></i>
            <span>{{ track.bpm }} BPM</span>
          </div>
        </div>

        <div class="price-section">
          <div class="price">{{ track.price }} ₽</div>
          <button class="buy-btn" @click="openPurchaseModal">
            <i class="fas fa-shopping-cart"></i> Купить бит
          </button>
        </div>

        <div class="track-description" v-if="track.description">
          <h3>Описание</h3>
          <p>{{ track.description }}</p>
        </div>

        <div class="license-info">
          <h3>Лицензия</h3>
          <p>При покупке вы получаете лицензию на использование бита в коммерческих целях. Договор оформляется автоматически.</p>
        </div>
      </div>
    </div>

    
    <PurchaseModal
      v-model="showPurchaseModal"
      :track="track"
      @purchase-complete="handlePurchaseComplete"
    />
  </div>

  <div v-else class="loading">
    <div class="spinner"></div>
    <p>Загрузка информации о треке...</p>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, inject } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../api';
import { useAuthStore } from '../stores/auth';  
import { showError, showSuccess } from '@/utils/alert';  

import PurchaseModal from '../components/PurchaseModal.vue';

const route = useRoute();
const router = useRouter();
const track = ref(null);
const showPurchaseModal = ref(false);
const { playTrack } = inject('player');
const authStore = useAuthStore();
const coverUrl = computed(() => {
  if (!track.value) return '';
  const url = track.value.cover_url;
  if (!url) return '/default-cover.jpg';
  if (url.startsWith('http')) return url;
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  return `${baseUrl}${url}`;
});

const fetchTrack = async () => {
  try {
    const { data } = await api.get(`/tracks/${route.params.id}`);
    track.value = data;
  } catch (error) {
    console.error('Ошибка загрузки трека:', error);
    
    router.push('/404');
  }
};

const formatDuration = (seconds) => {
  if (!seconds) return '0:00';
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('ru-RU');
};

const openPurchaseModal = () => {
  if (!authStore.user) {
    router.push({ path: '/login', query: { redirect: route.fullPath } });
    return;
  }
  showPurchaseModal.value = true;
};
const handlePurchaseComplete = (purchaseData) => {
  
  showSuccess(`Покупка успешно оформлена! Договор можно получить в личном кабинете`);
  showPurchaseModal.value = false;
};

const handleImageError = (e) => {
  e.target.src = '/default-cover.jpg';
};

onMounted(() => {
  fetchTrack();
});
</script>

<style scoped>
.track-detail {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 2rem;
  background: var(--bg-secondary);
  border-radius: 32px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.track-detail-container {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 2rem;
}


.track-cover-section {
  position: sticky;
  top: 2rem;
}

.cover-large {
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  margin-bottom: 1.5rem;
}

.cover-large img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  display: block;
}

.play-button-large {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  width: 60px;
  height: 60px;
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  transition: transform 0.2s;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.play-button-large:hover {
  transform: scale(1.05);
}

.track-stats {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.stat i {
  font-size: 1.2rem;
}


.track-info-section h1 {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #fff, #e0b0ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}

.author {
  margin-bottom: 1rem;
}

.author-link {
  color: var(--accent);
  text-decoration: none;
  font-size: 1.2rem;
  font-weight: 500;
  transition: color 0.2s;
}

.author-link:hover {
  color: #c084fc;
  text-decoration: underline;
}

.track-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin: 1.5rem 0;
  padding: 1rem 0;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
}

.meta-item i {
  width: 1.2rem;
}

.price-section {
  margin: 2rem 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(168, 85, 247, 0.1);
  padding: 1rem 1.5rem;
  border-radius: 60px;
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.price {
  font-size: 2rem;
  font-weight: 700;
  color: var(--accent);
}

.buy-btn {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border: none;
  padding: 0.8rem 2rem;
  border-radius: 40px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.buy-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(168, 85, 247, 0.4);
}

.track-description, .license-info {
  margin-top: 2rem;
}

.track-description h3, .license-info h3 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.track-description p, .license-info p {
  color: var(--text-secondary);
  line-height: 1.5;
}

.loading {
  text-align: center;
  padding: 4rem;
}

.spinner {
  border: 4px solid rgba(168, 85, 247, 0.1);
  border-top: 4px solid var(--accent);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .track-detail-container {
    grid-template-columns: 1fr;
  }
  .track-cover-section {
    position: static;
  }
  .price-section {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
}
</style>