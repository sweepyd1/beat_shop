import { ref, watch } from 'vue';
import apiClient from '../api';
import { debounce } from 'lodash'; // или написать свой debounce

export function useSearch() {
  const tracks = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const total = ref(0);

  // Параметры поиска
  const searchQuery = ref('');
  const selectedGenres = ref([]);
  const bpmRange = ref([80, 140]);
  const durationRange = ref([120, 360]); // в секундах (2-6 мин)
  const sortBy = ref('popular');
  const currentPage = ref(0);
  const limit = 20;

  // Загрузка жанров для фильтра (если нужно)
  const genres = ref([]);

  // Загрузка списка жанров с бэкенда
  const fetchGenres = async () => {
    try {
      const response = await apiClient.get('/genres');
      genres.value = response.data; // ожидаем [{id, name}, ...]
    } catch (err) {
      console.error('Failed to load genres', err);
    }
  };

  // Основная функция поиска
  const fetchTracks = async () => {
    loading.value = true;
    error.value = null;

    try {
      const params = {
        query: searchQuery.value || undefined,
        genre_ids: selectedGenres.value.length ? selectedGenres.value.map(g => g.id) : undefined,
        bpm_min: bpmRange.value[0],
        bpm_max: bpmRange.value[1],
        duration_min: durationRange.value[0],
        duration_max: durationRange.value[1],
        sort_by: sortBy.value,
        skip: currentPage.value * limit,
        limit: limit,
      };

      const response = await apiClient.get('/tracks/search', { params });
      tracks.value = response.data;
      // Если бэкенд возвращает общее количество, обновить total
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки';
    } finally {
      loading.value = false;
    }
  };

  // Debounced версия для поиска при вводе
  const debouncedFetch = debounce(fetchTracks, 300);

  // Следим за изменениями фильтров и перезагружаем
  watch([searchQuery, selectedGenres, bpmRange, durationRange, sortBy, currentPage], () => {
    debouncedFetch();
  }, { deep: true });

  return {
    tracks,
    loading,
    error,
    total,
    searchQuery,
    selectedGenres,
    bpmRange,
    durationRange,
    sortBy,
    currentPage,
    genres,
    fetchGenres,
    fetchTracks,
  };
}