<template>
  <div class="profile">
    <h1>Личный кабинет</h1>

    <div v-if="loading" class="loading">Загрузка...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <template v-else>
      <div class="profile-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="profile-content">
        <!-- Мои данные -->
        <div v-if="activeTab === 'info'" class="tab-pane">
          <div class="user-info">
            <div class="avatar">
              <img :src="avatarUrl" alt="avatar" />
            </div>
            <div class="details">
              <p><strong>Имя:</strong> {{ user.full_name }}</p>
              <p><strong>Email:</strong> {{ user.email }}</p>
              <p>
                <strong>Роль:</strong>
                {{ user.role === "author" ? "Автор" : "Покупатель" }}
              </p>
              <p>
                <strong>Дата регистрации:</strong>
                {{ formatDate(user.registered_at) }}
              </p>
              <button class="btn-secondary edit-btn" @click="openEditModal">
                Редактировать
              </button>
            </div>
          </div>
        </div>

        <!-- Мои покупки (только для покупателя) -->
        <div
          v-if="activeTab === 'purchases'"
          class="tab-pane"
        >
          <div v-if="purchases.length === 0" class="empty">
            <p>У вас пока нет покупок</p>
          </div>
          <div v-else class="purchases-list">
            <div
              v-for="purchase in purchases"
              :key="purchase.id"
              class="purchase-item"
            >
              <img
                :src="purchase.track.cover_url"
                :alt="purchase.track.title"
                class="purchase-cover"
              />
              <div class="purchase-info">
                <h3>{{ purchase.track.title }}</h3>
                <p>{{ purchase.track.author.full_name }}</p>
                <p class="purchase-date">
                  Куплено: {{ formatDate(purchase.purchase_date) }}
                </p>
                <div class="purchase-actions">
                  <button
                    @click="downloadTrack(purchase.track.id)"
                    class="download-btn"
                  >
                    <i class="fas fa-download"></i> Скачать
                  </button>
                  <button
                    @click="downloadContract(purchase.id)"
                    class="contract-btn"
                  >
                    <i class="fas fa-file-pdf"></i> Договор
                  </button>
                </div>
              </div>
              <div class="purchase-price">{{ purchase.amount }} ₽</div>
            </div>
          </div>
        </div>

        <!-- Избранное -->
        <div v-if="activeTab === 'favorites'" class="tab-pane">
          <div v-if="favorites.length === 0" class="empty">
            <p>У вас нет избранных треков</p>
          </div>
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
          <div v-if="subscriptions.length === 0" class="empty">
            <p>Вы ещё не подписаны на авторов</p>
          </div>
          <div class="authors-grid">
            <div v-for="sub in subscriptions" :key="sub.id" class="author-card">
              <img
                :src="sub.author.photo_url || '/default-avatar.png'"
                alt="author"
                class="author-avatar"
              />
              <h3>{{ sub.author.full_name }}</h3>
              <button @click="unsubscribe(sub.author.id)" class="unfollow-btn">
                Отписаться
              </button>
            </div>
          </div>
        </div>

        <!-- Студия продюсера (только для автора) -->
        <div
          v-if="activeTab === 'studio' && user.role === 'author'"
          class="tab-pane studio-pane"
        >
          <ArtistDashboard />
        </div>

        <!-- Мои треки (альтернативная вкладка для автора, можно оставить или убрать) -->
        <div
          v-if="activeTab === 'my-tracks' && user.role === 'author'"
          class="tab-pane"
        >
          <div class="section-header">
            <h2>Ваши биты</h2>
            <button class="add-track-btn" @click="activeTab = 'upload'">
              <i class="fas fa-plus"></i> Загрузить бит
            </button>
          </div>

          <div v-if="loading" class="loading">Загрузка...</div>

          <div v-else-if="authorTracks.length === 0" class="empty">
            <p>У вас ещё нет загруженных треков</p>
            <button class="upload-first-btn" @click="activeTab = 'upload'">
              Загрузить первый бит
            </button>
          </div>

          <div v-else class="track-grid">
            <div
              v-for="track in authorTracks"
              :key="track.id"
              class="track-card-wrapper"
            >
              <TrackCard :track="track" />
              <div class="track-actions">
                <button
                  @click="editTrack(track)"
                  class="edit-track-btn"
                  title="Редактировать"
                >
                  <i class="fas fa-edit"></i>
                </button>
                <button
                  @click="deleteTrack(track.id)"
                  class="delete-track-btn"
                  title="Удалить"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Загрузка трека (только для автора) -->
        <div
          v-if="activeTab === 'upload' && user.role === 'author'"
          class="tab-pane"
        >
          <div class="upload-form-container">
            <h2>Загрузка нового бита</h2>
            <form @submit.prevent="submitTrack" class="upload-form">
              <div class="form-group">
                <label>Название трека *</label>
                <input type="text" v-model="newTrack.title" required />
              </div>
              <div class="form-group">
                <label>Жанр *</label>
                <select v-model="newTrack.genre_id" required>
                  <option
                    v-for="genre in genres"
                    :key="genre.id"
                    :value="genre.id"
                  >
                    {{ genre.name }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>Цена (₽) *</label>
                <input
                  type="number"
                  v-model="newTrack.price"
                  min="0"
                  step="100"
                  required
                />
              </div>
              <div class="form-group">
                <label>BPM</label>
                <input type="number" v-model="newTrack.bpm" min="0" step="5" />
              </div>
              <div class="form-group">
                <label>Обложка *</label>
                <input
                  type="file"
                  accept="image/*"
                  @change="handleCoverChange"
                  required
                />
                <div v-if="coverPreview" class="cover-preview">
                  <img :src="coverPreview" alt="cover preview" />
                </div>
              </div>
              <div class="form-group">
                <label>MP3 файл *</label>
                <input
                  type="file"
                  accept="audio/mpeg"
                  @change="handleMp3Change"
                  required
                />
              </div>
              <button type="submit" class="submit-btn" :disabled="uploading">
                <i v-if="uploading" class="fas fa-spinner fa-spin"></i>
                <span v-else>Загрузить</span>
              </button>
            </form>
          </div>
        </div>
      </div>
    </template>

    <!-- Модальное окно редактирования профиля -->
    <div
      v-if="showEditModal"
      class="modal-overlay"
      @click.self="closeEditModal"
    >
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
              <input
                type="file"
                accept="image/*"
                @change="handleAvatarChange"
                hidden
              />
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
            <button type="button" class="btn-cancel" @click="closeEditModal">
              Отмена
            </button>
            <button type="submit" class="btn-save" :disabled="saving">
              Сохранить
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useAuthStore } from "../stores/auth";
import TrackCard from "../components/TrackCard.vue";
import ArtistDashboard from "../components/ArtistDashboard.vue";
import { useProfile } from "../composables/useProfile";
import api from "../api";

