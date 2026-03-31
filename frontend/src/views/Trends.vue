<template>
  <div class="trends-page">
    <!-- Фоновый градиент и эффекты -->
    <div class="bg-glow"></div>
    <div class="bg-noise"></div>

    <div class="container">
      <!-- Хедер с анимацией -->
      <div class="header">
        <h1 class="title">
          <span class="fire-icon">🔥</span> Музыкальные тренды
          <span class="trend-badge">TOP 10</span>
        </h1>
        <p class="subtitle">Популярное прямо сейчас — обновляется ежедневно</p>
      </div>

      <!-- Период с премиум-переключателем -->
      <div class="period-wrapper">
        <div class="period-selector">
          <button
            v-for="p in periods"
            :key="p.value"
            :class="['period-btn', { active: period === p.value }]"
            @click="changePeriod(p.value)"
          >
            <span class="period-text">{{ p.label }}</span>
            <span class="period-glow"></span>
          </button>
        </div>
        <div class="update-info">
          <i class="fas fa-chart-line"></i>
          <span>Тренды за {{ currentPeriodLabel }}</span>
        </div>
      </div>

      <!-- Анимированный список -->
      <TransitionGroup name="trend-list" tag="div" class="trends-list">
        <div
          v-for="(track, index) in trends"
          :key="track.id"
          class="trend-card"
          :style="{ animationDelay: `${index * 0.03}s` }"
        >
          <!-- Ранговый индикатор с огоньком для топ-3 -->
          <div class="rank-badge" :class="getRankClass(index)">
            <span class="rank-number">{{ index + 1 }}</span>
            <span v-if="index < 3" class="crown-icon">👑</span>
          </div>

          <!-- Обложка с эффектом свечения -->
          <div class="cover-wrapper">
            <img :src="track.cover" :alt="track.title" class="track-cover" />
            <div class="cover-overlay">
              <button class="quick-play" @click="playTrack(track)">
                <i class="fas fa-play"></i>
              </button>
            </div>
          </div>

          <!-- Информация о треке -->
          <div class="track-info">
            <div class="track-title-wrapper">
              <h3 class="track-title">{{ track.title }}</h3>
              <span v-if="track.isHot" class="hot-badge">HOT</span>
            </div>
            <p class="track-artist">{{ track.artist }}</p>
          </div>

          <!-- Статистика с динамикой -->
          <div class="stats-wrapper">
            <div class="stat-item">
              <i class="fas fa-headphones stat-icon"></i>
              <div class="stat-data">
                <span class="stat-value">{{ formatNumber(track.plays) }}</span>
                <span class="stat-label">прослушиваний</span>
              </div>
              <div class="trend-indicator" :class="getTrendClass(track.playsTrend)">
                <i :class="getTrendIcon(track.playsTrend)"></i>
                <span>{{ track.playsTrend }}%</span>
              </div>
            </div>
            <div class="stat-item">
              <i class="fas fa-shopping-cart stat-icon"></i>
              <div class="stat-data">
                <span class="stat-value">{{ track.sales }}</span>
                <span class="stat-label">продаж</span>
              </div>
              <div class="trend-indicator" :class="getTrendClass(track.salesTrend)">
                <i :class="getTrendIcon(track.salesTrend)"></i>
                <span>{{ track.salesTrend }}%</span>
              </div>
            </div>
          </div>

          <!-- Премиум-кнопка действия -->
          <div class="action-buttons">
            <button class="btn-icon" @click="addToFavorites(track)" title="В избранное">
              <i class="far fa-heart"></i>
            </button>
            <button class="btn-icon" @click="buyTrack(track)" title="Купить">
              <i class="fas fa-shopping-bag"></i>
            </button>
            <button class="btn-primary" @click="playTrack(track)">
              <i class="fas fa-play"></i> Слушать
            </button>
          </div>
        </div>
      </TransitionGroup>

      <!-- Блок с дополнительной аналитикой (эффектный) -->
      <div class="analytics-card">
        <div class="analytics-header">
          <i class="fas fa-chart-simple"></i>
          <h3>Аналитика периода</h3>
        </div>
        <div class="analytics-grid">
          <div class="analytics-item">
            <span class="analytics-value">{{ totalPlays }}</span>
            <span class="analytics-label">всего прослушиваний</span>
          </div>
          <div class="analytics-item">
            <span class="analytics-value">{{ totalSales }}</span>
            <span class="analytics-label">продано треков</span>
          </div>
          <div class="analytics-item">
            <span class="analytics-value">{{ avgGrowth }}%</span>
            <span class="analytics-label">средний рост</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const period = ref('week');
