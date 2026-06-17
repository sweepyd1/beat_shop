import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; 

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
  paramsSerializer: (params) => {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value === undefined || value === null) return;
      if (Array.isArray(value)) {
        value.forEach(v => searchParams.append(key, v));
      } else {
        searchParams.append(key, value);
      }
    });
    return searchParams.toString();
  }
});


api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});


api.interceptors.response.use((response) => {
  
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