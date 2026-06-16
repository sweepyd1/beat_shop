<template>
  <div class="profile">
    <!-- Hero section -->
    <div class="hero-section">
      <div class="hero-background"></div>
      <div class="hero-content">
        <div class="avatar-large">
          <img :src="avatarUrl" />
          <button class="edit-avatar-btn" @click="openEditModal">
            <i class="fas fa-camera"></i>
          </button>
        </div>
        <div class="hero-info">
          <h1>{{ user.full_name }}</h1>
          <p class="role-badge">
  {{ user.role === 'admin' ? 'Администратор' : user.role === 'author' ? 'Автор' : 'Покупатель' }}
</p>
          <div class="stats">
            <div class="stat">
              <span class="stat-value">{{ tracksCount }}</span>
              <span class="stat-label">Треков</span>
            </div>
            <!-- <div class="stat">
              <span class="stat-value">{{ user.followers_count || 0 }}</span>
              <span class="stat-label">Подписчиков</span>
            </div> -->
            <div class="stat">
              <span class="stat-value">{{ purchasesCount }}</span>
              <span class="stat-label">Покупок</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs-container">
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <span class="tab-icon" v-html="getTabIcon(tab.key)"></span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </div>
    </div>

    <!-- Tab content -->
    <div class="content-container">
      <transition-group name="fade" mode="out-in" tag="div">
        <!-- Мои данные -->
        <div v-if="activeTab === 'info'" class="tab-pane info-pane" key="info">
          <div class="info-card glass-card">
            <div class="info-grid">
              <div class="info-item">
                <i class="fas fa-envelope"></i>
                <div>
                  <label>Email</label>
                  <p>{{ user.email }}</p>
                </div>
              </div>
              <div class="info-item">
                <i class="fas fa-calendar-alt"></i>
                <div>
                  <label>Дата регистрации</label>
                  <p>{{ formatDate(user.registered_at) }}</p>
                </div>
              </div>
              <div class="info-item">
                <i class="fas fa-id-card"></i>
                <div>
                  <label>Роль</label>
                  <p>{{ user.role === 'admin' ? 'Администратор' : user.role === 'author' ? 'Автор' : 'Покупатель' }}</p>
                </div>
              </div>
            </div>
            <button class="btn-primary edit-profile-btn" @click="openEditModal">
              <i class="fas fa-user-edit"></i> Редактировать профиль
            </button>
          </div>
        </div>

        <!-- Мои покупки -->
        <div v-if="activeTab === 'purchases'" class="tab-pane" key="purchases">
          <div v-if="purchases.length === 0" class="empty-state">
            <i class="fas fa-shopping-cart empty-icon"></i>
            <p>У вас пока нет покупок</p>
            <router-link to="/search" class="btn-outline"
              >Перейти в каталог</router-link
            >
          </div>
          <div v-else class="purchases-grid">
            <div
              v-for="purchase in purchases"
              :key="purchase.id"
              class="purchase-card glass-card"
            >
              <div class="purchase-image">
                <img
                  :src="getImageUrl(purchase.track.cover_url)"
                  :alt="purchase.track.title"
                />
              </div>
              <div class="purchase-details">
                <h3>{{ purchase.track.title }}</h3>
                <p class="artist">{{ purchase.track.author.full_name }}</p>
                <p class="date">
                  Куплено: {{ formatDate(purchase.purchase_date) }}
                </p>
                <div class="purchase-actions">
                  <button
                    @click="downloadTrack(purchase.track.id)"
                    class="btn-icon"
                  >
                    <i class="fas fa-download"></i> Скачать
                  </button>
                  <button
                    @click="downloadContract(purchase.id)"
                    class="btn-icon"
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
        <div v-if="activeTab === 'favorites'" class="tab-pane" key="favorites">
          <div v-if="favorites.length === 0" class="empty-state">
            <i class="fas fa-heart empty-icon"></i>
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
        <!-- <div
          v-if="activeTab === 'subscriptions'"
          class="tab-pane"
          key="subscriptions"
        >
          <div v-if="subscriptions.length === 0" class="empty-state">
            <i class="fas fa-users empty-icon"></i>
            <p>Вы ещё не подписаны на авторов</p>
          </div>
          <div class="authors-grid">
            <div
              v-for="sub in subscriptions"
              :key="sub.id"
              class="author-card glass-card"
            >
              <div class="author-avatar-wrapper">
                <img
                  :src="sub.author.photo_url || '/default-avatar.png'"
                  alt="author"
                />
              </div>
              <h3>{{ sub.author.full_name }}</h3>
              <button @click="unsubscribe(sub.author.id)" class="btn-unfollow">
                <i class="fas fa-user-minus"></i> Отписаться
              </button>
            </div>
          </div>
        </div> -->

        <!-- Студия продюсера -->
        <div
          v-if="activeTab === 'studio' && user.role === 'author'"
          class="tab-pane studio-pane"
          key="studio"
        >
          <ArtistDashboard />
        </div>

        <!-- Мои треки -->
        <div
          v-if="activeTab === 'my-tracks' && user.role === 'author'"
          class="tab-pane"
          key="my-tracks"
        >
          <div class="section-header">
            <h2>Ваши биты</h2>
            <button class="btn-primary" @click="activeTab = 'upload'">
              <i class="fas fa-plus"></i> Загрузить бит
            </button>
          </div>

          <div v-if="loading" class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
          </div>

          <div v-else-if="authorTracks.length === 0" class="empty-state">
            <i class="fas fa-music empty-icon"></i>
            <p>У вас ещё нет загруженных треков</p>
            <button class="btn-primary" @click="activeTab = 'upload'">
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
                  class="btn-action edit"
                  title="Редактировать"
                >
                  <i class="fas fa-edit"></i>
                </button>
                <button
                  @click="deleteTrack(track.id)"
                  class="btn-action delete"
                  title="Удалить"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Загрузка трека -->
        <div
          v-if="activeTab === 'upload' && user.role === 'author'"
          class="tab-pane"
          key="upload"
        >
          <div class="upload-form-container glass-card">
            <h2>Загрузка нового бита</h2>
            <form @submit.prevent="submitTrack" class="upload-form">
              <div class="form-group">
                <label>Название трека *</label>
                <input
                  type="text"
                  v-model="newTrack.title"
                  required
                  placeholder="Введите название"
                />
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
              <div class="form-row">
                <div class="form-group">
                  <label>Цена (₽) *</label>
                  <input
                    type="number"
                    v-model="newTrack.price"
                    min="0"
                    max="10000000"
                    
                    step="1"
                    required
                  />
                </div>
                <!-- <div class="form-group">
                  <label>BPM</label>
                  <input
                    type="number"
                    v-model="newTrack.bpm"
                    min="0"
                    step="5"
                  />
                </div> -->
              </div>
              <div class="form-group file-group">
                <label>Обложка *</label>
                <div class="file-input">
                  <input
                    type="file"
                    accept="image/*"
                    @change="handleCoverChange"
                    id="cover-upload"
                  />
                  <label for="cover-upload" class="file-label">
                    <i class="fas fa-cloud-upload-alt"></i> Выберите файл
                  </label>
                  <span v-if="newTrack.cover_file" class="file-name">{{
                    newTrack.cover_file.name
                  }}</span>
                </div>
                <div v-if="coverPreview" class="cover-preview">
                  <img :src="coverPreview" alt="cover preview" />
                </div>
              </div>
              <div class="form-group file-group">
                <label>MP3 файл *</label>
                <div class="file-input">
                  <input
                    type="file"
                    accept="audio/mpeg"
                    @change="handleMp3Change"
                    id="mp3-upload"
                  />
                  <label for="mp3-upload" class="file-label">
                    <i class="fas fa-cloud-upload-alt"></i> Выберите файл
                  </label>
                  <span v-if="newTrack.mp3_file" class="file-name">{{
                    newTrack.mp3_file.name
                  }}</span>
                </div>
              </div>
              <button
                type="submit"
                class="btn-primary submit-btn"
                :disabled="uploading"
              >
                <i v-if="uploading" class="fas fa-spinner fa-spin"></i>
                <span v-else>Загрузить</span>
              </button>
            </form>
          </div>
        </div>
      </transition-group>
    </div>

    <!-- Modal for profile edit -->
    <transition name="modal-fade">
      <div
        v-if="showEditModal"
        class="modal-overlay"
        @click.self="closeEditModal"
      >
        <div class="modal glass-card">
          <button class="modal-close" @click="closeEditModal">&times;</button>
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
              <button
                type="button"
                class="btn-secondary"
                @click="closeEditModal"
              >
                Отмена
              </button>
              <button type="submit" class="btn-primary" :disabled="saving">
                <i v-if="saving" class="fas fa-spinner fa-spin"></i>
                <span v-else>Сохранить</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>
    <transition name="modal-fade">
      <div
        v-if="showEditTrackModal"
        class="modal-overlay"
        @click.self="closeEditTrackModal"
      >
        <div class="modal glass-card" style="max-width: 600px">
          <button class="modal-close" @click="closeEditTrackModal">
            &times;
          </button>
          <h2>Редактирование трека</h2>
          <form @submit.prevent="saveTrackEdit" class="edit-form">
            <div class="form-group">
              <label>Название трека *</label>
              <input type="text" v-model="editTrackForm.title" required />
            </div>
            <div class="form-group">
              <label>Жанр *</label>
              <select v-model="editTrackForm.genre_id" required>
                <option
                  v-for="genre in genres"
                  :key="genre.id"
                  :value="genre.id"
                >
                  {{ genre.name }}
                </option>
              </select>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Цена (₽) *</label>
                <input
                  type="number"
                  v-model="editTrackForm.price"
                  min="0"
                  step="1"
                  required
                />
              </div>
              <div class="form-group">
                <label>BPM</label>
                <input
                  type="number"
                  v-model="editTrackForm.bpm"
                  min="0"
                  step="1"
                />
              </div>
            </div>
            <div class="form-group file-group">
              <label>Обложка</label>
              <div class="file-input">
                <input
                  type="file"
                  id="edit-cover-input"
                  accept="image/*"
                  @change="handleEditCoverChange"
                />
                <label for="edit-cover-input" class="file-label">
                  <i class="fas fa-cloud-upload-alt"></i> Заменить обложку
                </label>
                <span v-if="editTrackForm.cover_file" class="file-name">{{
                  editTrackForm.cover_file.name
                }}</span>
              </div>
              <div v-if="editCoverPreview" class="cover-preview">
                <img :src="editCoverPreview" alt="cover preview" />
              </div>
            </div>
            <div class="form-group file-group">
              <label>MP3 файл</label>
              <div class="file-input">
                <input
                  type="file"
                  id="edit-mp3-input"
                  accept="audio/mpeg"
                  @change="handleEditMp3Change"
                />
                <label for="edit-mp3-input" class="file-label">
                  <i class="fas fa-cloud-upload-alt"></i> Заменить трек
                </label>
                <span v-if="editTrackForm.mp3_file" class="file-name">{{
                  editTrackForm.mp3_file.name
                }}</span>
              </div>
            </div>
            <div class="modal-buttons">
              <button
                type="button"
                class="btn-secondary"
                @click="closeEditTrackModal"
              >
                Отмена
              </button>
              <button
                type="submit"
                class="btn-primary"
                :disabled="editUploading"
              >
                <i v-if="editUploading" class="fas fa-spinner fa-spin"></i>
                <span v-else>Сохранить</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>
  </div>
  <!-- Modal for track edit -->
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useAuthStore } from "../stores/auth";
import TrackCard from "../components/TrackCard.vue";
import ArtistDashboard from "../components/ArtistDashboard.vue";
import { useProfile } from "../composables/useProfile";
import api from "../api";
import router from "@/router";
import { showError, showSuccess } from "@/utils/alert"; // <-- импорт
const authStore = useAuthStore();
const user = computed(() => authStore.user);

