<template>
  <div class="search">
    <div class="search-header">
      <div class="search-bar">
        <i class="fas fa-search"></i>
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Поиск треков, альбомов, артистов..."
        />
      </div>
      <button class="filter-toggle" @click="showFilters = !showFilters">
        <i class="fas fa-sliders-h"></i> Фильтры
      </button>
    </div>

    <div class="search-content" :class="{ 'filters-open': showFilters }">
      <aside class="filters" v-if="showFilters">
        <h3>Жанр</h3>
        <div v-for="genre in genres" :key="genre" class="filter-option">
          <input
            type="checkbox"
            :id="genre"
            :value="genre"
            v-model="selectedGenres"
          />
          <label :for="genre">{{ genre }}</label>
        </div>

        <h3>BPM</h3>
        <div class="range">
          <input
            type="range"
            min="60"
            max="180"
            step="1"
            v-model="bpmRange[0]"
          />
          <input
            type="range"
            min="60"
            max="180"
            step="1"
            v-model="bpmRange[1]"
          />
          <div class="range-values">
            {{ bpmRange[0] }}
            -
            {{ bpmRange[1] }}
            BPM
          </div>
        </div>

        <h3>Длительность</h3>
        <div class="range">
          <input
            type="range"
            min="0"
            max="10"
            step="0.5"
            v-model="durationRange[0]"
          />
          <input
            type="range"
            min="0"
            max="10"
            step="0.5"
            v-model="durationRange[1]"
          />
          <div class="range-values">
            {{ durationRange[0] }}
            -
            {{ durationRange[1] }}
            мин
          </div>
        </div>

        <button class="apply-filters" @click="applyFilters">Применить</button>
      </aside>

      <main class="results">
        <div class="results-header">
          <span>{{ filteredTracks.length }} результатов</span>
          <select v-model="sortBy">
            <option value="popular">По популярности</option>
            <option value="newest">Сначала новые</option>
            <option value="price">По цене</option>
          </select>
        </div>

        <div class="track-grid">
          <TrackCard
            v-for="track in filteredTracks"
            :key="track.id"
            :track="track"
          />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import TrackCard from "../components/TrackCard.vue";

const searchQuery = ref("");
const showFilters = ref(true);
const selectedGenres = ref([]);
const bpmRange = ref([80, 140]);
const durationRange = ref([2, 6]);
const sortBy = ref("popular");

const genres = [
  "Electronic",
  "Rock",
  "Hip-Hop",
  "Jazz",
  "Classical",
  "Ambient",
];

// Мок-данные
const allTracks = [
  {
    id: 1,
    title: "Neon Dreams",
    artist: "Arctica",
    cover: "https://via.placeholder.com/200",
    duration: 210,
    bpm: 128,
    genre: "Electronic",
    price: 1.99,
  },
  {
    id: 2,
    title: "Lost in Space",
    artist: "Cosmic",
    cover: "https://via.placeholder.com/200",
    duration: 185,
    bpm: 140,
    genre: "Electronic",
    price: 1.49,
  },
  {
    id: 3,
    title: "Echoes",
    artist: "The Waves",
    cover: "https://via.placeholder.com/200",
    duration: 240,
    bpm: 110,
    genre: "Rock",
    price: 2.49,
  },
  {
    id: 4,
    title: "Midnight",
    artist: "Luna",
    cover: "https://via.placeholder.com/200",
    duration: 200,
    bpm: 90,
    genre: "Ambient",
    price: 1.79,
  },
  {
    id: 5,
    title: "Sunset Drive",
    artist: "Pulse",
    cover: "https://via.placeholder.com/200",
    duration: 195,
    bpm: 122,
    genre: "Electronic",
    price: 1.99,
  },
];

const filteredTracks = computed(() => {
  let result = allTracks.filter((track) => {
    // Поиск по названию/артисту
    if (
      searchQuery.value &&
      !track.title.toLowerCase().includes(searchQuery.value.toLowerCase()) &&
      !track.artist.toLowerCase().includes(searchQuery.value.toLowerCase())
    ) {
      return false;
    }
    // Жанр
    if (
      selectedGenres.value.length &&
      !selectedGenres.value.includes(track.genre)
    ) {
      return false;
    }
    // BPM
    if (track.bpm < bpmRange.value[0] || track.bpm > bpmRange.value[1]) {
      return false;
    }
    // Длительность (в минутах)
    const durMin = track.duration / 60;
    if (durMin < durationRange.value[0] || durMin > durationRange.value[1]) {
      return false;
    }
    return true;
  });

  // Сортировка
  if (sortBy.value === "newest") {
    result = result.sort((a, b) => b.id - a.id);
  } else if (sortBy.value === "price") {
    result = result.sort((a, b) => a.price - b.price);
  } else {
    // popular - пока без изменений
  }

  return result;
});

const applyFilters = () => {
  // уже реактивно
};
</script>

<style scoped>
.search {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.search-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.search-bar {
  flex: 1;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 50px;
  padding: 0.5rem 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.search-bar i {
  color: #a0a0b0;
  margin-right: 1rem;
}

.search-bar input {
  background: none;
  border: none;
  color: white;
  font-size: 1rem;
  width: 100%;
  outline: none;
}

.filter-toggle {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 50px;
  padding: 0 1.5rem;
  color: white;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background 0.2s;
}

.filter-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
}

.search-content {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
}

.search-content.filters-open {
  grid-template-columns: 300px 1fr;
}

.filters {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 20px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  height: fit-content;
}

.filters h3 {
  font-size: 1rem;
  margin: 1.5rem 0 1rem;
  color: #a0a0b0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.filters h3:first-of-type {
  margin-top: 0;
}

.filter-option {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.filter-option input {
  margin-right: 0.8rem;
  accent-color: #a855f7;
}

.range {
  margin-bottom: 1rem;
}

.range input[type="range"] {
  width: 100%;
  margin: 0.5rem 0;
  background: transparent;
}

.range-values {
  color: #a0a0b0;
  font-size: 0.9rem;
  text-align: center;
}

.apply-filters {
  width: 100%;
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border: none;
  color: white;
  padding: 0.8rem;
  border-radius: 30px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 1rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.results-header select {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 30px;
  outline: none;
  cursor: pointer;
}

.track-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 2rem;
}
</style>
