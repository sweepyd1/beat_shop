import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // адрес вашего бэкенда

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для добавления токена авторизации
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Интерцептор для преобразования относительных путей в абсолютные
api.interceptors.response.use((response) => {
  // Если ответ - массив (например, список треков)
  if (Array.isArray(response.data)) {
    response.data = response.data.map(item => {
      if (item.cover_url && !item.cover_url.startsWith('http')) {
        item.cover_url = `${API_BASE_URL}${item.cover_url}`;
      }
      if (item.mp3_file_url && !item.mp3_file_url.startsWith('http')) {
        item.mp3_file_url = `${API_BASE_URL}${item.mp3_file_url}`;
      }
      return item;
    });
  } 
  // Если ответ - объект (один трек, автор и т.д.)
  else if (response.data && typeof response.data === 'object') {
    if (response.data.cover_url && !response.data.cover_url.startsWith('http')) {
      response.data.cover_url = `${API_BASE_URL}${response.data.cover_url}`;
    }
    if (response.data.mp3_file_url && !response.data.mp3_file_url.startsWith('http')) {
      response.data.mp3_file_url = `${API_BASE_URL}${response.data.mp3_file_url}`;
    }
  }
  return response;
}, (error) => {
  return Promise.reject(error);
});

export default api;