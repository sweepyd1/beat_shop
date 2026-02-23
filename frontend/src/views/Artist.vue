<template>
  <div class="artist-profile">
    <!-- Шапка профиля -->
    <div class="artist-header">
      <img
        :src="artist.avatar"
        :alt="artist.name"
        class="avatar"
        @error="handleImageError"
      />
      <div class="artist-info">
        <h1>{{ artist.name }}</h1>
        <p class="bio">{{ artist.bio }}</p>
        <div class="stats">
          <div class="stat-item">
            <span class="stat-value">{{ artist.followers }}</span>
            <span class="stat-label">подписчиков</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ artist.totalEarnings }} ₽</span>
            <span class="stat-label">выручка</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ artist.tracks.length }}</span>
            <span class="stat-label">битов</span>
          </div>
        </div>
        <button class="follow-btn" @click="toggleFollow">
          {{ isFollowed ? "Отписаться" : "Подписаться" }}
        </button>
      </div>
    </div>

    <!-- Статистика продаж -->
    <div class="sales-stats">
      <h2>Статистика продаж</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <i class="fas fa-chart-line"></i>
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
    </div>

    <!-- Список битов -->
    <div class="beats-section">
      <h2>Биты артиста</h2>
      <div class="beats-grid">
        <div v-for="beat in artist.tracks" :key="beat.id" class="beat-card">
          <img
            :src="beat.cover"
            :alt="beat.title"
            class="beat-cover"
            @error="handleImageError"
          />
          <div class="beat-info">
            <h3>{{ beat.title }}</h3>
            <p class="beat-price">{{ beat.price }} ₽</p>
            <button class="play-btn" @click="playTrack(beat)">
              <i class="fas fa-play"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from "vue";

const { playTrack } = inject("player");

const isFollowed = ref(false);

const toggleFollow = () => {
  isFollowed.value = !isFollowed.value;
};

// Встроенная заглушка (data:image/svg+xml)
const placeholderSVG =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200' viewBox='0 0 24 24' fill='%23cccccc'%3E%3Cpath d='M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z'/%3E%3C/svg%3E";

const handleImageError = (e) => {
  e.target.src = placeholderSVG;
};

// Мок-данные артиста (продавца)
const artist = ref({
  id: 1,
  name: "Arctica Beats",
  avatar: "https://picsum.photos/200/200?random=101",
  bio: "Профессиональный битмейкер. Создаю треки в жанрах trap, drill, lo-fi. Более 5 лет опыта, сотрудничаю с лейблами.",
  followers: 15400,
  totalEarnings: 1520000,
  tracks: [
    {
      id: 1,
      title: "Neon Dreams",
      price: 1500,
      cover: "https://picsum.photos/200/200?random=1",
      audioSrc: "",
    },
    {
      id: 2,
      title: "Dark Alley",
      price: 2000,
      cover: "https://picsum.photos/200/200?random=2",
      audioSrc: "",
    },
    {
      id: 3,
      title: "Sunset Vibes",
      price: 1200,
      cover: "https://picsum.photos/200/200?random=3",
      audioSrc: "",
    },
    {
      id: 4,
      title: "Moscow Nights",
      price: 1800,
      cover: "https://picsum.photos/200/200?random=4",
      audioSrc: "",
    },
  ],
  salesThisMonth: 42,
  monthlyEarnings: 89000,
  averageRating: 4.8,
});
</script>

<style scoped>
.artist-profile {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
}

.artist-header {
  display: flex;
  gap: 3rem;
  margin-bottom: 3rem;
  align-items: center;
  background: rgba(255, 255, 255, 0.02);
  padding: 2rem;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.avatar {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid rgba(168, 85, 247, 0.3);
  background-color: #2a2a35;
}

.artist-info h1 {
  font-size: 2.5rem;
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
  font-size: 2rem;
  font-weight: 700;
  color: #fff;
}

.stat-label {
  font-size: 0.9rem;
  color: #a0a0b0;
}

.follow-btn {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border: none;
  color: white;
  padding: 0.8rem 2.5rem;
  border-radius: 30px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.follow-btn:hover {
  transform: scale(1.05);
}

.sales-stats {
  margin-bottom: 3rem;
}

.sales-stats h2 {
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.03);
  padding: 1.5rem;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
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

.beats-section h2 {
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
}

.beats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 2rem;
}

.beat-card {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 16px;
  overflow: hidden;
  transition: transform 0.2s;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.beat-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.04);
}

.beat-cover {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  background-color: #2a2a35;
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

.beat-price {
  color: #a855f7;
  font-weight: 600;
  font-size: 0.9rem;
}

.play-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 1.2rem;
  cursor: pointer;
  width: 35px;
  height: 35px;
  border-radius: 50%;
  background: rgba(168, 85, 247, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.play-btn:hover {
  background: #a855f7;
}

@media (max-width: 768px) {
  .artist-header {
    flex-direction: column;
    text-align: center;
  }

  .stats {
    justify-content: center;
  }

  .beats-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
  }
}
</style>
