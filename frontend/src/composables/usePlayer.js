import { ref, readonly, provide } from 'vue';
import api from '@/api'; // путь к вашему axios-инстансу

export function usePlayer() {
  const currentTrack = ref(null);
  const isPlaying = ref(false);
  
  // Список всех треков для случайного выбора
  const playlist = ref([]);
  // История прослушанных треков
  const history = ref([]);
  const isLoading = ref(false);

  // Загрузка треков с бэкенда (один раз)
  const loadPlaylist = async () => {
    if (isLoading.value) return;
    isLoading.value = true;
    try {
      // Используйте любой рабочий эндпоинт, например /tracks/popular или /tracks
      const { data } = await api.get('/tracks/popular', { params: { limit: 50 } });
      playlist.value = data;
      console.log(`✅ Загружено ${playlist.value.length} треков для плейлиста`);
    } catch (err) {
      console.error('Ошибка загрузки плейлиста', err);
      // fallback: пробуем /tracks
      try {
        const { data } = await api.get('/tracks', { params: { limit: 50 } });
        playlist.value = data;
      } catch (e) {
        console.error('Не удалось загрузить треки ни через один эндпоинт', e);
      }
    } finally {
      isLoading.value = false;
    }
  };

  // Воспроизведение трека с сохранением истории
  const playTrack = (track) => {
    if (!track) return;
    
    // Сохраняем текущий трек в историю (если он есть и не равен новому)
    if (currentTrack.value && currentTrack.value.id !== track.id) {
      history.value.push(currentTrack.value);
      console.log(`📜 Сохранён в историю: ${currentTrack.value.title}`);
    }
    
    currentTrack.value = track;
    isPlaying.value = true;
    console.log(`🎵 Сейчас играет: ${track.title}`);
  };

  // Следующий трек (случайный из плейлиста)
  const nextTrack = async () => {
    if (playlist.value.length === 0) {
      await loadPlaylist();
    }
    
    if (playlist.value.length === 0) {
      console.warn('⚠️ Нет треков для воспроизведения');
      return;
    }
    
    // Выбираем случайный трек, не повторяя текущий (если есть другие)
    let randomTrack;
    do {
      const randomIndex = Math.floor(Math.random() * playlist.value.length);
      randomTrack = playlist.value[randomIndex];
    } while (randomTrack.id === currentTrack.value?.id && playlist.value.length > 1);
    
    playTrack(randomTrack);
  };

  // Предыдущий трек (из истории)
  const prevTrack = () => {
    if (history.value.length === 0) {
      console.warn('⚠️ История пуста, некуда возвращаться');
      return;
    }
    const previous = history.value.pop();
    playTrack(previous);
  };

  // Очистка (при необходимости)
  const clear = () => {
    currentTrack.value = null;
    isPlaying.value = false;
    playlist.value = [];
    history.value = [];
  };

  const player = {
    currentTrack: readonly(currentTrack),
    isPlaying: readonly(isPlaying),
    playTrack,
    nextTrack,
    prevTrack,
    clear
  };

  provide('player', player);
  return player;
}