const ALLOWED_IMAGE_TYPES = [
  "image/jpeg",
  "image/jpg",
  "image/png",
  "image/gif",
  "image/webp",
];
const MAX_MP3_SIZE = 50 * 1024 * 1024;   // 50 МБ для MP3
const MAX_COVER_SIZE = 5 * 1024 * 1024;  // 5 МБ для обложки
const MAX_AVATAR_SIZE = 2 * 1024 * 1024; // 2 МБ для аватара
const ALLOWED_AUDIO_TYPES = ["audio/mpeg", "audio/mp3"]; // audio/mpeg — это и есть MP3
const showEditTrackModal = ref(false);
const editingTrack = ref(null);
const editTrackForm = ref({
  title: "",
  genre_id: null,
  price: 0,
  bpm: null,
  cover_file: null,
  mp3_file: null,
});
const editCoverPreview = ref(null);
const editUploading = ref(false);
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
// Открыть модалку с данными трека

// Закрыть модалку
const closeEditTrackModal = () => {
  showEditTrackModal.value = false;
  editingTrack.value = null;
  editTrackForm.value = {
    title: "",
    genre_id: null,
    price: 0,
    bpm: null,
    cover_file: null,
    mp3_file: null,
  };
  editCoverPreview.value = null;
  // очистить input файлы, чтобы можно было выбрать заново
  const coverInput = document.getElementById("edit-cover-input");
  const mp3Input = document.getElementById("edit-mp3-input");
  if (coverInput) coverInput.value = "";
  if (mp3Input) mp3Input.value = "";
};

