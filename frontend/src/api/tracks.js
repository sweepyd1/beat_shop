import api from './index';

export const tracksApi = {
  
  getAllTracks(skip = 0, limit = 100) {
    return api.get('/tracks/', { params: { skip, limit } });
  },

  
  getPopularTracks(limit = 10) {
    return api.get('/tracks/popular', { params: { limit } });
  },

  
  getNewTracks(limit = 10) {
    return api.get('/tracks/new', { params: { limit } });
  },

  
  getTrends(period = 'week', limit = 10) {
    return api.get('/tracks/trends', { params: { period, limit } });
  },

  
  searchTracks(query = '', params = {}) {
    return api.get('/tracks/search', { 
      params: { 
        query,
        ...params 
      } 
    });
  },

  
  getTrackById(trackId) {
    return api.get(`/tracks/${trackId}`);
  },

  
  streamTrack(trackId) {
    return `${api.defaults.baseURL}/tracks/${trackId}/stream`;
  },

  
  downloadTrack(trackId) {
    return api.get(`/tracks/${trackId}/download`, {
      responseType: 'blob'
    });
  },

  
  getMyTracks() {
    return api.get('/tracks/me');
  },

  
  createTrack(formData) {
    return api.post('/tracks/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  
  updateTrack(trackId, trackData) {
    return api.put(`/tracks/${trackId}`, trackData);
  },

  
  deleteTrack(trackId) {
    return api.delete(`/tracks/${trackId}`);
  },
};

export default tracksApi;
