import { ref, readonly, provide } from 'vue';
import api from '@/api';

export function usePlayer() {
  const currentTrack = ref(null);
  const isPlaying = ref(false);
  
  
  const playlist = ref([]);
  
  
  const history = ref([]);       
  const historyIndex = ref(-1);  

  const isLoading = ref(false);

  
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

  
  const playTrack = (track, addToHistory = true) => {
    if (!track) return;
    
    if (addToHistory) {
      
      
      if (historyIndex.value < history.value.length - 1) {
        history.value = history.value.slice(0, historyIndex.value + 1);
      }
      
      if (history.value[historyIndex.value]?.id !== track.id) {
        history.value.push(track);
        historyIndex.value = history.value.length - 1;
      }
    } else {
      
      
    }
    
    currentTrack.value = track;
    isPlaying.value = true;
    console.log(`🎵 Сейчас играет: ${track.title} (история: ${historyIndex.value + 1}/${history.value.length})`);
  };

  
  const play = (track) => {
    playTrack(track, true);
  };

  
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

  
  const prevTrack = () => {
    if (historyIndex.value > 0) {
      historyIndex.value--;
      const previousTrack = history.value[historyIndex.value];
      playTrack(previousTrack, false); 
    } else {
      console.warn('⚠️ Начало истории, предыдущих треков нет');
    }
  };

  
  const forwardTrack = () => {
    if (historyIndex.value < history.value.length - 1) {
      historyIndex.value++;
      const nextInHistory = history.value[historyIndex.value];
      playTrack(nextInHistory, false);
    } else {
      console.warn('⚠️ Вы в конце истории');
    }
  };
  const togglePlay = () => {
  isPlaying.value = !isPlaying.value;
};

  const player = {
    currentTrack: readonly(currentTrack),
    isPlaying: readonly(isPlaying),
    playTrack: play,         
    nextTrack,
    prevTrack,
    forwardTrack,            
    togglePlay,  
    history: readonly(history),
    historyIndex: readonly(historyIndex),
  };

  provide('player', player);
  return player;
}