<!-- Файл: Search.vue (обновлённый) -->
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

    <!-- Активные фильтры в виде чипсов -->
    <div class="active-filters" v-if="selectedGenres.length || bpmRange[0] !== 80 || bpmRange[1] !== 140 || durationRange[0] !== 2 || durationRange[1] !== 6">
      <span class="chip" v-for="genre in selectedGenres" :key="genre" @click="removeGenre(genre)">
        {{ genre }} <i class="fas fa-times"></i>
      </span>
      <span class="chip" v-if="bpmRange[0] !== 80 || bpmRange[1] !== 140" @click="resetBpm">
        BPM: {{ bpmRange[0] }}-{{ bpmRange[1] }} <i class="fas fa-times"></i>
      </span>
      <span class="chip" v-if="durationRange[0] !== 2 || durationRange[1] !== 6" @click="resetDuration">
        Длит.: {{ durationRange[0] }}-{{ durationRange[1] }} мин <i class="fas fa-times"></i>
      </span>
      <button class="clear-all" @click="clearAllFilters">Очистить всё</button>
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
          <span class="genre-count">({{ getGenreCount(genre) }})</span>
        </div>

        <h3>BPM</h3>
        <div class="range">
          <div class="range-slider">
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
          </div>
          <div class="range-values">
            <span>{{ bpmRange[0] }} BPM</span> — <span>{{ bpmRange[1] }} BPM</span>
          </div>
        </div>

        <h3>Длительность (мин)</h3>
        <div class="range">
          <div class="range-slider">
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
          </div>
          <div class="range-values">
            <span>{{ durationRange[0] }} мин</span> — <span>{{ durationRange[1] }} мин</span>
          </div>
        </div>

        <button class="apply-filters" @click="applyFilters">Применить</button>
      </aside>

      <main class="results">
        <div class="results-header">
          <span class="result-count">{{ filteredTracks.length }} результатов</span>
          <div class="view-options">
            <button :class="{ active: viewMode === 'grid' }" @click="viewMode = 'grid'">
              <i class="fas fa-th"></i>
            </button>
            <button :class="{ active: viewMode === 'list' }" @click="viewMode = 'list'">
              <i class="fas fa-list"></i>
            </button>
            <select v-model="sortBy">
              <option value="popular">По популярности</option>
              <option value="newest">Сначала новые</option>
              <option value="price_asc">Сначала дешёвые</option>
              <option value="price_desc">Сначала дорогие</option>
            </select>
          </div>
        </div>

        <div class="track-grid" :class="[viewMode]" v-if="viewMode === 'grid'">
          <TrackCard
            v-for="track in filteredTracks"
            :key="track.id"
            :track="track"
            @image-error="handleImageError"
          />
        </div>

        <div class="track-list" v-else>
          <div
            v-for="(track, index) in filteredTracks"
            :key="track.id"
            class="track-row"
            @click="playTrack(track)"
          >
            <span class="index">{{ index + 1 }}</span>
            <img :src="track.cover" alt="" class="track-cover" @error="handleImageError" />
            <div class="track-info">
              <span class="title">{{ track.title }}</span>
              <span class="artist">{{ track.artist }}</span>
            </div>
            <span class="genre">{{ track.genre }}</span>
            <span class="bpm">{{ track.bpm }} BPM</span>
            <span class="price">{{ track.price }} ₽</span>
            <button class="more" @click.stop><i class="fas fa-ellipsis-v"></i></button>
          </div>
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
const viewMode = ref("grid"); // 'grid' или 'list'

const genres = ["Electronic", "Rock", "Hip-Hop", "Jazz", "Classical", "Ambient"];

