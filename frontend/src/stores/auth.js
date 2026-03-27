import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/api/index';

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null);
  const isLoading = ref(false);

  // Добавляем computed свойство isAuthenticated
  const isAuthenticated = computed(() => !!user.value);

  // Получение данных текущего пользователя (проверка авторизации)
  const fetchUser = async () => {
    try {
      isLoading.value = true;
      const response = await api.get('/auth/me');
      user.value = response.data;
      console.log('fetchUser success:', user.value);
      return true;
    } catch (error) {
      console.error('fetchUser error:', error);
      user.value = null;
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  // Вход
  const login = async (credentials) => {
    try {
      const formData = new FormData();
      formData.append('username', credentials.login);
      formData.append('password', credentials.password);
      const response = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      console.log('Login response:', response.data);
      // После успешного входа сервер установил куки, получаем пользователя
      await fetchUser();
      return response;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  // Регистрация
  const register = async (userData) => {
    try {
      const response = await api.post('/auth/register', userData);
      console.log('Register response:', response.data);
      // После регистрации сервер тоже устанавливает куки (автоматический вход)
      await fetchUser();
      return response;
    } catch (error) {
      console.error('Register error:', error);
      throw error;
    }
  };

  // Выход
  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      user.value = null;
    }
  };

  return { 
    user, 
    isLoading, 
    isAuthenticated,  // обязательно возвращаем!
    fetchUser, 
    login, 
    register, 
    logout 
  };
});