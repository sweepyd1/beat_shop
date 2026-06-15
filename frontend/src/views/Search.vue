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
        <i v-if="loading" class="fas fa-spinner fa-spin"></i>
      </div>
      <button class="filter-toggle" @click="showFilters = !showFilters">
        <i class="fas fa-sliders-h"></i> Фильтры
      </button>
    </div>

    <!-- Активные фильтры в виде чипсов -->
    <div class="active-filters" v-if="hasActiveFilters">
      <span
        class="chip"
        v-for="genre in selectedGenres"
        :key="genre.id"
        @click="removeGenre(genre)"
      >
        {{ genre.name }} <i class="fas fa-times"></i>
      </span>
      <span
        class="chip"
        v-if="bpmRange[0] !== 80 || bpmRange[1] !== 140"
        @click="resetBpm"
      >
        BPM: {{ bpmRange[0] }}-{{ bpmRange[1] }} <i class="fas fa-times"></i>
      </span>
      <span
        class="chip"
        v-if="durationRange[0] !== 120 || durationRange[1] !== 360"
        @click="resetDuration"
      >
        Длит.: {{ Math.round(durationRange[0] / 60) }}-{{
          Math.round(durationRange[1] / 60)
        }}
        мин <i class="fas fa-times"></i>
      </span>
      <button class="clear-all" @click="clearAllFilters">Очистить всё</button>
    </div>

    <div class="search-content" :class="{ 'filters-open': showFilters }">
      <aside class="filters" v-if="showFilters">
        <h3>Жанр</h3>
        <div v-for="genre in genres" :key="genre.id" class="filter-option">
          <input
            type="checkbox"
            :id="'genre-' + genre.id"
            :value="genre"
            v-model="selectedGenres"
          />
          <label :for="'genre-' + genre.id">{{ genre.name }}</label>
          <!-- Если нужно количество треков, можно добавить отдельный эндпоинт -->
        </div>

        <h3>BPM</h3>
        <div class="range">
          <div class="range-slider">
            <input
              type="range"
              min="60"
              max="180"
              step="1"
              :value="bpmRange[0]"
              @input="updateBpmMin($event.target.valueAsNumber)"
            />
            <input
              type="range"
              min="60"
              max="180"
              step="1"
              :value="bpmRange[1]"
              @input="updateBpmMax($event.target.valueAsNumber)"
            />
          </div>
          <div class="range-values">
            <span>{{ bpmRange[0] }} BPM</span> —
            <span>{{ bpmRange[1] }} BPM</span>
          </div>
        </div>

        <h3>Длительность (мин)</h3>
        <div class="range">
          <div class="range-slider">
            <input
              type="range"
              min="0"
              max="600"
              step="30"
              :value="durationRange[0]"
              @input="updateMin($event.target.valueAsNumber)"
            />
            <input
              type="range"
              min="0"
              max="600"
              step="30"
              :value="durationRange[1]"
              @input="updateMax($event.target.valueAsNumber)"
            />
          </div>
          <div class="range-values">
            <span>{{ Math.round(durationRange[0] / 60) }} мин</span> —
            <span>{{ Math.round(durationRange[1] / 60) }} мин</span>
          </div>
        </div>

        <button class="apply-filters" @click="fetchTracks">Применить</button>
      </aside>

      <main class="results">
        <div class="results-header">
          <span class="result-count">{{ tracks.length }} результатов</span>
          <div class="view-options">
            <button
              :class="{ active: viewMode === 'grid' }"
              @click="viewMode = 'grid'"
            >
              <i class="fas fa-th"></i>
            </button>
            <!-- <button
              :class="{ active: viewMode === 'list' }"
              @click="viewMode = 'list'"
            >
              <i class="fas fa-list"></i>
            </button> -->
            <select v-model="sortBy">
              <option value="popular">По популярности</option>
              <option value="newest">Сначала новые</option>
              <option value="price_asc">Сначала дешёвые</option>
              <option value="price_desc">Сначала дорогие</option>
            </select>
          </div>
        </div>

        <div v-if="loading" class="loading">Загрузка...</div>
        <div v-else-if="error" class="error">{{ error }}</div>
        <div v-else-if="tracks.length === 0" class="empty">
          Ничего не найдено
        </div>

        <div
          class="track-grid"
          :class="[viewMode]"
          v-else-if="viewMode === 'grid'"
        >
          <TrackCard
            v-for="track in tracks"
            :key="track.id"
            :track="track"
            @image-error="handleImageError"
          />
        </div>

        <div class="track-list" v-else>
          <div
            v-for="(track, index) in tracks"
            :key="track.id"
            class="track-row"
            @click="playTrack(track)"
          >
            <span class="index">{{ index + 1 }}</span>
            <img
              :src="track.cover_url"
              alt=""
              class="track-cover"
              @error="handleImageError"
            />
            <div class="track-info">
              <span class="title">{{ track.title }}</span>
              <span class="artist">{{ track.author.full_name }}</span>
            </div>
            <span class="genre">{{ track.genre.name }}</span>
            <span class="bpm">{{ track.bpm }} BPM</span>
            <span class="price">{{ track.price }} ₽</span>
            <button class="more" @click.stop>
              <i class="fas fa-ellipsis-v"></i>
            </button>
          </div>
        </div>

        <!-- Пагинация (если нужно) -->
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import TrackCard from "../components/TrackCard.vue";
import { useSearch } from "../composables/useSearch";

