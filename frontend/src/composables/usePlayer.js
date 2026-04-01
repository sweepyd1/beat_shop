import { ref, readonly, provide } from 'vue';

export function usePlayer() {
  const currentTrack = ref(null);
  const isPlaying = ref(false);
  const queue = ref([]);
  const currentIndex = ref(0);

  const playTrack = (track) => {
    currentTrack.value = track;
    isPlaying.value = true;
    if (!queue.value.some(t => t.id === track.id)) {
      queue.value.push(track);
      currentIndex.value = queue.value.length - 1;
    } else {
      const idx = queue.value.findIndex(t => t.id === track.id);
      if (idx !== -1) currentIndex.value = idx;
    }
  };

  const nextTrack = () => {
    if (queue.value.length === 0) return;
    const nextIdx = (currentIndex.value + 1) % queue.value.length;
    currentIndex.value = nextIdx;
    currentTrack.value = queue.value[nextIdx];
    isPlaying.value = true;
  };

  const prevTrack = () => {
    if (queue.value.length === 0) return;
    const prevIdx = (currentIndex.value - 1 + queue.value.length) % queue.value.length;
    currentIndex.value = prevIdx;
    currentTrack.value = queue.value[prevIdx];
    isPlaying.value = true;
  };

  const player = {
    currentTrack: readonly(currentTrack),
    isPlaying: readonly(isPlaying),
    playTrack,
    nextTrack,
    prevTrack
  };

  provide('player', player);
  return player;
}