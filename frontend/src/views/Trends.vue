<template>
  <div class="trends">
    <h1>Тренды</h1>

    <div class="period-selector">
      <button :class="{ active: period === 'day' }" @click="period = 'day'">День</button>
      <button :class="{ active: period === 'week' }" @click="period = 'week'">Неделя</button>
      <button :class="{ active: period === 'month' }" @click="period = 'month'">Месяц</button>
    </div>

    <div class="trends-list">
      <div v-for="(track, index) in trends" :key="track.id" class="trend-item">
        <span class="rank">{{ index + 1 }}</span>
        <img :src="track.cover" alt="" class="trend-cover" />
        <div class="trend-info">
          <h3>{{ track.title }}</h3>
          <p>{{ track.artist }}</p>
        </div>
        <div class="trend-stats">
          <span><i class="fas fa-headphones"></i> {{ track.plays }}</span>
          <span><i class="fas fa-shopping-cart"></i> {{ track.sales }}</span>
        </div>
        <button class="play-btn" @click="playTrack(track)"><i class="fas fa-play"></i></button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const period = ref('week');

// Мок-данные
const allTracks = [
  { id: 1, title: 'Neon Dreams', artist: 'Arctica', cover: 'https://picsum.photos/200/200?random=1', plays: 12400, sales: 342 },
  { id: 2, title: 'Lost in Space', artist: 'Cosmic', cover: 'https://picsum.photos/200/200?random=2', plays: 8700, sales: 215 },
  { id: 3, title: 'Echoes', artist: 'The Waves', cover: 'https://picsum.photos/200/200?random=3', plays: 5300, sales: 98 },
  { id: 4, title: 'Midnight', artist: 'Luna', cover: 'https://picsum.photos/200/200?random=4', plays: 3200, sales: 76 },
  { id: 5, title: 'Drill Szn', artist: 'Glock Beats', cover: 'https://picsum.photos/200/200?random=5', plays: 2800, sales: 45 },
  { id: 6, title: 'Lofi Dreams', artist: 'Sleepy', cover: 'https://picsum.photos/200/200?random=6', plays: 1500, sales: 23 },
];

// Сортируем по продажам (для имитации трендов)
const trends = computed(() => {
  return [...allTracks].sort((a, b) => b.sales - a.sales).slice(0, 10);
});

const playTrack = (track) => {
  console.log('Play', track);
};
</script>

<style scoped>
.trends {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 2rem;
}

.period-selector {
  display: flex;
  gap: 1rem;
  margin: 2rem 0;
  justify-content: center;
}

.period-selector button {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: white;
  padding: 0.5rem 2rem;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.2s;
}

.period-selector button.active {
  background: #a855f7;
  border-color: #a855f7;
}

.trends-list {
  background: rgba(255,255,255,0.02);
  border-radius: 20px;
  padding: 1rem;
}

.trend-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  transition: background 0.2s;
}

.trend-item:hover {
  background: rgba(255,255,255,0.03);
}

.trend-item:last-child {
  border-bottom: none;
}

.rank {
  width: 40px;
  font-size: 1.5rem;
  font-weight: 700;
  color: #a855f7;
  text-align: center;
}

.trend-cover {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  object-fit: cover;
  margin: 0 1rem;
}

.trend-info {
  flex: 1;
}

.trend-info h3 {
  font-size: 1rem;
  margin-bottom: 0.2rem;
}

.trend-info p {
  font-size: 0.85rem;
  color: #a0a0b0;
}

.trend-stats {
  display: flex;
  gap: 1rem;
  color: #a0a0b0;
  font-size: 0.9rem;
  margin-right: 1rem;
}

.trend-stats i {
  margin-right: 0.3rem;
  color: #a855f7;
}

.play-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(168,85,247,0.2);
  cursor: pointer;
  transition: all 0.2s;
}

.play-btn:hover {
  background: #a855f7;
}
</style>