const authStore = useAuthStore();
const user = computed(() => authStore.user);

const {
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

// Дополнительные данные для автора
const authorTracks = ref([]);
const genres = ref([]);
const newTrack = ref({
  title: "",
  genre_id: null,
  price: 0,
  bpm: null,
  cover_file: null,
  mp3_file: null,
});
const coverPreview = ref(null);
const uploading = ref(false);

// Вкладки
const tabs = computed(() => {
  const baseTabs = [
    { key: "info", label: "Мои данные" },
    { key: "purchases", label: "Мои покупки" }, // всегда доступна
    { key: "favorites", label: "Избранное" },
    { key: "subscriptions", label: "Подписки" },
  ];
  if (user.value?.role === "author") {
    baseTabs.push(
      { key: "studio", label: "Студия продюсера" },
      { key: "my-tracks", label: "Мои треки" },
      { key: "upload", label: "Загрузить бит" }
    );
  }
  return baseTabs;
});
const activeTab = ref("info");

// Редактирование профиля
const showEditModal = ref(false);
const editForm = ref({ full_name: "", email: "", avatar_file: null });
const previewAvatar = ref(null);
const saving = ref(false);

const avatarUrl = computed(() => {
  if (!user.value?.avatar) return "/default-avatar.png";
  if (user.value.avatar.startsWith("http")) return user.value.avatar;
  const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
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
    formData.append("full_name", editForm.value.full_name);
    formData.append("email", editForm.value.email);
    if (editForm.value.avatar_file) {
      formData.append("avatar", editForm.value.avatar_file);
    }
    await updateProfile(formData);
    closeEditModal();
  } catch (err) {
    console.error("Save failed", err);
    alert("Не удалось сохранить изменения");
  } finally {
    saving.value = false;
  }
};

// Загрузка треков автора
const fetchAuthorTracks = async () => {
  try {
    const response = await api.get("/tracks/me");
    authorTracks.value = response.data;
  } catch (error) {
    console.error("Ошибка загрузки треков автора:", error);
  }
};

const fetchGenres = async () => {
  try {
    const { data } = await api.get("/genres");
    genres.value = data;
  } catch (err) {
    console.error("Failed to load genres", err);
  }
};

const handleCoverChange = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  newTrack.value.cover_file = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    coverPreview.value = e.target.result;
  };
  reader.readAsDataURL(file);
};

