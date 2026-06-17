
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/api/index';

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null);
  const isLoading = ref(false);
  const initialized = ref(false);             

  const isAuthenticated = computed(() => !!user.value);

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

  
  const restoreSession = async () => {
    if (initialized.value) return;             
    initialized.value = true;
    await fetchUser();
  };

  const login = async (credentials) => {
    try {
      const formData = new FormData();
      formData.append('username', credentials.login);
      formData.append('password', credentials.password);
      const response = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      await fetchUser();
      initialized.value = true;               
      return response;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      const response = await api.post('/auth/register', userData);
      await fetchUser();
      initialized.value = true;               
      return response;
    } catch (error) {
      console.error('Register error:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      user.value = null;
      initialized.value = false;              
    }
  };

  return { 
    user, 
    isLoading, 
    isAuthenticated,
    initialized,
    fetchUser,
    restoreSession,        
    login, 
    register, 
    logout 
  };
});