const viewMode = ref("grid");
const showFilters = ref(true);

const {
  tracks,
  loading,
  error,
  searchQuery,
  selectedGenres,
  bpmRange,
  durationRange,
  sortBy,
  genres,
  fetchGenres,
  fetchTracks,
} = useSearch();

// Загружаем жанры при монтировании
onMounted(() => {
  fetchGenres();
  fetchTracks();
});
const updateMin = (val) => {
  let newMin = Math.min(val, durationRange.value[1]);
  durationRange.value = [newMin, durationRange.value[1]];
};

const updateMax = (val) => {
  let newMax = Math.max(val, durationRange.value[0]);
  durationRange.value = [durationRange.value[0], newMax];
};

// Защита для ползунков BPM (добавьте аналогично)
const updateBpmMin = (val) => {
  let newMin = Math.min(val, bpmRange.value[1]);
  bpmRange.value = [newMin, bpmRange.value[1]];
};

const updateBpmMax = (val) => {
  let newMax = Math.max(val, bpmRange.value[0]);
  bpmRange.value = [bpmRange.value[0], newMax];
};
// Проверка, есть ли активные фильтры
const hasActiveFilters = computed(() => {
  return (
    selectedGenres.value.length > 0 ||
    bpmRange.value[0] !== 80 ||
    bpmRange.value[1] !== 140 ||
    durationRange.value[0] !== 120 ||
    durationRange.value[1] !== 360
  );
});

// Методы для сброса фильтров
const removeGenre = (genre) => {
  selectedGenres.value = selectedGenres.value.filter((g) => g.id !== genre.id);
};
const resetBpm = () => {
  bpmRange.value = [80, 140];
};
const resetDuration = () => {
  durationRange.value = [120, 360];
};
const clearAllFilters = () => {
  selectedGenres.value = [];
  resetBpm();
  resetDuration();
};

const playTrack = (track) => {
  // Реализовать проигрывание
  console.log("Play", track);
};

const handleImageError = (e) => {
  e.target.src =
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200' viewBox='0 0 24 24' fill='%23cccccc'%3E%3Cpath d='M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z'/%3E%3C/svg%3E";
};
</script>

<style scoped>
/* ===== Базовые стили ===== */
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