// Мок-данные (расширенные)
const allTracks = [
  { id: 1, title: "Neon Dreams", artist: "Arctica", cover: "https://picsum.photos/200/200?random=1", duration: 210, bpm: 128, genre: "Electronic", price: 1.99, plays: 12400, date: "2025-02-15" },
  { id: 2, title: "Lost in Space", artist: "Cosmic", cover: "https://picsum.photos/200/200?random=2", duration: 185, bpm: 140, genre: "Electronic", price: 1.49, plays: 8700, date: "2025-02-10" },
  { id: 3, title: "Echoes", artist: "The Waves", cover: "https://picsum.photos/200/200?random=3", duration: 240, bpm: 110, genre: "Rock", price: 2.49, plays: 5300, date: "2025-02-05" },
  { id: 4, title: "Midnight", artist: "Luna", cover: "https://picsum.photos/200/200?random=4", duration: 200, bpm: 90, genre: "Ambient", price: 1.79, plays: 3200, date: "2025-02-12" },
  { id: 5, title: "Sunset Drive", artist: "Pulse", cover: "https://picsum.photos/200/200?random=5", duration: 195, bpm: 122, genre: "Electronic", price: 1.99, plays: 2100, date: "2025-02-18" },
  { id: 6, title: "Drill Szn", artist: "Glock Beats", cover: "https://picsum.photos/200/200?random=6", duration: 200, bpm: 150, genre: "Hip-Hop", price: 2.20, plays: 800, date: "2025-02-20" },
  { id: 7, title: "Lofi Dreams", artist: "Sleepy", cover: "https://picsum.photos/200/200?random=7", duration: 175, bpm: 85, genre: "Jazz", price: 1.10, plays: 1200, date: "2025-02-19" },
];

// Подсчёт количества треков в жанре
const getGenreCount = (genre) => {
  return allTracks.filter(t => t.genre === genre).length;
};

const filteredTracks = computed(() => {
  let result = allTracks.filter((track) => {
    if (searchQuery.value && !track.title.toLowerCase().includes(searchQuery.value.toLowerCase()) && !track.artist.toLowerCase().includes(searchQuery.value.toLowerCase())) return false;
    if (selectedGenres.value.length && !selectedGenres.value.includes(track.genre)) return false;
    if (track.bpm < bpmRange.value[0] || track.bpm > bpmRange.value[1]) return false;
    const durMin = track.duration / 60;
    if (durMin < durationRange.value[0] || durMin > durationRange.value[1]) return false;
    return true;
  });

  // Сортировка
  if (sortBy.value === "newest") {
    result = result.sort((a, b) => new Date(b.date) - new Date(a.date));
  } else if (sortBy.value === "price_asc") {
    result = result.sort((a, b) => a.price - b.price);
  } else if (sortBy.value === "price_desc") {
    result = result.sort((a, b) => b.price - a.price);
  } else {
    result = result.sort((a, b) => b.plays - a.plays);
  }
  return result;
});

const applyFilters = () => { /* уже реактивно */ };
const clearAllFilters = () => {
  selectedGenres.value = [];
  bpmRange.value = [80, 140];
  durationRange.value = [2, 6];
};
const removeGenre = (genre) => {
  selectedGenres.value = selectedGenres.value.filter(g => g !== genre);
};
const resetBpm = () => { bpmRange.value = [80, 140]; };
const resetDuration = () => { durationRange.value = [2, 6]; };
const playTrack = (track) => { console.log("Play", track); }; // Заглушка

const handleImageError = (e) => {
  e.target.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200' viewBox='0 0 24 24' fill='%23cccccc'%3E%3Cpath d='M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z'/%3E%3C/svg%3E";
};
</script>

