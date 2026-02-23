<!-- Файл: Artist.vue (обновлённый) -->
<template>
  <div class="artist-profile">
    <div class="artist-header">
      <div class="avatar-wrapper">
        <img
          :src="artist.avatar"
          :alt="artist.name"
          class="avatar"
          @error="handleImageError"
        />
        <div class="avatar-ring"></div>
      </div>
      <div class="artist-info">
        <h1>{{ artist.name }}</h1>
        <p class="bio">{{ artist.bio }}</p>
        <div class="stats">
          <div class="stat-item">
            <span class="stat-value" ref="followersRef">{{ formatNumber(artist.followers) }}</span>
            <span class="stat-label">подписчиков</span>
          </div>
          <div class="stat-item">
            <span class="stat-value" ref="earningsRef">{{ formatNumber(artist.totalEarnings) }} ₽</span>
            <span class="stat-label">выручка</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ artist.tracks.length }}</span>
            <span class="stat-label">битов</span>
          </div>
        </div>
        <button class="follow-btn" :class="{ followed: isFollowed }" @click="toggleFollow">
          <i :class="isFollowed ? 'fas fa-check' : 'fas fa-plus'"></i>
          {{ isFollowed ? "Отписаться" : "Подписаться" }}
        </button>
      </div>
    </div>

    <!-- Статистика продаж с мини-графиком -->
    <div class="sales-stats">
      <h2><i class="fas fa-chart-line"></i> Статистика продаж</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <i class="fas fa-shopping-cart"></i>
          <div>
            <span class="stat-card-value">{{ artist.salesThisMonth }}</span>
            <span class="stat-card-label">продаж в этом месяце</span>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-wallet"></i>
          <div>
            <span class="stat-card-value">{{ artist.monthlyEarnings }} ₽</span>
            <span class="stat-card-label">доход за месяц</span>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-star"></i>
          <div>
            <span class="stat-card-value">{{ artist.averageRating }}</span>
            <span class="stat-card-label">средний рейтинг</span>
          </div>
        </div>
      </div>
      <!-- Мини-график продаж (эмуляция) -->
      <div class="mini-chart">
        <div class="bar" style="height: 40px;"></div>
        <div class="bar" style="height: 60px;"></div>
        <div class="bar" style="height: 30px;"></div>
        <div class="bar" style="height: 80px;"></div>
        <div class="bar" style="height: 50px;"></div>
        <div class="bar" style="height: 70px;"></div>
        <div class="bar" style="height: 90px;"></div>
      </div>
    </div>

    <!-- Биты артиста -->
    <div class="beats-section">
      <h2><i class="fas fa-headphones"></i> Биты артиста</h2>
      <div class="beats-grid">
        <div v-for="beat in artist.tracks" :key="beat.id" class="beat-card">
          <img
            :src="beat.cover"
            :alt="beat.title"
            class="beat-cover"
            @error="handleImageError"
          />
          <div class="beat-overlay">
            <button class="play-btn" @click="playTrack(beat)">
              <i class="fas fa-play"></i>
            </button>
            <button class="like-btn"><i class="far fa-heart"></i></button>
          </div>
          <div class="beat-info">
            <div>
              <h3>{{ beat.title }}</h3>
              <p class="beat-meta">{{ beat.plays || 2300 }}\) просмотров · {{ beat.sales || 128 }} продаж</p>
            </div>
            <p class="beat-price">{{ beat.price }} ₽</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, onMounted } from "vue";

const { playTrack } = inject("player", { playTrack: (t) => console.log("play", t) });

const isFollowed = ref(false);
const toggleFollow = () => {
  isFollowed.value = !isFollowed.value;
};

const formatNumber = (num) => {
  return new Intl.NumberFormat('ru-RU').format(num);
};

const placeholderSVG = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200' viewBox='0 0 24 24' fill='%23cccccc'%3E%3Cpath d='M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z'/%3E%3C/svg%3E";

const handleImageError = (e) => {
  e.target.src = placeholderSVG;
};

const artist = ref({
  id: 1,
  name: "Arctica Beats",
  avatar: "https://picsum.photos/400/400?random=101",
  bio: "Профессиональный битмейкер. Создаю треки в жанрах trap, drill, lo-fi. Более 5 лет опыта, сотрудничаю с лейблами. Резидент BeatStars.",
  followers: 15400,
  totalEarnings: 1520000,
  tracks: [
    { id: 1, title: "Neon Dreams", price: 1500, cover: "https://picsum.photos/200/200?random=1", plays: 12400, sales: 342 },
    { id: 2, title: "Dark Alley", price: 2000, cover: "https://picsum.photos/200/200?random=2", plays: 8700, sales: 215 },
    { id: 3, title: "Sunset Vibes", price: 1200, cover: "https://picsum.photos/200/200?random=3", plays: 5300, sales: 98 },
    { id: 4, title: "Moscow Nights", price: 1800, cover: "https://picsum.photos/200/200?random=4", plays: 3200, sales: 76 },
  ],
  salesThisMonth: 42,
  monthlyEarnings: 89000,
  averageRating: 4.8,
});

// Анимация счётчиков (простая)
onMounted(() => {
  // Здесь можно реализовать анимацию чисел, но для краткости оставим как есть
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
  background: linear-gradient(145deg, rgba(168,85,247,0.1), rgba(59,130,246,0.05));
  padding: 2rem;
  border-radius: 40px;
  border: 1px solid rgba(168,85,247,0.2);
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
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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
  box-shadow: 0 10px 20px rgba(168,85,247,0.3);
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
  background: rgba(255,255,255,0.03);
  padding: 1.5rem;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid rgba(255,255,255,0.05);
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
  background: rgba(0,0,0,0.2);
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
  background: rgba(255,255,255,0.02);
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s;
  border: 1px solid rgba(255,255,255,0.05);
  position: relative;
}

.beat-card:hover {
  transform: translateY(-8px);
  border-color: #a855f7;
  box-shadow: 0 20px 30px rgba(168,85,247,0.2);
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
  gap: 1rem;
  opacity: 0;
  transition: opacity 0.3s;
}

.beat-card:hover .beat-overlay {
  opacity: 1;
}

.play-btn, .like-btn {
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
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(5px);
}

.play-btn:hover, .like-btn:hover {
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

@media (max-width: 768px) {
  .artist-header { flex-direction: column; text-align: center; }
  .stats { justify-content: center; }
}
</style>