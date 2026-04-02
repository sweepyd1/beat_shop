import { ref, readonly, provide } from 'vue';
import api from '@/api';

export function usePlayer() {
  const currentTrack = ref(null);
  const isPlaying = ref(false);
  
  // Плейлист всех доступных треков (для случайного выбора)
  const playlist = ref([]);
  
  // История прослушанных треков (в порядке воспроизведения)
  const history = ref([]);       // массив треков
  const historyIndex = ref(-1);  // текущий индекс в истории (-1 = ничего не играет)

  const isLoading = ref(false);

  // Загрузка плейлиста (треки для случайного выбора)
  const loadPlaylist = async () => {
    if (isLoading.value) return;
    isLoading.value = true;
    try {
      const { data } = await api.get('/tracks/popular', { params: { limit: 50 } });
      playlist.value = data;
      console.log(`📥 Плейлист загружен: ${playlist.value.length} треков`);
    } catch (err) {
      console.error('Ошибка загрузки плейлиста', err);
      try {
        const { data } = await api.get('/tracks', { params: { limit: 50 } });
        playlist.value = data;
      } catch (e) {
        console.error('Не удалось загрузить треки', e);
      }
    } finally {
      isLoading.value = false;
    }
  };

  // Основная функция воспроизведения трека с управлением историей
  const playTrack = (track, addToHistory = true) => {
    if (!track) return;
    
    if (addToHistory) {
      // Если мы не в конце истории (т.е. пользователь нажимал "назад" и теперь выбрал новый трек),
      // обрезаем историю после текущего индекса
      if (historyIndex.value < history.value.length - 1) {
        history.value = history.value.slice(0, historyIndex.value + 1);
      }
      // Добавляем трек в историю (если это не повтор текущего)
      if (history.value[historyIndex.value]?.id !== track.id) {
        history.value.push(track);
        historyIndex.value = history.value.length - 1;
      }
    } else {
      // Принудительная установка (например, при переходе по истории) – не добавляем заново
      // просто обновляем currentTrack
    }
    
    currentTrack.value = track;
    isPlaying.value = true;
    console.log(`🎵 Сейчас играет: ${track.title} (история: ${historyIndex.value + 1}/${history.value.length})`);
  };

  // Воспроизведение трека с добавлением в историю (для внешних вызовов)
  const play = (track) => {
    playTrack(track, true);
  };

  // Следующий трек (случайный)
  const nextTrack = async () => {
    if (playlist.value.length === 0) {
      await loadPlaylist();
    }
    if (playlist.value.length === 0) return;

    let randomTrack;
    do {
      const idx = Math.floor(Math.random() * playlist.value.length);
      randomTrack = playlist.value[idx];
    } while (randomTrack.id === currentTrack.value?.id && playlist.value.length > 1);
    
    playTrack(randomTrack, true);
  };

  // Предыдущий трек (из истории)
  const prevTrack = () => {
    if (historyIndex.value > 0) {
      historyIndex.value--;
      const previousTrack = history.value[historyIndex.value];
      playTrack(previousTrack, false); // не добавляем в историю заново
    } else {
      console.warn('⚠️ Начало истории, предыдущих треков нет');
    }
  };

  // Опционально: кнопка "вперёд" по истории (если пользователь нажимал "назад" и хочет вернуться)
  const forwardTrack = () => {
    if (historyIndex.value < history.value.length - 1) {
      historyIndex.value++;
      const nextInHistory = history.value[historyIndex.value];
      playTrack(nextInHistory, false);
    } else {
      console.warn('⚠️ Вы в конце истории');
    }
  };

  const player = {
    currentTrack: readonly(currentTrack),
    isPlaying: readonly(isPlaying),
    playTrack: play,         // внешний интерфейс
    nextTrack,
    prevTrack,
    forwardTrack,            // если хотите добавить кнопку "вперёд"
    history: readonly(history),
    historyIndex: readonly(historyIndex),
  };

  provide('player', player);
  return player;
}