// Обработчики выбора новых файлов
const handleEditCoverChange = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
    showError("Неподдерживаемый формат изображения");
    event.target.value = "";
    return;
  }
  editTrackForm.value.cover_file = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    editCoverPreview.value = e.target.result;
  };
  reader.readAsDataURL(file);
};

const handleEditMp3Change = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  if (!ALLOWED_AUDIO_TYPES.includes(file.type)) {
    showError("Неподдерживаемый аудиоформат. Загрузите MP3.");
    event.target.value = "";
    return;
  }
  editTrackForm.value.mp3_file = file;
};

// Сохранить изменения трека
const saveTrackEdit = async () => {
  if (!editingTrack.value) return;
  if (
    !editTrackForm.value.title ||
    !editTrackForm.value.genre_id ||
    editTrackForm.value.price === undefined
  ) {
    showError("Заполните название, жанр и цену");
    return;
  }

  editUploading.value = true;
  try {
    const formData = new FormData();
    formData.append("title", editTrackForm.value.title);
    formData.append("genre_id", editTrackForm.value.genre_id);
    formData.append("price", editTrackForm.value.price);
    if (editTrackForm.value.bpm)
      formData.append("bpm", editTrackForm.value.bpm);
    if (editTrackForm.value.cover_file)
      formData.append("cover", editTrackForm.value.cover_file);
    if (editTrackForm.value.mp3_file)
      formData.append("mp3", editTrackForm.value.mp3_file);

    await api.put(`/tracks/${editingTrack.value.id}`, formData, {
      headers: { "Content-Type": undefined },
    });

    showSuccess("Трек обновлён");
    closeEditTrackModal();
    await fetchAuthorTracks(); // обновить список треков
  } catch (err) {
    console.error("Update failed", err);
    const message = err.response?.data?.detail || "Ошибка обновления трека";
    showError(message);
  } finally {
    editUploading.value = false;
  }
};
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
    { key: "purchases", label: "Мои покупки" },
    { key: "favorites", label: "Избранное" },
    // { key: "subscriptions", label: "Подписки" },
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
  if (!user.value?.avatar_url) return "/default-avatar.png";
  if (user.value.avatar_url.startsWith("http")) return user.value.avatar_url;
  const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
  return `${baseUrl}${user.value.avatar_url}`;
});

