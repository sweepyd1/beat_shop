import api from '@/api';

/**
 * Отправляет событие прослушивания на бэкенд.
 * Ошибки не пробрасываются, чтобы не ломать воспроизведение.
 */
export async function logTrackListen(trackId) {
  try {
    await api.post(`/listen/${trackId}`);
    // console.log(`Listen logged for track ${trackId}`);
  } catch (error) {
    // Не блокируем плеер при ошибке логирования
    console.warn('Failed to log listen:', error?.response?.data || error.message);
  }
}