const handleMp3Change = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  newTrack.value.mp3_file = file;
};

const submitTrack = async () => {
  // Проверяем обязательные поля
  if (
    !newTrack.value.title ||
    !newTrack.value.genre_id ||
    !newTrack.value.price
  ) {
    alert("Заполните название, жанр и цену");
    return;
  }
  if (!newTrack.value.mp3_file) {
    alert("Выберите MP3 файл");
    return;
  }
  if (!newTrack.value.cover_file) {
    alert("Выберите обложку");
    return;
  }

  uploading.value = true;
  try {
    const formData = new FormData();
    formData.append("title", newTrack.value.title);
    formData.append("genre_id", newTrack.value.genre_id);
    formData.append("price", newTrack.value.price);
    if (newTrack.value.bpm) formData.append("bpm", newTrack.value.bpm);
    formData.append("cover", newTrack.value.cover_file);
    formData.append("mp3", newTrack.value.mp3_file);

    // Не указываем Content-Type – axios сам добавит multipart/form-data с boundary
    await api.post("/tracks", formData, {
      headers: { "Content-Type": undefined }, // сбросит глобальный заголовок
    });

    alert("Трек успешно загружен");
    // Очистка формы
    newTrack.value = {
      title: "",
      genre_id: null,
      price: 0,
      bpm: null,
      cover_file: null,
      mp3_file: null,
    };
    coverPreview.value = null;
    // Сброс полей выбора файлов
    const coverInput = document.querySelector('input[accept="image/*"]');
    const mp3Input = document.querySelector('input[accept="audio/mpeg"]');
    if (coverInput) coverInput.value = "";
    if (mp3Input) mp3Input.value = "";

    await fetchAuthorTracks();
    activeTab.value = "my-tracks";
  } catch (err) {
    console.error("Upload failed", err);
    const message = err.response?.data?.detail || "Ошибка загрузки трека";
    alert(message);
  } finally {
    uploading.value = false;
  }
};

const editTrack = (track) => {
  alert("Редактирование пока не реализовано");
};

const deleteTrack = async (trackId) => {
  if (!confirm("Удалить трек? Это действие нельзя отменить.")) return;
  try {
    await api.delete(`/tracks/${trackId}`);
    authorTracks.value = authorTracks.value.filter((t) => t.id !== trackId);
    alert("Трек удалён");
  } catch (err) {
    console.error("Delete failed", err);
    alert("Не удалось удалить трек");
  }
};

const downloadContract = async (purchaseId) => {
  try {
    const { data } = await api.get(`/purchase/${purchaseId}/contract`, {
      responseType: "blob",
    });
    const url = window.URL.createObjectURL(data);
    const link = document.createElement("a");
    link.href = url;
    link.download = `contract_${purchaseId}.pdf`;
    link.click();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    console.error("Failed to download contract", err);
    alert("Не удалось скачать договор");
  }
};

const formatDate = (dateString) => {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleDateString("ru-RU");
};