const getTabIcon = (tabKey) => {
  const icons = {
    info: '<i class="fas fa-user"></i>',
    purchases: '<i class="fas fa-shopping-cart"></i>',
    favorites: '<i class="fas fa-heart"></i>',
    subscriptions: '<i class="fas fa-users"></i>',
    studio: '<i class="fas fa-chalkboard-teacher"></i>',
    "my-tracks": '<i class="fas fa-music"></i>',
    upload: '<i class="fas fa-cloud-upload-alt"></i>',
  };
  return icons[tabKey] || '<i class="fas fa-circle"></i>';
};
const tracksCount = computed(() => {
  if (user.value?.role === "author") {
    return authorTracks.value.length;
  }
  return 0;
});

const purchasesCount = computed(() => purchases.value.length);
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
    await authStore.fetchUser();
    closeEditModal();
  } catch (err) {
    console.error("Save failed", err);
    showError("Не удалось сохранить изменения");
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
  if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
    showError(
      "Неподдерживаемый формат изображения. Используйте JPG, PNG, GIF или WebP."
    );
     if (file.size > MAX_COVER_SIZE) {
        showError(`❌ Обложка слишком большая (${formatSize(file.size)}). Максимум: ${formatSize(MAX_COVER_SIZE)}`);
        event.target.value = "";
        return;
    }
    // Очищаем input, чтобы можно было выбрать заново
    event.target.value = "";
    return;
  }
  newTrack.value.cover_file = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    coverPreview.value = e.target.result;
  };
  reader.readAsDataURL(file);
};
const formatSize = (bytes) => {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} КБ`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} МБ`;
};
const handleMp3Change = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  if (!ALLOWED_AUDIO_TYPES.includes(file.type)) {
    showError("Неподдерживаемый аудиоформат. Пожалуйста, загрузите MP3 файл.");
    event.target.value = "";
    return;
  }
   if (file.size > MAX_MP3_SIZE) {
        showError(`❌ Файл слишком большой (${formatSize(file.size)}). Максимум: ${formatSize(MAX_MP3_SIZE)}`);
        event.target.value = "";
        return;
    }
  newTrack.value.mp3_file = file;
};

