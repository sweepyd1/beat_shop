<!-- Файл: Artist.vue (обновлённый) -->
<template>
  <div class="artist-profile">
    <div v-if="loading" class="loading-state">
      <i class="fas fa-spinner fa-spin"></i>
      <p>Загрузка профиля автора...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{{ error }}</p>
      <router-link to="/" class="btn-primary">На главную</router-link>
    </div>

    <div v-else class="artist-content">
      <div class="artist-header">
        <div class="avatar-wrapper">
          <img
            :src="avatarUrl || '/default-avatar.png'"
            :alt="artist.full_name"
            class="avatar"
            @error="handleImageError"
          />
          <div class="avatar-ring"></div>
        </div>
        <div class="artist-info">
          <h1>{{ artist.full_name }}</h1>
          <p class="bio">{{ artist.bio || "Биография не указана" }}</p>
          <div class="stats">
            <div class="stat-item">
              <span class="stat-value">{{ artist.tracks_count || 0 }}</span>
              <span class="stat-label">битов</span>
            </div>
          </div>
          <!-- <button 
            v-if="isLoggedIn && !isOwnProfile" 
            class="follow-btn" 
            :class="{ followed: isFollowed }" 
            @click="toggleFollow"
          >
            <i :class="isFollowed ? 'fas fa-check' : 'fas fa-plus'"></i>
            {{ isFollowed ? "Отписаться" : "Подписаться" }}
          </button> -->
          <router-link
            v-if="isOwnProfile"
            to="/profile?tab=studio"
            class="btn-primary"
          >
            <i class="fas fa-cog"></i> Управление профилем
          </router-link>
        </div>
      </div>

      <!-- Биты артиста -->
      <div class="beats-section">
        <h2><i class="fas fa-headphones"></i> Биты артиста</h2>
        <div v-if="!tracks || tracks.length === 0" class="empty-state">
          <i class="fas fa-music empty-icon"></i>
          <p>У этого автора ещё нет треков</p>
        </div>
        <div v-else class="beats-grid">
          <TrackCard v-for="track in tracks" :key="track.id" :track="track" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "../stores/auth";
import TrackCard from "../components/TrackCard.vue";
import api from "../api";

const route = useRoute();
const authStore = useAuthStore();
const { playTrack } = inject("player", {
  playTrack: (t) => console.log("play", t),
});

const loading = ref(true);
const error = ref(null);
const artist = ref(null);
const artistStats = ref(null);
const tracks = ref([]);
const isFollowed = ref(false);
const isLoggedIn = computed(() => !!authStore.user);
const currentUserId = computed(() => authStore.user?.id);
const isOwnProfile = computed(() => {
  if (!artist.value || !currentUserId.value) return false;
  return artist.value.user_id === currentUserId.value;
});
const avatarUrl = computed(() => {
  if (!artist.value?.photo_url) return "/default-avatar.png";
  let url;
  if (artist.value.photo_url.startsWith("http")) {
    url = artist.value.photo_url;
  } else {
    const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
    // нормализуем baseUrl (убираем завершающий слеш)
    const normalizedBase = baseUrl.endsWith("/")
      ? baseUrl.slice(0, -1)
      : baseUrl;
    // добавляем слеш к path, если его нет
    const path = artist.value.photo_url.startsWith("/")
      ? artist.value.photo_url
      : "/" + artist.value.photo_url;
    url = normalizedBase + path;
  }
  console.log("Final avatar URL:", url);
  console.log(1);
  return url;
});
const formatNumber = (num) => {
  return new Intl.NumberFormat("ru-RU").format(num);
};

const handleImageError = (e) => {
  const placeholderSVG =
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200' viewBox='0 0 24 24' fill='%23cccccc'%3E%3Cpath d='M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z'/%3E%3C/svg%3E";
  e.target.src = placeholderSVG;
};

const salesChart = ref([40, 60, 30, 80, 50, 70, 90]);

const toggleFollow = async () => {
  if (!isLoggedIn.value) {
    alert("Пожалуйста, войдите чтобы подписаться");
    return;
  }
  try {
    if (isFollowed.value) {
      await api.delete(`/authors/${artist.value.id}/subscribe`);
    } else {
      await api.post(`/authors/${artist.value.id}/subscribe`);
    }
    isFollowed.value = !isFollowed.value;
  } catch (err) {
    console.error("Ошибка подписки:", err);
    showError("Ошибка при изменении подписки");
  }
};

