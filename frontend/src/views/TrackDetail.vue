<template>
  <div class="track-detail">
    <div class="track-header">
      <img :src="track.cover" :alt="track.title" class="track-cover" @error="handleImageError" />
      <div class="track-info">
        <h1>{{ track.title }}</h1>
        <router-link :to="`/artist/${track.artistId}`" class="artist">{{ track.artist }}</router-link>
        <div class="meta">
          <span><i class="fas fa-clock"></i> {{ formatTime(track.duration) }}</span>
          <span><i class="fas fa-chart-line"></i> {{ track.bpm }} BPM</span>
          <span><i class="fas fa-tag"></i> {{ track.genre }}</span>
          <span><i class="fas fa-headphones"></i> {{ track.plays }} прослушиваний</span>
        </div>
        <div class="price">{{ track.price }} ₽</div>
        <div class="actions">
          <button class="btn-primary" @click="addToCart"><i class="fas fa-cart-plus"></i> В корзину</button>
          <button class="btn-secondary" @click="playTrack(track)"><i class="fas fa-play"></i> Превью</button>
          <button class="btn-icon"><i class="far fa-heart"></i></button>
        </div>
      </div>
    </div>

    <div class="track-description" v-if="track.description">
      <h3>Описание</h3>
      <p>{{ track.description }}</p>
    </div>

    <div class="similar-tracks">
      <h3>Похожие треки</h3>
      <div class="track-grid">
        <TrackCard
          v-for="similar in similarTracks"
          :key="similar.id"
          :track="similar"
          @image-error="handleImageError"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import TrackCard from '../components/TrackCard.vue';

const route = useRoute();
const track = ref({});
const similarTracks = ref([]);

// Мок-данные (позже заменить на запрос к API)
const mockTracks = [
  { id: 1, title: 'Neon Dreams', artist: 'Arctica', artistId: 1, cover: 'https://picsum.photos/200/200?random=1', duration: 210, bpm: 128, genre: 'Electronic', price: 1.99, plays: 12400, description: 'Энергичный электронный трек с глубоким басом.' },
  { id: 2, title: 'Lost in Space', artist: 'Cosmic', artistId: 2, cover: 'https://picsum.photos/200/200?random=2', duration: 185, bpm: 140, genre: 'Electronic', price: 1.49, plays: 8700 },
  { id: 3, title: 'Echoes', artist: 'The Waves', artistId: 3, cover: 'https://picsum.photos/200/200?random=3', duration: 240, bpm: 110, genre: 'Rock', price: 2.49, plays: 5300 },
  { id: 4, title: 'Midnight', artist: 'Luna', artistId: 4, cover: 'https://picsum.photos/200/200?random=4', duration: 200, bpm: 90, genre: 'Ambient', price: 1.79, plays: 3200 },
];

onMounted(() => {
  const id = parseInt(route.params.id);
  track.value = mockTracks.find(t => t.id === id) || mockTracks[0];
  // Похожие — просто другие треки того же жанра
  similarTracks.value = mockTracks.filter(t => t.genre === track.value.genre && t.id !== track.value.id).slice(0, 4);
});

const formatTime = (sec) => {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
};

const addToCart = () => {
  console.log('Добавлено в корзину', track.value);
  // здесь будет логика добавления
};

const playTrack = (t) => {
  console.log('Play', t);
  // вызов плеера
};

const handleImageError = (e) => {
  e.target.src = 'data:image/svg+xml,...'; // сокращено
};
</script>

<style scoped>
.track-detail {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 2rem;
}

.track-header {
  display: flex;
  gap: 3rem;
  margin-bottom: 3rem;
  align-items: flex-end;
  background: rgba(255,255,255,0.02);
  padding: 2rem;
  border-radius: 30px;
  border: 1px solid rgba(255,255,255,0.05);
}

.track-cover {
  width: 250px;
  height: 250px;
  border-radius: 24px;
  object-fit: cover;
  box-shadow: 0 20px 30px rgba(0,0,0,0.5);
}

.track-info {
  flex: 1;
}

.track-info h1 {
  font-size: 3rem;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #fff, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.artist {
  font-size: 1.2rem;
  color: #a855f7;
  text-decoration: none;
  margin-bottom: 1rem;
  display: inline-block;
}

.artist:hover {
  text-decoration: underline;
}

.meta {
  display: flex;
  gap: 1.5rem;
  color: #a0a0b0;
  margin: 1rem 0;
  flex-wrap: wrap;
}

.meta i {
  margin-right: 0.3rem;
  color: #a855f7;
}

.price {
  font-size: 2rem;
  font-weight: 700;
  color: #a855f7;
  margin: 1rem 0;
}

.actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.btn-primary {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border: none;
  color: white;
  padding: 0.8rem 2rem;
  border-radius: 30px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  transform: scale(1.05);
  box-shadow: 0 10px 20px rgba(168,85,247,0.3);
}

.btn-secondary {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: white;
  padding: 0.8rem 2rem;
  border-radius: 30px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: rgba(255,255,255,0.1);
}

.btn-icon {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: #a855f7;
  border-color: #a855f7;
}

.track-description {
  background: rgba(255,255,255,0.02);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 3rem;
}

.track-description h3 {
  margin-bottom: 1rem;
}

.similar-tracks h3 {
  margin-bottom: 1.5rem;
}

.track-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 2rem;
}
</style>