const submitTrack = async () => {
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

    await api.post("/tracks", formData, {
      headers: { "Content-Type": undefined },
    });

    showSuccess("Трек успешно загружен");
    newTrack.value = {
      title: "",
      genre_id: null,
      price: 0,
      bpm: null,
      cover_file: null,
      mp3_file: null,
    };
    coverPreview.value = null;
    const coverInput = document.querySelector('input[accept="image/*"]');
    const mp3Input = document.querySelector('input[accept="audio/mpeg"]');
    if (coverInput) coverInput.value = "";
    if (mp3Input) mp3Input.value = "";

    await fetchAuthorTracks();
    activeTab.value = "my-tracks";
  } catch (err) {
    console.error("Upload failed", err);
    const message = err.response?.data?.detail || "Ошибка загрузки трека";
    showError(message);
  } finally {
    uploading.value = false;
  }
};

const editTrack = (track) => {
  if (track?.sales > 0 || track?.is_exclusive_sold) {
    showError("❌ Этот трек уже был продан. Редактирование невозможно.");
    return;
  }
  editingTrack.value = track;
  editTrackForm.value = {
    title: track.title,
    genre_id: track.genre?.id || null,
    price: track.price,
    bpm: track.bpm || null,
    cover_file: null,
    mp3_file: null,
  };
  editCoverPreview.value = track.cover_url
    ? getImageUrl(track.cover_url)
    : null;
  showEditTrackModal.value = true;
};

