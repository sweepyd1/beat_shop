<template>
  <div class="home">
    <!-- Hero-секция -->
    <section class="hero">
      <h1>Покупай биты напрямую у авторов</h1>
      <p>
        Тысячи эксклюзивных битов в разных жанрах. Лицензии без скрытых
        платежей.
      </p>
      <button class="cta-btn" @click="$router.push('/search')">
        Начать поиск
      </button>
    </section>

    <!-- Популярные биты -->
    <section class="section">
      <h2>Популярные биты</h2>
      <div class="track-grid">
        <TrackCard
          v-for="track in popularTracks"
          :key="track.id"
          :track="track"
          @image-error="handleImageError"
        />
      </div>
    </section>

    <!-- Коллекции по жанрам -->
    <section class="section">
      <h2>Подборки по жанрам</h2>
      <div class="genre-collections">
        <div
          v-for="collection in genreCollections"
          :key="collection.id"
          class="collection-card"
          @click="$router.push(`/collection/${collection.id}`)"
        >
          <img
            :src="collection.cover"
            :alt="collection.genre"
            class="collection-cover"
            @error="handleImageError"
          />
          <div class="collection-info">
            <h3>{{ collection.genre }}</h3>
            <p>{{ collection.tracks }} битов</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Новые релизы -->
    <section class="section">
      <h2>Новые релизы</h2>
      <div class="track-grid">
        <TrackCard
          v-for="track in newReleases"
          :key="track.id"
          :track="track"
          @image-error="handleImageError"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from "vue";
import TrackCard from "../components/TrackCard.vue";

// Встроенная SVG-заглушка (серая с нотой)
const placeholderSVG =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200' viewBox='0 0 24 24' fill='%23cccccc'%3E%3Cpath d='M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z'/%3E%3C/svg%3E";

// Обработчик ошибки загрузки изображения
const handleImageError = (e) => {
  e.target.src = placeholderSVG;
};

// Мок-данные популярных треков
const popularTracks = ref([
  {
    id: 1,
    title: "Neon Dreams",
    artist: "Arctica Beats",
    cover: "https://picsum.photos/200/200?random=1",
    duration: 210,
    price: 1500,
    audioSrc: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
  },
  {
    id: 2,
    title: "Dark Alley",
    artist: "Phonk Lord",
    cover: "https://picsum.photos/200/200?random=2",
    duration: 185,
    price: 2000,
    audioSrc: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
  },
  {
    id: 3,
    title: "Sunset Vibes",
    artist: "Lo-fi Cat",
    cover: "https://picsum.photos/200/200?random=3",
    duration: 240,
    price: 1200,
    audioSrc: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
  },
  {
    id: 4,
    title: "Moscow Nights",
    artist: "Arctica Beats",
    cover: "https://picsum.photos/200/200?random=4",
    duration: 195,
    price: 1800,
    audioSrc: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
  },
]);

// Мок-данные новых релизов
const newReleases = ref([
  {
    id: 5,
    title: "Drill Szn",
    artist: "Glock Beats",
    cover: "https://picsum.photos/200/200?random=5",
    duration: 200,
    price: 2200,
    audioSrc: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
  },
  {
    id: 6,
    title: "Lofi Dreams",
    artist: "Sleepy",
    cover: "https://picsum.photos/200/200?random=6",
    duration: 175,
    price: 1100,
    audioSrc: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3",
  },
]);

// Мок-данные коллекций по жанрам
const genreCollections = ref([
  {
    id: 1,
    genre: "Trap",
    cover: "https://picsum.photos/300/300?random=10",
    tracks: 124,
  },
  {
    id: 2,
    genre: "Drill",
    cover: "https://picsum.photos/300/300?random=11",
    tracks: 89,
  },
  {
    id: 3,
    genre: "Lo-Fi",
    cover: "https://picsum.photos/300/300?random=12",
    tracks: 67,
  },
  {
    id: 4,
    genre: "House",
    cover: "https://picsum.photos/300/300?random=13",
    tracks: 112,
  },
]);
</script>

<style scoped>
.home {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.hero {
  text-align: center;
  padding: 5rem 2rem;
  background: radial-gradient(
    circle at 70% 30%,
    rgba(168, 85, 247, 0.15),
    transparent 70%
  );
  border-radius: 40px;
  margin-bottom: 4rem;
}

.hero h1 {
  font-size: 4rem;
  font-weight: 800;
  background: linear-gradient(45deg, #fff, #c0c0ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 1rem;
  line-height: 1.2;
}

.hero p {
  font-size: 1.2rem;
  color: #a0a0b0;
  max-width: 600px;
  margin: 0 auto 2rem;
}

.cta-btn {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border: none;
  color: white;
  padding: 1rem 3rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.2s;
}

.cta-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(168, 85, 247, 0.3);
}

.section {
  margin-bottom: 4rem;
}

.section h2 {
  font-size: 2rem;
  margin-bottom: 2rem;
  font-weight: 600;
}

.track-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 2rem;
}

.genre-collections {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 2rem;
}

.collection-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s;
  aspect-ratio: 1;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.collection-card:hover {
  transform: translateY(-5px);
  border-color: rgba(168, 85, 247, 0.3);
}

.collection-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: brightness(0.8);
  transition: filter 0.3s;
}

.collection-card:hover .collection-cover {
  filter: brightness(0.6);
}

.collection-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 1.5rem;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.9), transparent);
}

.collection-info h3 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.2rem;
  color: white;
}

.collection-info p {
  color: #a0a0b0;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .home {
    padding: 1rem;
  }

  .hero {
    padding: 3rem 1rem;
  }

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