/* ===== Активные фильтры (чипсы) ===== */
.active-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  align-items: center;
}
.chip {
  background: rgba(168, 85, 247, 0.2);
  border: 1px solid rgba(168, 85, 247, 0.4);
  border-radius: 30px;
  padding: 0.3rem 1rem;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}
.chip i {
  font-size: 0.8rem;
  opacity: 0.7;
}
.chip:hover {
  background: rgba(168, 85, 247, 0.3);
  border-color: #a855f7;
}
.clear-all {
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #a0a0b0;
  padding: 0.3rem 1rem;
  border-radius: 30px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}
.clear-all:hover {
  background: rgba(255, 255, 255, 0.05);
  color: white;
}

/* ===== Сетка поиска ===== */
.search-content {
  display: grid;
  gap: 2rem;
  transition: grid-template-columns 0.3s;
}
.search-content.filters-open {
  grid-template-columns: 300px 1fr;
}

/* ===== Стилизация фильтров ===== */
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

/* Кастомные чекбоксы */
.filter-option {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  position: relative;
}
.filter-option input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}
.filter-option label {
  padding-left: 28px;
  cursor: pointer;
  position: relative;
  user-select: none;
}
.filter-option label:before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  background: transparent;
  transition: all 0.2s;
}
.filter-option input[type="checkbox"]:checked + label:before {
  background: #a855f7;
  border-color: #a855f7;
}
.filter-option input[type="checkbox"]:checked + label:after {
  content: "\f00c";
  font-family: "Font Awesome 6 Free";
  font-weight: 900;
  position: absolute;
  left: 3px;
  top: 1px;
  font-size: 12px;
  color: white;
}
.filter-option:hover label:before {
  border-color: #a855f7;
}

/* Стилизация range слайдеров */
.range {
  margin-bottom: 1rem;
}
.range-slider {
  position: relative;
  height: 30px;
}
.range-slider input[type="range"] {
  position: absolute;
  width: 100%;
  pointer-events: none;
  -webkit-appearance: none;
  background: transparent;
}
.range-slider input[type="range"]::-webkit-slider-thumb {
  pointer-events: auto;
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #a855f7;
  cursor: pointer;
  margin-top: -6px;
  border: 2px solid white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}
.range-slider input[type="range"]::-webkit-slider-runnable-track {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}
.range-values {
  display: flex;
  justify-content: space-between;
  color: #a0a0b0;
  font-size: 0.9rem;
  margin-top: 0.5rem;
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

/* ===== Результаты ===== */
.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.result-count {
  font-size: 1.1rem;
  color: #a0a0b0;
}
.view-options {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
.view-options button {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.2s;
}
.view-options button.active {
  background: #a855f7;
  border-color: #a855f7;
}

/* Кастомный select */
.view-options select {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  padding: 0.5rem 2rem 0.5rem 1.5rem;
  border-radius: 30px;
  outline: none;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 12px;
}
.view-options select option {
  background: #1a1a2e; /* тёмный фон */
  color: white;
}

/* Отображение сетки/списка */
.track-grid.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 2rem;
}
.track-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.track-row {
  display: flex;
  align-items: center;
  padding: 0.8rem 1rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
}
.track-row:hover {
  background: rgba(255, 255, 255, 0.05);
}
.track-row .index {
  width: 30px;
  color: #a0a0b0;
}
.track-cover {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  object-fit: cover;
  margin-right: 1rem;
}
.track-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.track-info .title {
  font-weight: 500;
}
.track-info .artist {
  font-size: 0.85rem;
  color: #a0a0b0;
}
.track-row .genre,
.track-row .bpm,
.track-row .price {
  margin: 0 1rem;
  color: #a0a0b0;
  font-size: 0.9rem;
  min-width: 80px;
}
.track-row .price {
  color: #a855f7;
  font-weight: 600;
}
.more {
  background: none;
  border: none;
  color: #a0a0b0;
  font-size: 1.2rem;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
}
.track-row:hover .more {
  opacity: 1;
}

/* Состояния загрузки/ошибки */
.loading,
.error,
.empty {
  text-align: center;
  padding: 3rem;
  color: #a0a0b0;
}
.error {
  color: #ff4d4d;
}

/* ===== АДАПТИВНЫЕ СТИЛИ ===== */

/* Планшеты и небольшие десктопы */
@media (max-width: 1024px) {
  .search {
    padding: 1.5rem;
  }
  .track-grid.grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 1.5rem;
  }
}

