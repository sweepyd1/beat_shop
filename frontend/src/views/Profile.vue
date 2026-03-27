<template>
  <div class="profile">
    <h1>Личный кабинет</h1>

    <div v-if="loading" class="loading">Загрузка...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <template v-else>
      <div class="profile-tabs">
        <button :class="{ active: activeTab === 'info' }" @click="activeTab = 'info'">Мои данные</button>
        <button :class="{ active: activeTab === 'purchases' }" @click="activeTab = 'purchases'">Мои покупки</button>
        <button :class="{ active: activeTab === 'favorites' }" @click="activeTab = 'favorites'">Избранное</button>
        <button :class="{ active: activeTab === 'subscriptions' }" @click="activeTab = 'subscriptions'">Подписки</button>
      </div>

      <div class="profile-content">
        <!-- Информация о пользователе -->
        <div v-if="activeTab === 'info'" class="tab-pane">
          <div class="user-info" v-if="user">
            <div class="avatar">
              <img :src="avatarUrl" alt="" />
            </div>
            <div class="details">
              <p><strong>Имя:</strong> {{ user.full_name }}</p>
              <p><strong>Email:</strong> {{ user.email }}</p>
              <p><strong>Дата регистрации:</strong> {{ formatDate(user.registered_at) }}</p>
              <button class="btn-secondary edit-btn" @click="openEditModal">Редактировать</button>
            </div>
          </div>
        </div>

        <!-- Мои покупки -->
        <div v-if="activeTab === 'purchases'" class="tab-pane">
          <!-- ... -->
        </div>

        <!-- Избранное -->
        <div v-if="activeTab === 'favorites'" class="tab-pane">
          <div class="track-grid">
            <TrackCard
              v-for="fav in favorites"
              :key="fav.id"
              :track="fav.track"
            />
          </div>
        </div>

        <!-- Подписки -->
        <div v-if="activeTab === 'subscriptions'" class="tab-pane">
          <!-- ... -->
        </div>
      </div>
    </template>

    <!-- Модальное окно редактирования -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal">
        <h2>Редактирование профиля</h2>
        <form @submit.prevent="saveProfile" class="edit-form">
          <div class="avatar-upload">
            <div class="avatar-preview">
              <img :src="previewAvatar || avatarUrl" alt="Avatar preview" />
            </div>
            <label class="upload-label">
              <i class="fas fa-camera"></i>
              <span>Загрузить фото</span>
              <input type="file" accept="image/*" @change="handleAvatarChange" hidden />
            </label>
          </div>

          <div class="form-group">
            <label>Имя</label>
            <input type="text" v-model="editForm.full_name" required />
          </div>

          <div class="form-group">
            <label>Email</label>
            <input type="email" v-model="editForm.email" required />
          </div>

          <div class="modal-buttons">
            <button type="button" class="btn-cancel" @click="closeEditModal">Отмена</button>
            <button type="submit" class="btn-save" :disabled="saving">Сохранить</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import TrackCard from '../components/TrackCard.vue';
import { useProfile } from '../composables/useProfile';

const activeTab = ref('info');

const {
  user,
  purchases,
  favorites,
  subscriptions,
  loading,
  error,
  fetchAll,
  updateProfile,
  downloadTrack,
  unsubscribe,
} = useProfile();

// Модальное окно
const showEditModal = ref(false);
const editForm = ref({
  full_name: '',
  email: '',
  avatar_file: null,
});
const avatarFile = ref(null);
const previewAvatar = ref(null);
const saving = ref(false);

// Полный URL аватара с бэкенда
const avatarUrl = computed(() => {
  if (!user.value?.avatar) return '/default-avatar.png';
  if (user.value.avatar.startsWith('http')) return user.value.avatar;
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  return `${baseUrl}${user.value.avatar}`;
});

const openEditModal = () => {
  editForm.value = {
    full_name: user.value.full_name,
    email: user.value.email,
    avatar_file: null,
  };
  previewAvatar.value = null;
  showEditModal.value = true;
};

const closeEditModal = () => {
  showEditModal.value = false;
};

const handleAvatarChange = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  editForm.value.avatar_file = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    previewAvatar.value = e.target.result;
  };
  reader.readAsDataURL(file);
};

const saveProfile = async () => {
  saving.value = true;
  try {
    const formData = new FormData();
    formData.append('full_name', editForm.value.full_name);
    formData.append('email', editForm.value.email);
    if (editForm.value.avatar_file) {
      formData.append('avatar', editForm.value.avatar_file);
    }
    await updateProfile(formData);
    closeEditModal();
  } catch (err) {
    console.error('Save failed', err);
    alert('Не удалось сохранить изменения');
  } finally {
    saving.value = false;
  }
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU');
};

onMounted(() => {
  fetchAll();
});
</script>

<style scoped>
.profile {
  max-width: 1000px;
  margin: 2rem auto;
  padding: 0 2rem;
}

.profile-tabs {
  display: flex;
  gap: 0.5rem;
  margin: 2rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  padding-bottom: 0.5rem;
}

.profile-tabs button {
  background: none;
  border: none;
  color: #a0a0b0;
  padding: 0.5rem 1.5rem;
  font-size: 1rem;
  cursor: pointer;
  border-radius: 30px;
  transition: all 0.2s;
}

.profile-tabs button.active {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  color: white;
}

.tab-pane {
  background: rgba(255,255,255,0.02);
  border-radius: 20px;
  padding: 2rem;
  min-height: 300px;
}

.user-info {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.avatar img {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #a855f7;
}

.details p {
  margin: 0.5rem 0;
  font-size: 1.1rem;
}

.edit-btn {
  margin-top: 1rem;
  background: rgba(168,85,247,0.2);
  border: 1px solid #a855f7;
  color: #a855f7;
  padding: 0.5rem 1.5rem;
  border-radius: 40px;
  cursor: pointer;
  transition: all 0.2s;
}

.edit-btn:hover {
  background: #a855f7;
  color: white;
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: rgba(20,20,30,0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(168,85,247,0.3);
  padding: 2rem;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.5);
}

.modal h2 {
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
  text-align: center;
  background: linear-gradient(135deg, #fff, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.avatar-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.avatar-preview {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid #a855f7;
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(168,85,247,0.2);
  border: 1px solid #a855f7;
  padding: 0.5rem 1rem;
  border-radius: 40px;
  cursor: pointer;
  color: #a855f7;
  transition: all 0.2s;
}

.upload-label:hover {
  background: #a855f7;
  color: white;
}

.edit-form .form-group {
  margin-bottom: 1rem;
}

.edit-form label {
  display: block;
  margin-bottom: 0.5rem;
  color: #d0d0e0;
}

.edit-form input {
  width: 100%;
  background: rgba(0,0,0,0.3);
  border: 1px solid #2a2a3a;
  border-radius: 40px;
  padding: 0.8rem 1rem;
  color: white;
  font-size: 1rem;
}

.edit-form input:focus {
  outline: none;
  border-color: #a855f7;
  box-shadow: 0 0 0 3px rgba(168,85,247,0.2);
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-cancel, .btn-save {
  padding: 0.6rem 1.5rem;
  border-radius: 40px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-cancel {
  background: rgba(255,255,255,0.1);
  color: #a0a0b0;
}

.btn-cancel:hover {
  background: rgba(255,255,255,0.2);
}

.btn-save {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  color: white;
  box-shadow: 0 4px 15px rgba(168,85,247,0.3);
}

.btn-save:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(168,85,247,0.5);
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.track-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 2rem;
}

.empty {
  text-align: center;
  padding: 2rem;
}


</style>