<style scoped>
.search { max-width: 1400px; margin: 0 auto; padding: 2rem; }
.search-header { display: flex; gap: 1rem; margin-bottom: 2rem; }
.search-bar { flex: 1; display: flex; align-items: center; background: rgba(255,255,255,0.05); border-radius: 50px; padding: 0.5rem 1.5rem; border: 1px solid rgba(255,255,255,0.1); }
.search-bar i { color: #a0a0b0; margin-right: 1rem; }
.search-bar input { background: none; border: none; color: white; font-size: 1rem; width: 100%; outline: none; }
.filter-toggle { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 50px; padding: 0 1.5rem; color: white; font-size: 1rem; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; transition: background 0.2s; }
.filter-toggle:hover { background: rgba(255,255,255,0.1); }

/* Активные фильтры (чипсы) */
.active-filters { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.5rem; align-items: center; }
.chip { background: rgba(168,85,247,0.2); border: 1px solid rgba(168,85,247,0.4); border-radius: 30px; padding: 0.3rem 1rem; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 0.5rem; cursor: pointer; transition: all 0.2s; }
.chip i { font-size: 0.8rem; opacity: 0.7; }
.chip:hover { background: rgba(168,85,247,0.3); border-color: #a855f7; }
.clear-all { background: none; border: 1px solid rgba(255,255,255,0.2); color: #a0a0b0; padding: 0.3rem 1rem; border-radius: 30px; font-size: 0.9rem; cursor: pointer; transition: all 0.2s; }
.clear-all:hover { background: rgba(255,255,255,0.05); color: white; }

.search-content { display: grid; gap: 2rem; transition: grid-template-columns 0.3s; }
.search-content.filters-open { grid-template-columns: 300px 1fr; }
.filters { background: rgba(255,255,255,0.02); border-radius: 20px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.05); height: fit-content; }
.filters h3 { font-size: 1rem; margin: 1.5rem 0 1rem; color: #a0a0b0; text-transform: uppercase; letter-spacing: 0.5px; }
.filters h3:first-of-type { margin-top: 0; }
.filter-option { display: flex; align-items: center; margin-bottom: 0.5rem; }
.filter-option input { margin-right: 0.8rem; accent-color: #a855f7; }
.filter-option label { flex: 1; }
.filter-option .genre-count { color: #a0a0b0; font-size: 0.8rem; }
.range { margin-bottom: 1rem; }
.range-slider { position: relative; height: 30px; }
.range-slider input[type="range"] { position: absolute; width: 100%; pointer-events: none; -webkit-appearance: none; background: transparent; }
.range-slider input[type="range"]::-webkit-slider-thumb { pointer-events: auto; -webkit-appearance: none; width: 16px; height: 16px; border-radius: 50%; background: #a855f7; cursor: pointer; margin-top: -6px; }
.range-slider input[type="range"]::-webkit-slider-runnable-track { width: 100%; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; }
.range-values { display: flex; justify-content: space-between; color: #a0a0b0; font-size: 0.9rem; margin-top: 0.5rem; }
.apply-filters { width: 100%; background: linear-gradient(45deg, #a855f7, #3b82f6); border: none; color: white; padding: 0.8rem; border-radius: 30px; font-weight: 600; cursor: pointer; margin-top: 1rem; }

.results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.result-count { font-size: 1.1rem; color: #a0a0b0; }
.view-options { display: flex; gap: 0.5rem; align-items: center; }
.view-options button { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white; width: 40px; height: 40px; border-radius: 30px; cursor: pointer; transition: all 0.2s; }
.view-options button.active { background: #a855f7; border-color: #a855f7; }
.view-options select { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white; padding: 0.5rem 1.5rem; border-radius: 30px; outline: none; cursor: pointer; }

.track-grid.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 2rem; }
.track-list { display: flex; flex-direction: column; gap: 0.5rem; }
.track-row { display: flex; align-items: center; padding: 0.8rem 1rem; background: rgba(255,255,255,0.02); border-radius: 12px; cursor: pointer; transition: background 0.2s; }
.track-row:hover { background: rgba(255,255,255,0.05); }
.track-row .index { width: 30px; color: #a0a0b0; }
.track-cover { width: 40px; height: 40px; border-radius: 6px; object-fit: cover; margin-right: 1rem; }
.track-info { flex: 1; display: flex; flex-direction: column; }
.track-info .title { font-weight: 500; }
.track-info .artist { font-size: 0.85rem; color: #a0a0b0; }
.track-row .genre, .track-row .bpm, .track-row .price { margin: 0 1rem; color: #a0a0b0; font-size: 0.9rem; min-width: 80px; }
.track-row .price { color: #a855f7; font-weight: 600; }
.more { background: none; border: none; color: #a0a0b0; font-size: 1.2rem; cursor: pointer; opacity: 0; transition: opacity 0.2s; }
.track-row:hover .more { opacity: 1; }
</style>