const deleteTrack = async (trackId) => {
  const track = authorTracks.value.find((t) => t.id === trackId);
  console.log(track)
  console.log(track.sales)
  // Проверяем продажи на фронтенде для быстрого UX
  if (track?.sales > 0 || track?.is_exclusive_sold) {
    showError("❌ Этот трек уже был продан. Удаление невозможно.");
    return;
  }
  if (!confirm("Удалить трек? Это действие нельзя отменить.")) return;
  try {
    await api.delete(`/tracks/${trackId}`);
    authorTracks.value = authorTracks.value.filter((t) => t.id !== trackId);
    showSuccess("Трек удалён");
  } catch (err) {
    console.error("Delete failed", err);
    showError("Не удалось удалить трек");
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
    showError("Не удалось скачать договор");
  }
};
const getImageUrl = (url) => {
  if (!url) return "/default-cover.jpg";
  if (url.startsWith("http")) return url;
  const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
  return `${baseUrl}${url}`;
};
const formatDate = (dateString) => {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleDateString("ru-RU", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
};

onMounted(async () => {
  if (!user.value) {
    router.push("/");
    return;
  }
  await fetchAll();

  if (user.value?.role === "author") {
    await fetchAuthorTracks();
    await fetchGenres();
  }

  window.addEventListener("favorites-updated", fetchAll);
  console.log(purchases.value);
});
</script>

<style scoped>
/* ========== GLOBAL & UTILITIES ========== */
.profile {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 2rem 4rem;
  font-family: "Inter", system-ui, -apple-system, sans-serif;
}

.glass-card {
  background: rgba(20, 20, 30, 0.6);
  backdrop-filter: blur(12px);
  border-radius: 28px;
  border: 1px solid rgba(168, 85, 247, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.glass-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
  border-color: rgba(168, 85, 247, 0.4);
}

.btn-primary {
  background: linear-gradient(135deg, #a855f7, #3b82f6);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 40px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(168, 85, 247, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.7rem 1.4rem;
  border-radius: 40px;
  color: #e0e0e0;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
}

.btn-outline {
  background: transparent;
  border: 1px solid #a855f7;
  color: #a855f7;
  padding: 0.6rem 1.2rem;
  border-radius: 40px;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-outline:hover {
  background: #a855f7;
  color: white;
}

/* ========== HERO SECTION ========== */
.hero-section {
  position: relative;
  margin-bottom: 2rem;
  border-radius: 32px;
  overflow: hidden;
}

.hero-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(
      circle at 20% 30%,
      rgba(168, 85, 247, 0.2),
      transparent 70%
    ),
    linear-gradient(135deg, #0a0a0f, #1a1a2a);
  z-index: 0;
}

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 3rem 2rem;
  backdrop-filter: blur(2px);
}

.avatar-large {
  position: relative;
  width: 120px;
  height: 120px;
  flex-shrink: 0;
}

.avatar-large img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #a855f7;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

.edit-avatar-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #a855f7;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.edit-avatar-btn:hover {
  transform: scale(1.1);
  background: #8b46d9;
}

.hero-info h1 {
  font-size: 2.2rem;
  margin: 0 0 0.5rem 0;
  background: linear-gradient(135deg, #fff, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.role-badge {
  background: rgba(168, 85, 247, 0.2);
  display: inline-block;
  padding: 0.2rem 1rem;
  border-radius: 40px;
  font-size: 0.8rem;
  color: #c084fc;
  margin-bottom: 1rem;
}

.stats {
  display: flex;
  gap: 2rem;
}

.stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
}

.stat-label {
  font-size: 0.8rem;
  color: #a0a0b0;
}

/* ========== TABS ========== */
.tabs-container {
  margin-bottom: 2rem;
  overflow-x: auto;
  scrollbar-width: thin;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 0;
}

.tabs button {
  background: transparent;
  border: none;
  padding: 0.75rem 1.5rem;
  color: #a0a0b0;
  font-weight: 500;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border-radius: 40px;
  white-space: nowrap;
}

.tabs button .tab-icon {
  font-size: 1.1rem;
}

.tabs button.active {
  background: linear-gradient(
    135deg,
    rgba(168, 85, 247, 0.2),
    rgba(59, 130, 246, 0.2)
  );
  color: white;
  box-shadow: 0 2px 8px rgba(168, 85, 247, 0.2);
}

.tabs button:hover:not(.active) {
  color: #d0d0e0;
  background: rgba(255, 255, 255, 0.05);
}

/* ========== TAB CONTENT ========== */
.content-container {
  min-height: 500px;
}

.tab-pane {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

/* Info Pane */
.info-pane .info-card {
  padding: 2rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.info-item i {
  font-size: 1.8rem;
  color: #a855f7;
  width: 40px;
}

.info-item label {
  display: block;
  font-size: 0.8rem;
  color: #a0a0b0;
  margin-bottom: 0.2rem;
}

.info-item p {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 500;
}

.edit-profile-btn {
  width: 100%;
  justify-content: center;
}

/* Purchases Grid */
.purchases-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.purchase-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.2rem;
  flex-wrap: wrap;
}

.purchase-image {
  width: 80px;
  height: 80px;
  border-radius: 16px;
  overflow: hidden;
  flex-shrink: 0;
}

.purchase-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.purchase-details {
  flex: 1;
  min-width: 180px;
}

.purchase-details h3 {
  margin: 0 0 0.2rem;
  font-size: 1.1rem;
}

.purchase-details .artist {
  margin: 0 0 0.2rem;
  color: #a0a0b0;
  font-size: 0.85rem;
}

.purchase-details .date {
  margin: 0 0 0.8rem;
  font-size: 0.7rem;
  color: #6b6b80;
}

.purchase-actions {
  display: flex;
  gap: 0.8rem;
}

.btn-icon {
  background: rgba(168, 85, 247, 0.1);
  border: none;
  padding: 0.4rem 1rem;
  border-radius: 40px;
  color: #a855f7;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-icon:hover {
  background: #a855f7;
  color: white;
}

.purchase-price {
  font-size: 1.4rem;
  font-weight: 700;
  background: linear-gradient(135deg, #a855f7, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  flex-shrink: 0;
}

/* Track Grid */
.track-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 2rem;
}

.track-card-wrapper {
  position: relative;
  transition: transform 0.2s;
}

.track-card-wrapper:hover {
  transform: translateY(-6px);
}

.track-actions {
  position: absolute;
  top: 0.8rem;
  right: 0.8rem;
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.track-card-wrapper:hover .track-actions {
  opacity: 1;
}

.btn-action {
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-action.edit:hover {
  background: #a855f7;
  transform: scale(1.05);
}

.btn-action.delete:hover {
  background: #ff4444;
  transform: scale(1.05);
}

/* Authors Grid */
.authors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1.5rem;
}

.author-card {
  padding: 1.5rem;
  text-align: center;
  transition: all 0.2s;
}

.author-avatar-wrapper {
  width: 100px;
  height: 100px;
  margin: 0 auto 1rem;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid #a855f7;
}

.author-avatar-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.author-card h3 {
  margin: 0 0 1rem;
  font-size: 1.1rem;
}

.btn-unfollow {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.4rem 1rem;
  border-radius: 40px;
  color: #ff8888;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-unfollow:hover {
  background: rgba(255, 68, 68, 0.2);
  border-color: #ff4444;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 28px;
}

.empty-icon {
  font-size: 3rem;
  color: #a855f7;
  opacity: 0.5;
  margin-bottom: 1rem;
}

.empty-state p {
  margin-bottom: 1.5rem;
  color: #a0a0b0;
}

/* Upload Form */
.upload-form-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
}

.upload-form-container h2 {
  margin-bottom: 1.5rem;
  font-size: 1.6rem;
  text-align: center;
  background: linear-gradient(135deg, #fff, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.upload-form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 500;
  color: #c0c0d0;
}

.form-group input,
.form-group select {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(168, 85, 247, 0.3);
  border-radius: 40px;
  padding: 0.7rem 1rem;
  color: white;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #a855f7;
  box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.2);
}

.file-group .file-input {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.file-input input {
  display: none;
}

.file-label {
  background: rgba(168, 85, 247, 0.15);
  border: 1px solid rgba(168, 85, 247, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 40px;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.file-label:hover {
  background: rgba(168, 85, 247, 0.3);
}

.file-name {
  font-size: 0.8rem;
  color: #a0a0b0;
}

.cover-preview {
  margin-top: 0.5rem;
  width: 100px;
  height: 100px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #a855f7;
}

.cover-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.submit-btn {
  margin-top: 0.5rem;
  justify-content: center;
}

/* Section Header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.section-header h2 {
  font-size: 1.5rem;
  margin: 0;
  background: linear-gradient(135deg, #fff, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.loading-spinner {
  text-align: center;
  padding: 3rem;
  color: #a855f7;
  font-size: 2rem;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  position: relative;
  max-width: 500px;
  width: 90%;
  padding: 2rem;
  animation: modalSlideIn 0.3s ease;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1.5rem;
  background: none;
  border: none;
  font-size: 1.8rem;
  color: #a0a0b0;
  cursor: pointer;
  transition: color 0.2s;
}

.modal-close:hover {
  color: white;
}

.modal h2 {
  margin-bottom: 1.5rem;
  text-align: center;
  font-size: 1.8rem;
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
  transition: all 0.2s;
  font-size: 0.85rem;
}

.upload-label:hover {
  background: #a855f7;
  color: white;
}

.edit-form .form-group {
  margin-bottom: 1.2rem;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

/* Responsive */
@media (max-width: 768px) {
  .profile {
    padding: 0 1rem 3rem;
  }

  .hero-content {
    flex-direction: column;
    text-align: center;
    padding: 2rem 1rem;
  }

  .hero-info h1 {
    font-size: 1.8rem;
  }

  .stats {
    justify-content: center;
  }

  .tabs {
    justify-content: flex-start;
  }

  .tabs button {
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .purchase-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .purchase-price {
    align-self: flex-end;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .track-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 1rem;
  }
}
</style>