const periods = [
  { value: 'day', label: 'За день' },
  { value: 'week', label: 'За неделю' },
  { value: 'month', label: 'За месяц' }
];

// Моковые данные для разных периодов (имитация реальных)
const mockData = {
  day: [
    { id: 1, title: 'Neon Dreams', artist: 'Arctica', cover: 'https://picsum.photos/id/29/200/200', plays: 3400, sales: 42, playsTrend: 12, salesTrend: 8, isHot: true },
    { id: 2, title: 'Drill Szn', artist: 'Glock Beats', cover: 'https://picsum.photos/id/30/200/200', plays: 2800, sales: 35, playsTrend: 25, salesTrend: 18, isHot: true },
    { id: 3, title: 'Lost in Space', artist: 'Cosmic', cover: 'https://picsum.photos/id/31/200/200', plays: 2100, sales: 28, playsTrend: 5, salesTrend: 2, isHot: false },
    { id: 4, title: 'Echoes', artist: 'The Waves', cover: 'https://picsum.photos/id/32/200/200', plays: 1500, sales: 19, playsTrend: -3, salesTrend: -1, isHot: false },
    { id: 5, title: 'Midnight', artist: 'Luna', cover: 'https://picsum.photos/id/33/200/200', plays: 1200, sales: 14, playsTrend: 7, salesTrend: 5, isHot: false },
  ],
  week: [
    { id: 1, title: 'Neon Dreams', artist: 'Arctica', cover: 'https://picsum.photos/id/29/200/200', plays: 12400, sales: 342, playsTrend: 18, salesTrend: 12, isHot: true },
    { id: 2, title: 'Lost in Space', artist: 'Cosmic', cover: 'https://picsum.photos/id/31/200/200', plays: 8700, sales: 215, playsTrend: 9, salesTrend: 6, isHot: true },
    { id: 3, title: 'Echoes', artist: 'The Waves', cover: 'https://picsum.photos/id/32/200/200', plays: 5300, sales: 98, playsTrend: 22, salesTrend: 15, isHot: false },
    { id: 4, title: 'Midnight', artist: 'Luna', cover: 'https://picsum.photos/id/33/200/200', plays: 3200, sales: 76, playsTrend: -5, salesTrend: -2, isHot: false },
    { id: 5, title: 'Drill Szn', artist: 'Glock Beats', cover: 'https://picsum.photos/id/30/200/200', plays: 2800, sales: 45, playsTrend: 45, salesTrend: 30, isHot: true },
    { id: 6, title: 'Lofi Dreams', artist: 'Sleepy', cover: 'https://picsum.photos/id/34/200/200', plays: 1500, sales: 23, playsTrend: 3, salesTrend: 1, isHot: false },
  ],
  month: [
    { id: 1, title: 'Neon Dreams', artist: 'Arctica', cover: 'https://picsum.photos/id/29/200/200', plays: 45600, sales: 1250, playsTrend: 32, salesTrend: 28, isHot: true },
    { id: 2, title: 'Lost in Space', artist: 'Cosmic', cover: 'https://picsum.photos/id/31/200/200', plays: 32100, sales: 890, playsTrend: 24, salesTrend: 19, isHot: true },
    { id: 3, title: 'Echoes', artist: 'The Waves', cover: 'https://picsum.photos/id/32/200/200', plays: 19800, sales: 540, playsTrend: 41, salesTrend: 33, isHot: false },
    { id: 4, title: 'Drill Szn', artist: 'Glock Beats', cover: 'https://picsum.photos/id/30/200/200', plays: 15400, sales: 410, playsTrend: 78, salesTrend: 65, isHot: true },
    { id: 5, title: 'Midnight', artist: 'Luna', cover: 'https://picsum.photos/id/33/200/200', plays: 8900, sales: 210, playsTrend: -2, salesTrend: -5, isHot: false },
  ]
};

const trends = computed(() => {
  return (mockData[period.value] || mockData.week).sort((a, b) => b.sales - a.sales).slice(0, 10);
});

const currentPeriodLabel = computed(() => {
  return periods.find(p => p.value === period.value)?.label || 'Неделю';
});

const totalPlays = computed(() => {
  return trends.value.reduce((sum, t) => sum + t.plays, 0);
});

const totalSales = computed(() => {
  return trends.value.reduce((sum, t) => sum + t.sales, 0);
});

const avgGrowth = computed(() => {
  const avg = trends.value.reduce((sum, t) => sum + (t.salesTrend || 0), 0) / trends.value.length;
  return avg.toFixed(1);
});

const changePeriod = (newPeriod) => {
  period.value = newPeriod;
  // Анимация: можно добавить класс загрузки, но для плавности просто обновляется
};

