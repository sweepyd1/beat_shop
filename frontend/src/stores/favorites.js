import { defineStore } from 'pinia';
import api from '@/api';

export const useFavoritesStore = defineStore('favorites', {
  state: () => ({
    items: [],
    loading: false,
  }),
  actions: {
    async fetch() {
      this.loading = true;
      try {
        const { data } = await api.get('/favorites');
        this.items = data;
      } catch (err) {
        console.error('Failed to fetch favorites', err);
      } finally {
        this.loading = false;
      }
    },
    async add(trackId) {
      try {
        await api.post(`/favorites/${trackId}`);
        await this.fetch(); 
      } catch (err) {
        console.error('Failed to add favorite', err);
        throw err;
      }
    },
    async remove(trackId) {
      try {
        await api.delete(`/favorites/${trackId}`);
        await this.fetch(); 
      } catch (err) {
        console.error('Failed to remove favorite', err);
        throw err;
      }
    },
    isFavorite(trackId) {
      return this.items.some(fav => fav.track_id === trackId);
    },
  },
});