onMounted(async () => {
  await fetchAll();
  if (user.value?.role === "author") {
    await fetchAuthorTracks();
    await fetchGenres();
  }
});
</script>

<style scoped>
/* Общие стили */
.profile {
  max-width: 1000px;
  margin: 2rem auto;
  padding: 0 2rem;
}

.loading,
.error {
  text-align: center;
  padding: 2rem;
  color: #a0a0b0;
}

.profile-tabs {
  display: flex;
  gap: 0.5rem;
  margin: 2rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 0.5rem;
  flex-wrap: wrap;
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
  background: rgba(255, 255, 255, 0.02);
  border-radius: 20px;
  padding: 2rem;
  min-height: 300px;
}

.studio-pane {
  padding: 0;
  background: transparent;
}

/* Информация пользователя */
.user-info {
  display: flex;
  gap: 2rem;
  align-items: center;
  flex-wrap: wrap;
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
  background: rgba(168, 85, 247, 0.2);
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

/* Покупки */
.purchases-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.purchase-item {
  display: flex;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  padding: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.purchase-cover {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  object-fit: cover;
}

.purchase-info {
  flex: 1;
}

.purchase-info h3 {
  margin-bottom: 0.2rem;
}

.purchase-date {
  color: #a0a0b0;
  font-size: 0.8rem;
}

.purchase-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.download-btn,
.contract-btn {
  background: none;
  border: 1px solid #a855f7;
  color: #a855f7;
  padding: 0.3rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.download-btn:hover,
.contract-btn:hover {
  background: #a855f7;
  color: white;
}

.purchase-price {
  font-size: 1.2rem;
  font-weight: bold;
  color: #a855f7;
}

/* Избранное */
.track-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 2rem;
}

/* Подписки */
.authors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1.5rem;
}

.author-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 20px;
  padding: 1rem;
  text-align: center;
}

.author-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 0.5rem;
}

.unfollow-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  padding: 0.3rem 1rem;
  border-radius: 20px;
  color: white;
  cursor: pointer;
  margin-top: 0.5rem;
}

/* Мои треки */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.add-track-btn {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border: none;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 30px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.track-card-wrapper {
  position: relative;
}

.track-actions {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.track-card-wrapper:hover .track-actions {
  opacity: 1;
}

.edit-track-btn,
.delete-track-btn {
  background: rgba(0, 0, 0, 0.6);
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  color: white;
  cursor: pointer;
}

.edit-track-btn:hover {
  background: #a855f7;
}

.delete-track-btn:hover {
  background: #ff4444;
}

/* Форма загрузки */
.upload-form-container {
  max-width: 500px;
  margin: 0 auto;
}

.upload-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.upload-form .form-group {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.upload-form label {
  font-weight: 500;
  color: #d0d0e0;
}

.upload-form input,
.upload-form select {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid #2a2a3a;
  border-radius: 40px;
  padding: 0.6rem 1rem;
  color: white;
}

.cover-preview {
  margin-top: 0.5rem;
  width: 100px;
  height: 100px;
  border-radius: 12px;
  overflow: hidden;
}

.cover-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.submit-btn {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border: none;
  padding: 0.8rem;
  border-radius: 40px;
  color: white;
  font-weight: bold;
  cursor: pointer;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: rgba(20, 20, 30, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(168, 85, 247, 0.3);
  padding: 2rem;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
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
  background: rgba(168, 85, 247, 0.2);
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
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid #2a2a3a;
  border-radius: 40px;
  padding: 0.8rem 1rem;
  color: white;
  font-size: 1rem;
}

.edit-form input:focus {
  outline: none;
  border-color: #a855f7;
  box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.2);
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-cancel,
.btn-save {
  padding: 0.6rem 1.5rem;
  border-radius: 40px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: #a0a0b0;
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.2);
}

.btn-save {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  color: white;
  box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3);
}

.btn-save:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(168, 85, 247, 0.5);
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.empty {
  text-align: center;
  padding: 2rem;
  color: #a0a0b0;
}

@media (max-width: 768px) {
  .profile {
    padding: 0 1rem;
  }
  .track-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
  }
}
</style>