const formatNumber = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num.toString();
};

const getRankClass = (index) => {
  if (index === 0) return 'rank-gold';
  if (index === 1) return 'rank-silver';
  if (index === 2) return 'rank-bronze';
  return '';
};

const getTrendClass = (trend) => {
  if (trend > 0) return 'trend-up';
  if (trend < 0) return 'trend-down';
  return 'trend-zero';
};

const getTrendIcon = (trend) => {
  if (trend > 0) return 'fas fa-arrow-up';
  if (trend < 0) return 'fas fa-arrow-down';
  return 'fas fa-minus';
};

const playTrack = (track) => {
  console.log('Play', track);
  // Здесь можно вызвать глобальный плеер
};

const addToFavorites = (track) => {
  console.log('Add to favorites', track);
};

const buyTrack = (track) => {
  console.log('Buy track', track);
};
</script>

<style scoped>
/* Общий фон */
.trends-page {
  min-height: 100vh;
  background: radial-gradient(circle at 10% 20%, #0a0a1a, #02020a);
  position: relative;
  padding: 2rem 0;
  overflow-x: hidden;
}

.bg-glow {
  position: fixed;
  top: -20%;
  left: -20%;
  width: 140%;
  height: 140%;
  background: radial-gradient(circle, rgba(168,85,247,0.15) 0%, rgba(0,0,0,0) 70%);
  pointer-events: none;
  z-index: 0;
}

.bg-noise {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIj48ZmlsdGVyIGlkPSJmIj48ZmVUdXJidWxlbmNlIHR5cGU9ImZyYWN0YWxOb2lzZSIgYmFzZUZyZXF1ZW5jeT0iLjciIG51bU9jdGF2ZXM9IjMiLz48L2ZpbHRlcj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWx0ZXI9InVybCgjZikiIG9wYWNpdHk9IjAuMDMiLz48L3N2Zz4=');
  pointer-events: none;
  opacity: 0.4;
  z-index: 0;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  position: relative;
  z-index: 2;
}

/* Хедер */
.header {
  text-align: center;
  margin-bottom: 3rem;
}

.title {
  font-size: 3rem;
  font-weight: 800;
  background: linear-gradient(135deg, #fff, #a855f7, #ec4899);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  letter-spacing: -0.02em;
}

.fire-icon {
  font-size: 2.5rem;
  filter: drop-shadow(0 0 8px #f97316);
  animation: flicker 2s infinite;
}

.trend-badge {
  background: linear-gradient(45deg, #a855f7, #ec4899);
  padding: 0.2rem 0.8rem;
  border-radius: 60px;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  margin-left: 1rem;
  box-shadow: 0 0 15px rgba(168,85,247,0.5);
}

.subtitle {
  color: #a0a0b0;
  margin-top: 0.5rem;
  font-size: 1.1rem;
}

/* Переключатель периода */
.period-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 2rem;
  background: rgba(15,15,25,0.6);
  backdrop-filter: blur(12px);
  border-radius: 60px;
  padding: 0.3rem;
  border: 1px solid rgba(168,85,247,0.3);
}

.period-selector {
  display: flex;
  gap: 0.5rem;
}

.period-btn {
  position: relative;
  background: transparent;
  border: none;
  padding: 0.6rem 1.8rem;
  border-radius: 40px;
  color: #c0c0d0;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;
}

.period-btn.active {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  color: white;
  box-shadow: 0 0 15px rgba(168,85,247,0.6);
}

.period-text {
  position: relative;
  z-index: 2;
}

.update-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-right: 1rem;
  color: #a855f7;
  font-size: 0.9rem;
  background: rgba(168,85,247,0.1);
  border-radius: 40px;
  padding: 0.4rem 1.2rem;
}

/* Список трендов */
.trends-list {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  margin-bottom: 3rem;
}

.trend-card {
  display: flex;
  align-items: center;
  background: rgba(20,20,30,0.5);
  backdrop-filter: blur(8px);
  border-radius: 2rem;
  padding: 1rem 1.5rem;
  border: 1px solid rgba(255,255,255,0.05);
  transition: all 0.3s cubic-bezier(0.2, 0.9, 0.4, 1.1);
  animation: slideUp 0.4s ease-out forwards;
  opacity: 0;
  transform: translateY(20px);
}

.trend-card:hover {
  transform: translateY(-5px) scale(1.01);
  background: rgba(30,30,45,0.7);
  border-color: rgba(168,85,247,0.4);
  box-shadow: 0 20px 35px -15px rgba(0,0,0,0.5);
}

@keyframes slideUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Ранговый бейдж */
.rank-badge {
  width: 70px;
  text-align: center;
  position: relative;
}

.rank-number {
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #fff, #a0a0b0);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
}

.rank-gold .rank-number {
  background: linear-gradient(135deg, #ffd700, #ffb347);
  background-clip: text;
  -webkit-background-clip: text;
  text-shadow: 0 0 8px #ffd700;
}
.rank-silver .rank-number {
  background: linear-gradient(135deg, #e0e0e0, #a0a0a0);
  background-clip: text;
}
.rank-bronze .rank-number {
  background: linear-gradient(135deg, #cd7f32, #b87333);
  background-clip: text;
}

.crown-icon {
  position: absolute;
  top: -10px;
  right: 10px;
  font-size: 1.2rem;
  filter: drop-shadow(0 0 4px gold);
}

/* Обложка */
.cover-wrapper {
  position: relative;
  margin: 0 1rem;
}

.track-cover {
  width: 70px;
  height: 70px;
  border-radius: 1rem;
  object-fit: cover;
  box-shadow: 0 8px 20px rgba(0,0,0,0.4);
  transition: all 0.2s;
}

.cover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.cover-wrapper:hover .cover-overlay {
  opacity: 1;
}

.quick-play {
  background: #a855f7;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  transform: scale(0.9);
  transition: transform 0.2s;
}
.quick-play:hover {
  transform: scale(1.1);
}

/* Информация */
.track-info {
  flex: 2;
  margin-left: 0.5rem;
}

.track-title-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.track-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0;
}

.hot-badge {
  background: linear-gradient(45deg, #f97316, #ec4899);
  font-size: 0.7rem;
  padding: 0.2rem 0.5rem;
  border-radius: 20px;
  font-weight: bold;
  color: white;
  text-transform: uppercase;
}

.track-artist {
  color: #a0a0b0;
  font-size: 0.85rem;
  margin-top: 0.2rem;
}

/* Статистика */
.stats-wrapper {
  flex: 3;
  display: flex;
  gap: 2rem;
  justify-content: space-around;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  background: rgba(0,0,0,0.3);
  padding: 0.4rem 1rem;
  border-radius: 40px;
}

.stat-icon {
  font-size: 1.2rem;
  color: #a855f7;
}

.stat-data {
  display: flex;
  flex-direction: column;
}
.stat-value {
  font-weight: 700;
  font-size: 1.1rem;
}
.stat-label {
  font-size: 0.7rem;
  color: #a0a0b0;
}

.trend-indicator {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  font-size: 0.8rem;
  font-weight: 600;
}
.trend-up {
  color: #10b981;
}
.trend-down {
  color: #ef4444;
}
.trend-zero {
  color: #f59e0b;
}

/* Кнопки действий */
.action-buttons {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.btn-icon {
  background: rgba(255,255,255,0.05);
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 40px;
  color: white;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-icon:hover {
  background: #a855f7;
  transform: scale(1.05);
}

.btn-primary {
  background: linear-gradient(45deg, #a855f7, #ec4899);
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 40px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(168,85,247,0.4);
}

/* Аналитическая карточка */
.analytics-card {
  background: rgba(20,20,30,0.6);
  backdrop-filter: blur(12px);
  border-radius: 2rem;
  padding: 1.5rem;
  border: 1px solid rgba(168,85,247,0.3);
  margin-top: 2rem;
}
.analytics-header {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  font-size: 1.3rem;
  margin-bottom: 1rem;
  color: #a855f7;
}
.analytics-grid {
  display: flex;
  justify-content: space-around;
  text-align: center;
}
.analytics-value {
  display: block;
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #fff, #a855f7);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
}
.analytics-label {
  font-size: 0.9rem;
  color: #a0a0b0;
}

/* Анимации для списка */
.trend-list-move, .trend-list-enter-active, .trend-list-leave-active {
  transition: all 0.4s ease;
}
.trend-list-enter-from, .trend-list-leave-to {
  opacity: 0;
  transform: translateX(50px);
}
.trend-list-leave-active {
  position: absolute;
}

@keyframes flicker {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; text-shadow: 0 0 5px #f97316; }
}

@media (max-width: 1000px) {
  .trend-card {
    flex-wrap: wrap;
    padding: 1rem;
  }
  .stats-wrapper {
    order: 3;
    width: 100%;
    margin-top: 1rem;
    justify-content: space-evenly;
  }
  .action-buttons {
    order: 4;
    width: 100%;
    justify-content: flex-end;
    margin-top: 1rem;
  }
  .rank-badge {
    width: 50px;
  }
}
</style>