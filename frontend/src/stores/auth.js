import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '@/api/index';

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null);
  const isLoading = ref(false);

  // Получение данных текущего пользователя (проверка авторизации)
  const fetchUser = async () => {
    try {
      isLoading.value = true;
      const response = await api.get('/auth/me');
      user.value = response.data;
    } catch (error) {
      user.value = null;
    } finally {
      isLoading.value = false;
    }
  };

  // Вход
  const login = async (credentials) => {
    const formData = new FormData();
    formData.append('username', credentials.login);
    formData.append('password', credentials.password);
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    // После успешного входа сервер установил куки, получаем пользователя
    await fetchUser();
    return response;
  };

  // Регистрация
  const register = async (userData) => {
    const response = await api.post('/auth/register', userData);
    // После регистрации сервер тоже устанавливает куки (автоматический вход)
    await fetchUser();
    return response;
  };

  // Выход
  const logout = async () => {
    await api.post('/auth/logout');
    user.value = null;
  };

  return { user, isLoading, fetchUser, login, register, logout };
});