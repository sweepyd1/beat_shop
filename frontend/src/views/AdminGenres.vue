<template>
  <div class="admin-genres-page">
    <div class="page-header">
      <h1>🎵 Управление жанрами</h1>
      <p>Добавление, редактирование, удаление музыкальных жанров</p>
    </div>

    <!-- Кнопка добавления -->
    <div class="actions">
      <button class="btn-primary" @click="openCreateModal">
        <i class="fas fa-plus"></i> Добавить жанр
      </button>
    </div>

    <!-- Таблица жанров -->
    <div class="genres-table-container">
      <table class="genres-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Изображение</th>
            <th>Название</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="4" class="loading-cell">
              <i class="fas fa-spinner fa-spin"></i> Загрузка...
            </td>
          </tr>
          <tr v-else-if="genres.length === 0">
            <td colspan="4" class="empty-cell">Нет жанров</td>
          </tr>
          <tr v-for="genre in genres" :key="genre.id">
            <td>{{ genre.id }}</td>
            <td>
              <img 
                v-if="genre.image_url" 
                :src="getImageUrl(genre.image_url)" 
                class="genre-thumb" 
                alt="cover"
              >
              <div v-else class="no-image">—</div>
            </td>
            <td>{{ genre.name }}</td>
            <td class="actions-cell">
              <button class="btn-edit" @click="openEditModal(genre)">
                <i class="fas fa-edit"></i>
              </button>
              <!-- <button class="btn-delete" @click="confirmDelete(genre)">
                <i class="fas fa-trash"></i>
              </button> -->
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Модальное окно создания/редактирования -->
    <teleport to="body">
      <div v-if="modalVisible" class="modal-overlay" @click.self="closeModal">
        <div class="modal-content genre-modal">
          <div class="modal-header">
            <h2>{{ isEdit ? 'Редактировать жанр' : 'Новый жанр' }}</h2>
            <button @click="closeModal" class="close-btn">&times;</button>
          </div>
          <form @submit.prevent="saveGenre">
            <div class="form-group">
              <label>Название жанра</label>
              <input 
                type="text" 
                v-model="form.name" 
                required 
                placeholder="Например: Hip-Hop, Electronic"
              />
            </div>
            <div class="form-group">
              <label>Изображение жанра</label>
              <div class="image-upload-area">
                <div class="current-image" v-if="form.image_url">
                  <img :src="getImageUrl(form.image_url)" alt="preview" />
                  <button type="button" class="remove-image" @click="removeImage">✕</button>
                </div>
                <div class="upload-controls">
                  <input 
                    type="file" 
                    ref="fileInput"
                    accept="image/*"
                    @change="handleImageUpload"
                    style="display: none"
                  />
                  <button type="button" class="btn-secondary" @click="$refs.fileInput.click()">
                    <i class="fas fa-cloud-upload-alt"></i> Загрузить картинку
                  </button>
                  <span class="or">или</span>
                  <input 
                    type="text" 
                    v-model="form.image_url" 
                    placeholder="URL изображения"
                    class="url-input"
                  />
                </div>
              </div>
              <div class="image-hint">Рекомендуемый размер: 400x400px</div>
            </div>
            <div class="modal-buttons">
              <button type="button" class="btn-secondary" @click="closeModal">Отмена</button>
              <button type="submit" class="btn-primary" :disabled="saving">
                <i v-if="saving" class="fas fa-spinner fa-spin"></i>
                <span v-else>{{ isEdit ? 'Сохранить' : 'Создать' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/api';
import { showSuccess, showError } from '@/utils/alert';

const genres = ref([]);
const loading = ref(true);
const modalVisible = ref(false);
const isEdit = ref(false);
const saving = ref(false);
const form = ref({ id: null, name: '', image_url: '' });
const fileInput = ref(null);

const fetchGenres = async () => {
  try {
    const { data } = await api.get('/admin/genres/');  // эндпоинт GET /admin/genres/
    genres.value = data;
  } catch (error) {
    console.error(error);
    showError('Не удалось загрузить жанры');
  } finally {
    loading.value = false;
  }
};

const getImageUrl = (url) => {
  if (!url) return '';
  if (url.startsWith('http')) return url;
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  return `${baseUrl}${url}`;
};

const openCreateModal = () => {
  isEdit.value = false;
  form.value = { id: null, name: '', image_url: '' };
  modalVisible.value = true;
};

const openEditModal = (genre) => {
  isEdit.value = true;
  form.value = { ...genre };
  modalVisible.value = true;
};

const closeModal = () => {
  modalVisible.value = false;
  form.value = { id: null, name: '', image_url: '' };
  if (fileInput.value) fileInput.value.value = '';
};

const handleImageUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  // Проверка типа
  if (!file.type.startsWith('image/')) {
    showError('Можно загружать только изображения');
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    showError('Размер файла не более 5 МБ');
    return;
  }
  
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const { data } = await api.post('/admin/genres/upload-image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    form.value.image_url = data.image_url;
    showSuccess('Изображение загружено');
  } catch (error) {
    console.error(error);
    showError('Ошибка загрузки изображения');
  }
};

const removeImage = () => {
  form.value.image_url = '';
};

const saveGenre = async () => {
  if (!form.value.name.trim()) {
    showError('Название жанра обязательно');
    return;
  }
  saving.value = true;
  try {
    const payload = { name: form.value.name, image_url: form.value.image_url };
    if (isEdit.value) {
      await api.put(`/admin/genres/${form.value.id}`, payload);
      showSuccess('Жанр обновлён');
    } else {
      await api.post('/admin/genres/', payload);
      showSuccess('Жанр создан');
    }
    await fetchGenres();
    closeModal();
  } catch (error) {
    console.error(error);
    const msg = error.response?.data?.detail || 'Ошибка сохранения';
    showError(msg);
  } finally {
    saving.value = false;
  }
};

const confirmDelete = async (genre) => {
  if (!confirm(`Удалить жанр "${genre.name}"? Все треки этого жанра потеряют привязку.`)) return;
  try {
    await api.delete(`/admin/genres/${genre.id}`);
    showSuccess('Жанр удалён');
    await fetchGenres();
  } catch (error) {
    showError('Ошибка удаления');
  }
};

onMounted(() => {
  fetchGenres();
});
</script>

<style scoped>
.admin-genres-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  background: linear-gradient(135deg, #a855f7, #ec4899);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}

.actions {
  margin: 2rem 0 1.5rem;
}

.btn-primary {
  background: linear-gradient(135deg, #a855f7, #ec4899);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  color: white;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.genres-table-container {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 1rem;
  overflow-x: auto;
}

.genres-table {
  width: 100%;
  border-collapse: collapse;
}


.genres-table th,
.genres-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.genres-table th {
  color: #c084fc;
  font-weight: 600;
}

.genre-thumb {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 0.5rem;
}

.no-image {
  color: #6b7280;
}
.genres-table td {
  padding: 1rem;
  text-align: left;
  vertical-align: middle;          /* ✅ добавлено */
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
  align-items: center;             /* ✅ добавлено */
}

/* Опционально – чтобы граница была у всей строки, а не у ячейки,
   можно убрать border-bottom у td и добавить к tr: */
.genres-table tr {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.genres-table td {
  border-bottom: none;            /* если используете вариант с tr */
}
.actions-cell {
  display: flex;
  gap: 0.5rem;
}

.btn-edit, .btn-delete {
  background: none;
  border: none;
  padding: 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit {
  color: #60a5fa;
}
.btn-edit:hover {
  background: rgba(96, 165, 250, 0.2);
}
.btn-delete {
  color: #f87171;
}
.btn-delete:hover {
  background: rgba(248, 113, 113, 0.2);
}

.loading-cell, .empty-cell {
  text-align: center;
  padding: 2rem;
  color: #9ca3af;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #1a1a2e;
  border-radius: 1rem;
  padding: 2rem;
  width: 500px;
  max-width: 90%;
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  color: #9ca3af;
  cursor: pointer;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #d1d5db;
  font-weight: 500;
}

.form-group input[type="text"] {
  width: 100%;
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(168, 85, 247, 0.3);
  border-radius: 0.5rem;
  color: white;
}

.image-upload-area {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.current-image {
  position: relative;
  display: inline-block;
  width: 100px;
  height: 100px;
}

.current-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 0.5rem;
  border: 1px solid #a855f7;
}

.remove-image {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  font-size: 12px;
  cursor: pointer;
}

.upload-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  color: white;
  cursor: pointer;
}

.or {
  color: #6b7280;
}

.url-input {
  flex: 1;
  min-width: 180px;
}

.image-hint {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}
</style>