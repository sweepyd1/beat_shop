import api from './index';

export const tracksApi = {
  // Получить все треки
  getAllTracks(skip = 0, limit = 100) {
    return api.get('/tracks/', { params: { skip, limit } });
  },

  // Получить популярные треки
  getPopularTracks(limit = 10) {
    return api.get('/tracks/popular', { params: { limit } });
  },

  // Получить новые треки
  getNewTracks(limit = 10) {
    return api.get('/tracks/new', { params: { limit } });
  },

  // Получить трендовые треки
  getTrends(period = 'week', limit = 10) {
    return api.get('/tracks/trends', { params: { period, limit } });
  },

  // Поиск треков
  searchTracks(query = '', params = {}) {
    return api.get('/tracks/search', { 
      params: { 
        query,
        ...params 
      } 
    });
  },

  // Получить трек по ID
  getTrackById(trackId) {
    return api.get(`/tracks/${trackId}`);
  },

  // Получить поток трека (для воспроизведения)
  streamTrack(trackId) {
    return `${api.defaults.baseURL}/tracks/${trackId}/stream`;
  },

  // Скачать трек
  downloadTrack(trackId) {
    return api.get(`/tracks/${trackId}/download`, {
      responseType: 'blob'
    });
  },

  // Получить мои треки (для автора)
  getMyTracks() {
    return api.get('/tracks/me');
  },

  // Создать трек
  createTrack(formData) {
    return api.post('/tracks/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Обновить трек
  updateTrack(trackId, trackData) {
    return api.put(`/tracks/${trackId}`, trackData);
  },

  // Удалить трек
  deleteTrack(trackId) {
    return api.delete(`/tracks/${trackId}`);
  },
};

export default tracksApi;