/* Мобильные устройства (горизонтальная ориентация и узкие планшеты) */
@media (max-width: 768px) {
  .search {
    padding: 1rem;
  }

  .search-header {
    gap: 0.75rem;
    margin-bottom: 1rem;
  }

  .search-bar {
    padding: 0.4rem 1rem;
  }

  .search-bar input {
    font-size: 0.9rem;
  }

  .filter-toggle {
    padding: 0 1rem;
    font-size: 0.9rem;
  }
  .filter-toggle i {
    font-size: 0.9rem;
  }

  /* Фильтры: при открытии занимают всю ширину, сетка становится блоком */
  .search-content.filters-open {
    display: block;
  }

  .filters {
    margin-bottom: 1.5rem;
    width: 100%;
  }

  .results-header {
    flex-wrap: wrap;
    gap: 1rem;
  }

  .view-options {
    margin-left: auto;
  }

  .view-options button {
    width: 36px;
    height: 36px;
  }

  .view-options select {
    padding: 0.4rem 1.8rem 0.4rem 1rem;
    font-size: 0.85rem;
  }

  .track-grid.grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
  }

  /* Список: перестраиваем в две строки для экономии места */
  .track-row {
    flex-wrap: wrap;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.75rem;
  }

  .track-row .index {
    width: 24px;
    font-size: 0.9rem;
  }

  .track-cover {
    width: 48px;
    height: 48px;
  }

  .track-info {
    flex: 1;
    min-width: 120px;
  }

  .track-row .genre,
  .track-row .bpm,
  .track-row .price {
    margin: 0;
    min-width: auto;
    font-size: 0.8rem;
    padding: 0.2rem 0.5rem;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 20px;
  }

  /* Помещаем genre, bpm, price в строку после обложки */
  .track-row .genre {
    margin-left: 2rem;
  }

  .more {
    opacity: 1; /* всегда видно на таче */
    margin-left: auto;
  }

  .active-filters {
    margin-bottom: 1rem;
  }

  .chip {
    font-size: 0.8rem;
    padding: 0.2rem 0.75rem;
  }

  .clear-all {
    font-size: 0.8rem;
    padding: 0.2rem 0.75rem;
  }
}

/* Очень маленькие телефоны (<480px) */
@media (max-width: 480px) {
  .track-grid.grid {
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 0.75rem;
  }

  .track-row .genre,
  .track-row .bpm {
    display: none; /* скрываем жанр и BPM на узких экранах */
  }

  .track-row .price {
    order: 2;
    margin-left: auto;
  }

  .more {
    order: 3;
  }

  .view-options button:first-of-type {
    display: none; /* скрываем кнопку сетки, если места мало — оставляем только список? Лучше оставить обе, но уменьшить */
  }

  /* Возвращаем обе кнопки, но уменьшаем */
  .view-options button {
    width: 32px;
    height: 32px;
    font-size: 0.8rem;
  }

  .view-options button:first-of-type {
    display: inline-flex; /* отменяем скрытие */
  }

  .result-count {
    font-size: 0.9rem;
  }

  .filter-toggle {
    padding: 0 0.8rem;
    font-size: 0.8rem;
  }

  .search-bar {
    padding: 0.3rem 0.8rem;
  }
}

/* Для устройств, где hover не поддерживается (touch) */
@media (hover: none) {
  .more {
    opacity: 1;
  }
  .track-row:hover .more {
    opacity: 1;
  }
}
</style>