const fetchArtistData = async () => {
  loading.value = true;
  error.value = null;

  try {
    const authorId = route.params.id;
    const response = await api.get(`/authors/${authorId}`);
    artist.value = response.data;
    tracks.value = response.data.tracks || [];
    artistStats.value = response.data;
    console.log("Full response:", response.data);
    console.log("photo_url:", response.data.photo_url);

    // Генерируем случайные данные для графика
    salesChart.value = Array.from(
      { length: 7 },
      () => Math.floor(Math.random() * 80) + 20
    );
  } catch (err) {
    console.error("Ошибка загрузки данных автора:", err);
    error.value =
      err.response?.data?.detail || "Ошибка загрузки профиля автора";
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchArtistData();
});
</script>

<style scoped>
.artist-profile {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.artist-header {
  display: flex;
  gap: 3rem;
  margin-bottom: 3rem;
  align-items: center;
  background: linear-gradient(
    145deg,
    rgba(168, 85, 247, 0.1),
    rgba(59, 130, 246, 0.05)
  );
  padding: 2rem;
  border-radius: 40px;
  border: 1px solid rgba(168, 85, 247, 0.2);
  backdrop-filter: blur(10px);
}

.avatar-wrapper {
  position: relative;
  width: 200px;
  height: 200px;
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
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.artist-info {
  flex: 1;
}

.artist-info h1 {
  font-size: 2.8rem;
  background: linear-gradient(135deg, #fff, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}

.bio {
  color: #a0a0b0;
  line-height: 1.6;
  margin-bottom: 1.5rem;
  max-width: 600px;
}

.stats {
  display: flex;
  gap: 3rem;
  margin-bottom: 2rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 2.2rem;
  font-weight: 700;
  color: #fff;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.9rem;
  color: #a0a0b0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.follow-btn {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border: none;
  color: white;
  padding: 0.8rem 2.5rem;
  border-radius: 30px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.follow-btn.followed {
  background: #2a2a35;
  border: 1px solid #a855f7;
}

.follow-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 10px 20px rgba(168, 85, 247, 0.3);
}

.sales-stats {
  margin-bottom: 3rem;
}

.sales-stats h2 {
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.03);
  padding: 1.5rem;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-3px);
  border-color: #a855f7;
}

.stat-card i {
  font-size: 2.5rem;
  color: #a855f7;
}

.stat-card-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
}

.stat-card-label {
  font-size: 0.9rem;
  color: #a0a0b0;
}

.mini-chart {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
  height: 100px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 20px;
  padding: 1rem;
}

.mini-chart .bar {
  flex: 1;
  background: linear-gradient(to top, #a855f7, #3b82f6);
  border-radius: 5px 5px 0 0;
  transition: height 0.3s;
}

.beats-section h2 {
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.beats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 2rem;
}

.beat-card {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s;
  border: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
}

.beat-card:hover {
  transform: translateY(-8px);
  border-color: #a855f7;
  box-shadow: 0 20px 30px rgba(168, 85, 247, 0.2);
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
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  opacity: 0;
  transition: opacity 0.3s;
}

.beat-card:hover .beat-overlay {
  opacity: 1;
}

.play-btn,
.like-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: none;
  background: #a855f7;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  transition: transform 0.2s;
}

.like-btn {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(5px);
}

.play-btn:hover,
.like-btn:hover {
  transform: scale(1.1);
}

.beat-info {
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.beat-info h3 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.2rem;
}

.beat-meta {
  font-size: 0.8rem;
  color: #a0a0b0;
}

.beat-price {
  color: #a855f7;
  font-weight: 700;
  font-size: 1.2rem;
}

/* Loading and error states */
.loading-state,
.error-state {
  text-align: center;
  padding: 4rem 2rem;
}

.loading-state i,
.error-state i {
  font-size: 3rem;
  color: #a855f7;
  margin-bottom: 1rem;
}

.loading-state p,
.error-state p {
  color: #a0a0b0;
  font-size: 1.1rem;
}

.error-state i {
  color: #ef4444;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #a0a0b0;
}

.empty-state .empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #a855f7;
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
