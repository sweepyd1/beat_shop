<template>
  <div class="admin-container">
    <div class="header">
      <h1 class="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
        🎵 Админ панель
      </h1>
      <p class="text-gray-400">Управление треками</p>
    </div>

    <!-- Вкладки -->
    <div class="tabs">
      <button 
        :class="['tab', { active: activeTab === 'add' }]"
        @click="activeTab = 'add'"
      >
        <i class="fas fa-plus-circle"></i> Добавить трек
      </button>
      <button 
        :class="['tab', { active: activeTab === 'list' }]"
        @click="activeTab = 'list'"
      >
        <i class="fas fa-list"></i> Все треки ({{ tracks.length }})
      </button>
    </div>

    <!-- Добавление трека -->
    <div v-if="activeTab === 'add'" class="card add-card">
      <form @submit.prevent="submitTrack" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-6">
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">MP3 файл</label>
              <div 
                class="upload-area"
                :class="{ 'drag-over': dragOverMp3 }"
                @dragover.prevent="dragOverMp3 = true"
                @dragleave="dragOverMp3 = false"
                @drop.prevent="handleDrop($event, 'mp3')"
                @click="triggerFileInput('mp3')"
              >
                <input type="file" ref="mp3Input" accept=".mp3" @change="handleFileChange($event, 'mp3')" hidden />
                <div v-if="form.mp3_file" class="file-preview">
                  <i class="fas fa-music text-4xl text-purple-400"></i>
                  <span class="text-sm">{{ form.mp3_file.name }}</span>
                  <button type="button" @click.stop="clearFile('mp3')" class="text-red-400 hover:text-red-300">✖</button>
                </div>
                <div v-else class="upload-placeholder">
                  <i class="fas fa-cloud-upload-alt text-4xl text-gray-500 mb-2"></i>
                  <p>Перетащите MP3 или кликните для выбора</p>
                  <p class="text-xs text-gray-500">MP3, до 50 МБ</p>
                </div>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">Обложка</label>
              <div 
                class="upload-area"
                :class="{ 'drag-over': dragOverCover }"
                @dragover.prevent="dragOverCover = true"
                @dragleave="dragOverCover = false"
                @drop.prevent="handleDrop($event, 'cover')"
                @click="triggerFileInput('cover')"
              >
                <input type="file" ref="coverInput" accept="image/*" @change="handleFileChange($event, 'cover')" hidden />
                <div v-if="form.cover_file" class="file-preview">
                  <img :src="coverPreview" class="preview-image" />
                  <button type="button" @click.stop="clearFile('cover')" class="text-red-400 hover:text-red-300">✖</button>
                </div>
                <div v-else class="upload-placeholder">
                  <i class="fas fa-image text-4xl text-gray-500 mb-2"></i>
                  <p>Обложка (JPG/PNG)</p>
                </div>
              </div>
            </div>
          </div>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-300">Название *</label>
              <input v-model="form.title" type="text" required class="input" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-300">Жанр *</label>
              <select v-model="form.genre_id" required class="input">
                <option v-for="g in genres" :key="g.id" :value="g.id">{{ g.name }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-300">Автор *</label>
              <select v-model="form.author_id" required class="input">
                <option v-for="a in authors" :key="a.id" :value="a.id">{{ a.full_name }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-300">Цена (₽) *</label>
              <input v-model.number="form.price" type="number" step="0.01" required class="input" />
            </div>

          </div>
        </div>

        <div class="flex justify-end">
          <button type="submit" :disabled="loading" class="btn-primary">
            <i class="fas fa-upload mr-2"></i>
            {{ loading ? 'Загрузка...' : 'Добавить трек' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Список треков -->
    <div v-if="activeTab === 'list'" class="card">
      <div class="flex justify-between items-center mb-4">
        <input v-model="searchQuery" placeholder="Поиск по названию или автору..." class="search-input" />
        <select v-model="genreFilter" class="filter-select">
          <option value="">Все жанры</option>
          <option v-for="g in genres" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
      </div>

      <div v-if="tracksLoading" class="text-center py-12">
        <i class="fas fa-spinner fa-spin text-2xl text-purple-500"></i>
      </div>
      <div v-else class="track-grid">
        <div v-for="track in filteredTracks" :key="track.id" class="track-card">
          <div class="relative">
            <img :src="track.cover_url" class="track-cover" @error="e => e.target.src='/default-cover.jpg'" />
            <div class="action-buttons">
              <button @click.stop="openEditModal(track)" class="edit-btn" title="Редактировать">
                <i class="fas fa-edit"></i>
              </button>
              <button @click.stop="deleteTrack(track.id)" class="delete-btn" title="Удалить">
                <i class="fas fa-trash-alt"></i>
              </button>
            </div>
          </div>
          <div class="track-info">
            <h3 class="track-title">{{ track.title }}</h3>
            <p class="track-artist">{{ track.author?.full_name }}</p>
            <div class="track-meta">
              <span class="track-genre">{{ track.genre?.name }}</span>
              <span class="track-price">{{ track.price }} ₽</span>
            </div>
            <div class="track-stats">
              <span><i class="fas fa-play-circle"></i> {{ track.plays }}</span>
              <span><i class="fas fa-clock"></i> {{ formatDuration(track.duration_seconds) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования -->
    <teleport to="body">
      <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Редактирование трека</h2>
            <button @click="closeEditModal" class="close-btn">&times;</button>
          </div>
          <form @submit.prevent="submitEdit" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-6">
                <div>
                  <label class="block text-sm font-medium text-gray-300 mb-2">Новый MP3 (необязательно)</label>
                  <div class="upload-area" @click="$refs.editMp3Input.click()">
                    <input type="file" ref="editMp3Input" accept=".mp3" @change="onEditMp3Change" hidden />
                    <div v-if="editMp3File" class="file-preview">
                      <i class="fas fa-music text-4xl text-purple-400"></i>
                      <span class="text-sm">{{ editMp3File.name }}</span>
                    </div>
                    <div v-else class="upload-placeholder">
                      <i class="fas fa-music text-4xl text-gray-500 mb-2"></i>
                      <p>Заменить MP3 (опционально)</p>
                    </div>
                  </div>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-300 mb-2">Новая обложка</label>
                  <div class="upload-area" @click="$refs.editCoverInput.click()">
                    <input type="file" ref="editCoverInput" accept="image/*" @change="onEditCoverChange" hidden />
                    <div v-if="editCoverPreview" class="file-preview">
                      <img :src="editCoverPreview" class="preview-image" />
                    </div>
                    <div v-else class="upload-placeholder">
                      <i class="fas fa-image text-4xl text-gray-500 mb-2"></i>
                      <p>Заменить обложку (опционально)</p>
                    </div>
                  </div>
                </div>
              </div>

              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-300">Название *</label>
                  <input v-model="editForm.title" type="text" required class="input" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-300">Жанр *</label>
                  <select v-model="editForm.genre_id" required class="input">
                    <option v-for="g in genres" :key="g.id" :value="g.id">{{ g.name }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-300">Автор *</label>
                  <select v-model="editForm.author_id" required class="input">
                    <option v-for="a in authors" :key="a.id" :value="a.id">{{ a.full_name }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-300">Цена (₽) *</label>
                  <input v-model.number="editForm.price" type="number" step="0.01" required class="input" />
                </div>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-300">BPM</label>
                    <input v-model.number="editForm.bpm" type="number" class="input" />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-300">Длительность (сек)</label>
                    <input v-model.number="editForm.duration_seconds" type="number" class="input" />
                  </div>
                </div>
              </div>
            </div>

            <div class="flex justify-end">
              <button type="submit" :disabled="editLoading" class="btn-primary">
                <i class="fas fa-save mr-2"></i>
                {{ editLoading ? 'Сохранение...' : 'Сохранить изменения' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '@/api';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import { showError, showSuccess } from '@/utils/alert';  // <-- импорт
const authStore = useAuthStore();
const router = useRouter();

if (authStore.user?.role !== 'admin') {
  router.replace('/');
}

const activeTab = ref('list');
const dragOverMp3 = ref(false);
const dragOverCover = ref(false);

const form = ref({
  title: '',
  genre_id: null,
  author_id: null,
  price: 0,
  bpm: null,
  duration_seconds: null,
  mp3_file: null,
  cover_file: null
});

const editingTrackId = ref(null);
const editForm = ref({
  title: '',
  genre_id: null,
  author_id: null,
  price: 0,
  bpm: null,
  duration_seconds: null,
});
const editCoverPreview = ref(null);
const editCoverFile = ref(null);
const editMp3File = ref(null);
const editLoading = ref(false);
const showEditModal = ref(false);

const genres = ref([]);
const authors = ref([]);
const tracks = ref([]);
const loading = ref(false);
const tracksLoading = ref(false);
const searchQuery = ref('');
const genreFilter = ref('');

const mp3Input = ref(null);
const coverInput = ref(null);

const coverPreview = computed(() => {
  if (form.value.cover_file) {
    return URL.createObjectURL(form.value.cover_file);
  }
  return null;
});

const filteredTracks = computed(() => {
  let result = tracks.value;
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(t =>
      t.title.toLowerCase().includes(q) ||
      t.author?.full_name.toLowerCase().includes(q)
    );
  }
  if (genreFilter.value) {
    result = result.filter(t => t.genre_id === genreFilter.value);
  }
  return result;
});

const triggerFileInput = (type) => {
  if (type === 'mp3') mp3Input.value.click();
  else coverInput.value.click();
};

const handleFileChange = (event, type) => {
  const file = event.target.files[0];
  if (file) {
    if (type === 'mp3' && !file.name.endsWith('.mp3')) {
      showError('Файл должен быть MP3');
      return;
    }
    if (type === 'cover' && !['image/jpeg','image/png','image/jpg'].includes(file.type)) {
      showError('Обложка должна быть JPG или PNG');
      return;
    }
    form.value[`${type}_file`] = file;
  }
};

const handleDrop = (event, type) => {
  const file = event.dataTransfer.files[0];
  if (type === 'mp3') {
    if (file && file.name.endsWith('.mp3')) {
      form.value.mp3_file = file;
      dragOverMp3.value = false;
    } else showError('Пожалуйста, перетащите MP3 файл');
  } else if (type === 'cover') {
    if (file && file.type.startsWith('image/')) {
      form.value.cover_file = file;
      dragOverCover.value = false;
    } else showError('Пожалуйста, перетащите изображение');
  }
};

const clearFile = (type) => {
  form.value[`${type}_file`] = null;
  if (type === 'mp3') mp3Input.value.value = '';
  else coverInput.value.value = '';
};

const submitTrack = async () => {
  if (!form.value.mp3_file || !form.value.cover_file) {
    showError('Выберите MP3 и обложку');
    return;
  }
  loading.value = true;
  const fd = new FormData();
  fd.append('title', form.value.title);
  fd.append('genre_id', form.value.genre_id);
  fd.append('author_id', form.value.author_id);
  fd.append('price', form.value.price);
  if (form.value.bpm) fd.append('bpm', form.value.bpm);
  if (form.value.duration_seconds) fd.append('duration_seconds', form.value.duration_seconds);
  fd.append('mp3_file', form.value.mp3_file);
  fd.append('cover', form.value.cover_file);

  try {
    await api.post('/admin/tracks', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    showSuccess('Трек успешно добавлен');
    form.value = { title: '', genre_id: null, author_id: null, price: 0, bpm: null, duration_seconds: null, mp3_file: null, cover_file: null };
    if (coverPreview.value) URL.revokeObjectURL(coverPreview.value);
    fetchTracks();
    activeTab.value = 'list';
  } catch (err) {
    console.error(err);
    showError(err.response?.data?.detail || 'Ошибка добавления трека');
  } finally {
    loading.value = false;
  }
};

// Редактирование
const openEditModal = async (track) => {
  try {
    const { data } = await api.get(`/admin/tracks/${track.id}`);
    editingTrackId.value = data.id;
    editForm.value = {
      title: data.title,
      genre_id: data.genre.id,
      author_id: data.author.id,
      price: data.price,
      bpm: data.bpm || null,
      duration_seconds: data.duration_seconds || null,
    };
    editCoverFile.value = null;
    editMp3File.value = null;
    editCoverPreview.value = data.cover_url || null;
    showEditModal.value = true;
  } catch (err) {
    console.error('Ошибка загрузки трека для редактирования:', err);
    showError('Не удалось загрузить данные трека');
  }
};

const onEditCoverChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    if (!file.type.startsWith('image/')) {
      alert('Выберите изображение');
      return;
    }
    editCoverFile.value = file;
    editCoverPreview.value = URL.createObjectURL(file);
  }
};

const onEditMp3Change = (event) => {
  const file = event.target.files[0];
  if (file && file.name.endsWith('.mp3')) {
    editMp3File.value = file;
  } else if (file) {
    alert('Выберите MP3 файл');
  }
};

const submitEdit = async () => {
  editLoading.value = true;
  const fd = new FormData();
  fd.append('title', editForm.value.title);
  fd.append('genre_id', editForm.value.genre_id);
  fd.append('author_id', editForm.value.author_id);
  fd.append('price', editForm.value.price);
  if (editForm.value.bpm) fd.append('bpm', editForm.value.bpm);
  if (editForm.value.duration_seconds) fd.append('duration_seconds', editForm.value.duration_seconds);
  if (editCoverFile.value) fd.append('cover', editCoverFile.value);
  if (editMp3File.value) fd.append('mp3_file', editMp3File.value);

  try {
    await api.put(`/admin/tracks/${editingTrackId.value}`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    showSuccess('Трек обновлён');
    showEditModal.value = false;
    fetchTracks();
  } catch (err) {
    console.error(err);
    showError(err.response?.data?.detail || 'Ошибка обновления');
  } finally {
    editLoading.value = false;
  }
};

const closeEditModal = () => {
  showEditModal.value = false;
  if (editCoverPreview.value && editCoverFile.value) {
    URL.revokeObjectURL(editCoverPreview.value);
  }
};

const fetchGenres = async () => {
  try {
    const res = await api.get('/genres');
    genres.value = res.data;
  } catch (err) { console.error(err); }
};

const fetchAuthors = async () => {
  try {
    const res = await api.get('/authors');
    authors.value = res.data;
  } catch (err) { console.error(err); }
};

const fetchTracks = async () => {
  tracksLoading.value = true;
  try {
    const res = await api.get('/admin/tracks');  // ← изменено на /list
    tracks.value = res.data;
  } catch (err) {
    console.error(err);
  } finally {
    tracksLoading.value = false;
  }
};

const deleteTrack = async (id) => {
  if (!confirm('Удалить трек? Это действие необратимо.')) return;
  try {
    await api.delete(`/admin/tracks/${id}`);
    fetchTracks();
  } catch (err) { console.error(err); alert('Ошибка удаления'); }
};

const formatDuration = (seconds) => {
  if (!seconds) return '—';
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2,'0')}`;
};

onMounted(() => {
  fetchGenres();
  fetchAuthors();
  fetchTracks();
});
</script>

<style scoped>

.admin-container {
  max-width: 1400px;
  margin: 2rem auto;
  padding: 0 1rem;
}
.header {
  text-align: center;
  margin-bottom: 2rem;
}
.tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  padding-bottom: 0.5rem;
}
.tab {
  background: none;
  border: none;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  cursor: pointer;
  color: #a0a0b0;
  transition: all 0.2s;
  border-radius: 2rem;
}
.tab i {
  margin-right: 0.5rem;
}
.tab.active {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  color: white;
}
.card {
  background: rgba(20,20,30,0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(168,85,247,0.2);
  border-radius: 1.5rem;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.add-card {
  max-width: 1000px;
  margin: 0 auto;
}
.input, .search-input, .filter-select {
  width: 100%;
  background: rgba(0,0,0,0.4);
  border: 1px solid #2a2a3a;
  border-radius: 2rem;
  padding: 0.6rem 1rem;
  color: white;
  font-size: 0.9rem;
  transition: all 0.2s;
}
.input:focus, .search-input:focus, .filter-select:focus {
  outline: none;
  border-color: #a855f7;
  box-shadow: 0 0 0 2px rgba(168,85,247,0.2);
}
.upload-area {
  background: rgba(0,0,0,0.3);
  border: 2px dashed rgba(168,85,247,0.4);
  border-radius: 1rem;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}
.upload-area.drag-over {
  border-color: #a855f7;
  background: rgba(168,85,247,0.1);
}
.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #a0a0b0;
}
.file-preview {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}
.preview-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 0.5rem;
}
.btn-primary {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 2rem;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: inline-flex;
  align-items: center;
}
.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(168,85,247,0.4);
}
.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.track-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}
.track-card {
  background: rgba(255,255,255,0.05);
  border-radius: 1rem;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}
.track-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.3);
}
.track-cover {
  width: 100%;
  height: 200px;
  object-fit: cover;
}
.track-info {
  padding: 1rem;
}
.track-title {
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.track-artist {
  font-size: 0.85rem;
  color: #a0a0b0;
  margin-bottom: 0.5rem;
}
.track-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}
.track-genre {
  background: rgba(168,85,247,0.2);
  padding: 0.2rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.7rem;
}
.track-price {
  font-weight: 600;
  color: #a855f7;
}
.track-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: #a0a0b0;
}

/* Кнопки действий (редактировать/удалить) */
.action-buttons {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s;
}
.track-card:hover .action-buttons {
  opacity: 1;
}
.edit-btn,
.delete-btn {
  background: rgba(0,0,0,0.7);
  border: none;
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}
.edit-btn:hover {
  background: #3b82f6;
}
.delete-btn:hover {
  background: #ff4d4d;
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background: #1e1e2e;
  border: 1px solid rgba(168,85,247,0.2);
  border-radius: 1.5rem;
  padding: 2rem;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.modal-header h2 {
  font-size: 1.5rem;
  color: white;
}
.close-btn {
  background: none;
  border: none;
  color: #a0a0b0;
  font-size: 2rem;
  cursor: pointer;
}
.close-btn:hover {
  color: white;
}

.search-input, .filter-select {
  width: auto;
  min-width: 200px;
}
@media (max-width: 640px) {
  .track-grid {
    grid-template-columns: 1fr}
  }
</style>