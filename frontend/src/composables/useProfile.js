import { ref } from 'vue';
import apiClient from '../api';
import api from '@/api';

export function useProfile() {
  const user = ref(null);
  const purchases = ref([]);
  const favorites = ref([]);
  const subscriptions = ref([]);
  const loading = ref(false);
  const error = ref(null);

  const fetchUser = async () => {
    try {
      const response = await apiClient.get('/auth/me'); // предположительный эндпоинт
      user.value = response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки пользователя';
    }
  };

  const fetchPurchases = async () => {
    try {
      const response = await apiClient.get('/users/me/purchases');
      purchases.value = response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки покупок';
    }
  };

  const fetchFavorites = async () => {
    try {
      const response = await apiClient.get('/users/me/favorites');
      favorites.value = response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки избранного';
    }
  };

  const fetchSubscriptions = async () => {
    try {
      const response = await apiClient.get('/users/me/subscriptions');
      subscriptions.value = response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки подписок';
    }
  };

  // Загрузить все данные сразу
  const fetchAll = async () => {
    loading.value = true;
    error.value = null;
    try {
      await Promise.all([
        fetchUser(),
        fetchPurchases(),
        fetchFavorites(),
        fetchSubscriptions(),
      ]);
    } catch (err) {
      // ошибки уже обработаны в каждом методе, но можно добавить общую
    } finally {
      loading.value = false;
    }
  };

  // Действия
  const editProfile = async (formData) => {
    try {
      const response = await apiClient.put('/auth/me', formData);
      user.value = response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка редактирования';
    }
  };
   const updateProfile = async (formData) => {
    try {
      const response = await api.put('/users/me', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      user.value = response.data;
      return response.data;
    } catch (err) {
      console.error('Update profile error', err);
      throw err;
    }
  };

  const downloadTrack = async (trackId) => {
    try {
      // предположим, что есть эндпоинт для скачивания
      const response = await apiClient.get(`/tracks/${trackId}/download`, {
        responseType: 'blob',
      });
      // создать ссылку и скачать файл
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'track.mp3'); // имя файла можно взять из заголовков
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      error.value = 'Ошибка скачивания';
    }
  };

  const unsubscribe = async (authorId) => {
    try {
      await apiClient.delete(`/authors/${authorId}/subscribe`);
      subscriptions.value = subscriptions.value.filter(a => a.id !== authorId);
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка отписки';
    }
  };

  return {
    user,
    purchases,
    favorites,
    subscriptions,
    loading,
    error,
    fetchAll,
    editProfile,
    downloadTrack,
    unsubscribe,
    updateProfile
  };
}