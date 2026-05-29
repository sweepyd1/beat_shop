<template>
  <div class="admin-container">
    <!-- Анимированный градиентный фон -->
    <div class="hero-glow"></div>

    <!-- Заголовок -->
    <div class="header" data-aos="fade-up">
      <div class="badge">Администрирование</div>
      <h1 class="title">
        <span class="gradient-text">Управление пользователями</span>
      </h1>
      <p class="subtitle">Просмотр, создание, редактирование и блокировка пользователей</p>
    </div>

    <!-- Панель инструментов -->
    <div class="toolbar" data-aos="fade-up" data-aos-delay="100">
      <div class="toolbar-left">
        <div class="search-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Поиск по имени, логину или email..."
            class="search-input"
          />
        </div>
        <select v-model="filterRole" class="filter-select">
          <option value="">Все роли</option>
          <option value="user">Пользователь</option>
          <option value="author">Автор</option>
          <option value="admin">Администратор</option>
        </select>
      </div>
      <button @click="openCreateModal" class="btn-primary">
        <i class="fas fa-plus"></i>
        <span>Добавить пользователя</span>
      </button>
    </div>

    <!-- Таблица пользователей -->
    <div class="card" data-aos="fade-up" data-aos-delay="200">
      <!-- Скелетон загрузки -->
      <div v-if="loading" class="skeleton-container">
        <div v-for="i in 5" :key="i" class="skeleton-row">
          <div class="skeleton-avatar"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-badge"></div>
          <div class="skeleton-badge"></div>
          <div class="skeleton-actions"></div>
        </div>
      </div>

      <!-- Таблица -->
      <div v-else class="table-wrapper">
        <table class="users-table">
          <thead>
            <tr>
              <th @click="sortBy('avatar')" class="sortable">
                <span>Аватар</span>
                <i class="fas fa-sort" v-if="sortKey !== 'avatar'"></i>
                <i :class="sortOrder === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down'" v-else></i>
              </th>
              <th @click="sortBy('full_name')" class="sortable">
                <span>Имя</span>
                <i class="fas fa-sort" v-if="sortKey !== 'full_name'"></i>
                <i :class="sortOrder === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down'" v-else></i>
              </th>
              <th @click="sortBy('login')" class="sortable">
                <span>Логин</span>
                <i class="fas fa-sort" v-if="sortKey !== 'login'"></i>
                <i :class="sortOrder === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down'" v-else></i>
              </th>
              <th @click="sortBy('email')" class="sortable">
                <span>Email</span>
                <i class="fas fa-sort" v-if="sortKey !== 'email'"></i>
                <i :class="sortOrder === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down'" v-else></i>
              </th>
              <th @click="sortBy('role')" class="sortable">
                <span>Роль</span>
                <i class="fas fa-sort" v-if="sortKey !== 'role'"></i>
                <i :class="sortOrder === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down'" v-else></i>
              </th>
              <th @click="sortBy('is_active')" class="sortable">
                <span>Статус</span>
                <i class="fas fa-sort" v-if="sortKey !== 'is_active'"></i>
                <i :class="sortOrder === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down'" v-else></i>
              </th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in paginatedUsers" :key="user.id" class="user-row">
              <td class="avatar-cell">
                <div class="avatar-wrapper">
                  <img
                    :src="getAvatarUrl(user.avatar_url)"
                    class="user-avatar"
                    @error="e => e.target.src = '/default-avatar.png'"
                  />
                  <div class="avatar-status" :class="{ online: user.is_active }"></div>
                </div>
              </td>
              <td class="fullname">{{ user.full_name }}</td>
              <td class="login">{{ user.login }}</td>
              <td class="email">{{ user.email }}</td>
              <td>
                <span :class="['role-badge', user.role]">
                  <i :class="roleIcon(user.role)"></i>
                  {{ roleName(user.role) }}
                </span>
              </td>
              <td>
                <span :class="['status-badge', user.is_active ? 'active' : 'blocked']">
                  <i :class="user.is_active ? 'fas fa-circle' : 'fas fa-ban'"></i>
                  {{ user.is_active ? 'Активен' : 'Заблокирован' }}
                </span>
              </td>
              <td class="actions-cell">
                <button @click="openEditModal(user)" class="action-btn edit" title="Редактировать">
                  <i class="fas fa-pen"></i>
                </button>
                <button @click="toggleActive(user)" class="action-btn" :class="user.is_active ? 'block' : 'unblock'" :title="user.is_active ? 'Заблокировать' : 'Разблокировать'">
                  <i :class="user.is_active ? 'fas fa-lock' : 'fas fa-lock-open'"></i>
                </button>
                <button @click="deleteUser(user.id)" class="action-btn delete" title="Удалить">
                  <i class="fas fa-trash-alt"></i>
                </button>
                <button @click="openStats(user)" class="action-btn stats" title="Подробная статистика">
                  <i class="fas fa-chart-line"></i>
                </button>
              </td>
            </tr>
            <tr v-if="filteredUsers.length === 0">
              <td colspan="7" class="empty-state">
                <i class="fas fa-users-slash"></i>
                <p>Пользователи не найдены</p>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Пагинация -->
        <div class="pagination" v-if="totalPages > 1">
          <button @click="currentPage--" :disabled="currentPage === 1" class="page-btn">
            <i class="fas fa-chevron-left"></i>
          </button>
          <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
          <button @click="currentPage++" :disabled="currentPage === totalPages" class="page-btn">
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Модалка создания/редактирования -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
          <div class="modal-container" @click.stop>
            <div class="modal-header">
              <h2>{{ editingUserId ? 'Редактирование пользователя' : 'Новый пользователь' }}</h2>
              <button @click="closeModal" class="modal-close">
                <i class="fas fa-times"></i>
              </button>
            </div>
            <form @submit.prevent="submitUser" class="modal-form">
              <div class="form-grid">
                <div class="form-group">
                  <label>Полное имя <span class="required">*</span></label>
                  <input v-model="form.full_name" type="text" required class="form-input" />
                </div>
                <div class="form-group">
                  <label>Логин <span class="required">*</span></label>
                  <input v-model="form.login" type="text" required class="form-input" :disabled="!!editingUserId" />
                </div>
                <div class="form-group">
                  <label>Email <span class="required">*</span></label>
                  <input v-model="form.email" type="email" required class="form-input" />
                </div>
                <div class="form-group">
                  <label v-if="!editingUserId">Пароль <span class="required">*</span></label>
                  <label v-else>Новый пароль <span class="optional">(оставьте пустым, чтобы не менять)</span></label>
                  <input v-model="form.password" :type="editingUserId ? 'password' : 'password'" class="form-input" :required="!editingUserId" />
                </div>
                <div class="form-group">
                  <label>Роль</label>
                  <select v-model="form.role" class="form-select">
                    <option value="user">Пользователь</option>
                    <option value="author">Автор</option>
                    <option value="admin">Администратор</option>
                  </select>
                </div>
                <div class="form-group full-width">
                  <label>Аватар</label>
                  <div class="avatar-upload" @click="$refs.avatarInput.click()">
                    <input type="file" ref="avatarInput" accept="image/*" @change="onAvatarChange" hidden />
                    <div v-if="avatarPreview" class="avatar-preview">
                      <img :src="avatarPreview" />
                      <span class="change-avatar">Изменить</span>
                    </div>
                    <div v-else class="upload-placeholder">
                      <i class="fas fa-cloud-upload-alt"></i>
                      <span>Загрузить аватар</span>
                    </div>
                  </div>
                </div>
                <div class="form-group" v-if="editingUserId">
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="form.is_active" class="checkbox" />
                    <span>Активен</span>
                  </label>
                </div>
              </div>
              <div class="modal-actions">
                <button type="button" @click="closeModal" class="btn-secondary">Отмена</button>
                <button type="submit" :disabled="saving" class="btn-primary">
                  <i class="fas fa-save"></i>
                  {{ saving ? 'Сохранение...' : (editingUserId ? 'Обновить' : 'Создать') }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Модалка статистики -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="showStatsModal" class="modal-overlay" @click.self="showStatsModal = false">
          <div class="modal-container stats-modal">
            <div class="modal-header">
              <h2>Статистика пользователя</h2>
              <button @click="showStatsModal = false" class="modal-close">
                <i class="fas fa-times"></i>
              </button>
            </div>
            <div v-if="statsLoading" class="stats-loading">
              <i class="fas fa-spinner fa-spin"></i>
              <span>Загрузка данных...</span>
            </div>
            <div v-else-if="statsUser" class="stats-content">
              <div class="stats-grid">
                <div class="stat-card">
                  <div class="stat-icon"><i class="fas fa-shopping-cart"></i></div>
                  <div class="stat-info">
                    <span class="stat-label">Покупок</span>
                    <span class="stat-value">{{ statsUser.purchases_count }}</span>
                  </div>
                </div>
                <div class="stat-card">
                  <div class="stat-icon"><i class="fas fa-heart"></i></div>
                  <div class="stat-info">
                    <span class="stat-label">Избранное</span>
                    <span class="stat-value">{{ statsUser.favorites_count }}</span>
                  </div>
                </div>
                <div class="stat-card">
                  <div class="stat-icon"><i class="fas fa-bell"></i></div>
                  <div class="stat-info">
                    <span class="stat-label">Подписок</span>
                    <span class="stat-value">{{ statsUser.subscriptions_count }}</span>
                  </div>
                </div>
                <div class="stat-card">
                  <div class="stat-icon"><i class="fas fa-ruble-sign"></i></div>
                  <div class="stat-info">
                    <span class="stat-label">Потрачено</span>
                    <span class="stat-value">{{ statsUser.total_spent.toFixed(2) }} ₽</span>
                  </div>
                </div>
              </div>

              <div class="stats-section" v-if="statsUser.top_genres?.length">
                <h3>Топ жанров</h3>
                <div class="genres-list">
                  <div v-for="g in statsUser.top_genres" :key="g.genre_name" class="genre-item">
                    <span class="genre-name">{{ g.genre_name }}</span>
                    <div class="genre-bar">
                      <div class="genre-bar-fill" :style="{ width: `${(g.count / statsUser.top_genres[0].count) * 100}%` }"></div>
                    </div>
                    <span class="genre-count">{{ g.count }}</span>
                  </div>
                </div>
              </div>

              <div class="stats-section" v-if="statsUser.recent_purchases?.length">
                <h3>Последние покупки</h3>
                <ul class="recent-list">
                  <li v-for="p in statsUser.recent_purchases.slice(0,5)" :key="p.id">
                    <i class="fas fa-music"></i>
                    <span>{{ p.track?.title || 'Трек' }}</span>
                    <strong>{{ p.amount }} ₽</strong>
                  </li>
                </ul>
              </div>

              <div class="stats-section" v-if="statsUser.recent_favorites?.length">
                <h3>Недавно добавлено в избранное</h3>
                <ul class="recent-list">
                  <li v-for="f in statsUser.recent_favorites.slice(0,5)" :key="f.id">
                    <i class="fas fa-heart"></i>
                    <span>{{ f.track?.title || 'Трек' }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '@/api';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

// Проверка прав
if (authStore.user?.role !== 'admin') {
  router.replace('/');
}

// Данные
const users = ref([]);
const loading = ref(false);
const searchQuery = ref('');
const filterRole = ref('');
const showModal = ref(false);
const editingUserId = ref(null);
const saving = ref(false);
const statsUser = ref(null);
const showStatsModal = ref(false);
const statsLoading = ref(false);

// Пагинация и сортировка
const currentPage = ref(1);
const pageSize = ref(10);
const sortKey = ref('full_name');
const sortOrder = ref('asc');

// Форма
const form = ref({
  full_name: '',
  login: '',
  email: '',
  password: '',
  role: 'user',
  is_active: true
});
const avatarFile = ref(null);
const avatarPreview = ref(null);

// Получение URL аватара
const getAvatarUrl = (url) => {
  if (!url) return '/default-avatar.png';
  if (url.startsWith('http')) return url;
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  return `${baseUrl}${url}`;
};

// Роль: иконка и название
const roleIcon = (role) => {
  const icons = { user: 'fas fa-user', author: 'fas fa-microphone-alt', admin: 'fas fa-crown' };
  return icons[role] || 'fas fa-user';
};
const roleName = (role) => {
  const names = { user: 'Пользователь', author: 'Автор', admin: 'Администратор' };
  return names[role] || role;
};

// Фильтрация и сортировка
const filteredUsers = computed(() => {
  let result = users.value;
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(u =>
      u.full_name.toLowerCase().includes(q) ||
      u.email.toLowerCase().includes(q) ||
      u.login.toLowerCase().includes(q)
    );
  }
  if (filterRole.value) {
    result = result.filter(u => u.role === filterRole.value);
  }
  // Сортировка
  return [...result].sort((a, b) => {
    let aVal = a[sortKey.value];
    let bVal = b[sortKey.value];
    if (sortKey.value === 'is_active') {
      aVal = aVal ? 1 : 0;
      bVal = bVal ? 1 : 0;
    }
    if (typeof aVal === 'string') aVal = aVal.toLowerCase();
    if (typeof bVal === 'string') bVal = bVal.toLowerCase();
    if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1;
    return 0;
  });
});

const totalPages = computed(() => Math.ceil(filteredUsers.value.length / pageSize.value));
const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return filteredUsers.value.slice(start, start + pageSize.value);
});

const sortBy = (key) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortOrder.value = 'asc';
  }
  currentPage.value = 1; // сброс страницы при сортировке
};

// Загрузка пользователей
const fetchUsers = async () => {
  loading.value = true;
  try {
    const { data } = await api.get('/admin/users');
    users.value = data;
  } catch (err) {
    console.error(err);
    showError('Ошибка загрузки пользователей');
  } finally {
    loading.value = false;
  }
};

// Модалка создания
const openCreateModal = () => {
  editingUserId.value = null;
  form.value = { full_name: '', login: '', email: '', password: '', role: 'user', is_active: true };
  avatarFile.value = null;
  avatarPreview.value = null;
  showModal.value = true;
};

// Редактирование
const openEditModal = (user) => {
  editingUserId.value = user.id;
  form.value = {
    full_name: user.full_name,
    login: user.login,
    email: user.email,
    password: '',
    role: user.role,
    is_active: user.is_active
  };
  avatarFile.value = null;
  avatarPreview.value = user.avatar_url ? getAvatarUrl(user.avatar_url) : null;
  showModal.value = true;
};

// Загрузка аватара
const onAvatarChange = (e) => {
  const file = e.target.files[0];
  if (file) {
    avatarFile.value = file;
    avatarPreview.value = URL.createObjectURL(file);
  }
};

// Отправка формы
const submitUser = async () => {
  saving.value = true;
  const fd = new FormData();
  fd.append('full_name', form.value.full_name);
  fd.append('email', form.value.email);
  fd.append('role', form.value.role);
  if (form.value.password) fd.append('password', form.value.password);
  if (avatarFile.value) fd.append('avatar', avatarFile.value);
  if (!editingUserId.value) {
    fd.append('login', form.value.login);
  } else {
    fd.append('is_active', form.value.is_active);
  }

  try {
    if (editingUserId.value) {
      await api.put(`/admin/users/${editingUserId.value}`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    } else {
      await api.post('/admin/users', fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    }
    showModal.value = false;
    fetchUsers();
  } catch (err) {
    console.error(err);
    showError(err.response?.data?.detail || 'Ошибка сохранения');
  } finally {
    saving.value = false;
  }
};

// Блокировка/разблокировка
const toggleActive = async (user) => {
  const fd = new FormData();
  fd.append('is_active', !user.is_active);
  try {
    await api.put(`/admin/users/${user.id}`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    fetchUsers();
  } catch (err) {
    console.error(err);
  }
};

// Удаление
const deleteUser = async (id) => {
  if (!confirm('Удалить пользователя? Это действие необратимо.')) return;
  try {
    await api.delete(`/admin/users/${id}`);
    fetchUsers();
  } catch (err) {
    console.error(err);
    showError('Ошибка удаления');
  }
};

// Статистика
const openStats = async (user) => {
  statsLoading.value = true;
  showStatsModal.value = true;
  try {
    const { data } = await api.get(`/admin/users/${user.id}/profile`);
    statsUser.value = data;
  } catch (err) {
    console.error(err);
    showError('Не удалось загрузить статистику');
  } finally {
    statsLoading.value = false;
  }
};

// Закрытие модалок
const closeModal = () => {
  showModal.value = false;
  if (avatarPreview.value && avatarFile.value) {
    URL.revokeObjectURL(avatarPreview.value);
  }
};

onMounted(fetchUsers);
</script>

<style scoped>
/* Глобальные переменные и анимации */
.admin-container {
  max-width: 1400px;
  margin: 2rem auto;
  padding: 0 1.5rem;
  position: relative;
  z-index: 1;
}

.hero-glow {
  position: fixed;
  top: -20%;
  left: -20%;
  width: 140%;
  height: 140%;
  background: radial-gradient(circle at 30% 10%, rgba(168,85,247,0.15), transparent 70%);
  pointer-events: none;
  z-index: 0;
}

/* Заголовок */
.header {
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
  z-index: 2;
}

.badge {
  display: inline-block;
  background: rgba(168,85,247,0.2);
  backdrop-filter: blur(4px);
  padding: 0.25rem 1rem;
  border-radius: 2rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #c084fc;
  margin-bottom: 1rem;
  border: 1px solid rgba(168,85,247,0.3);
}

.title {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
}

.gradient-text {
  background: linear-gradient(135deg, #a855f7, #ec4899, #3b82f6);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
}

.subtitle {
  color: #9ca3af;
  font-size: 1.1rem;
}

/* Панель инструментов */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 2rem;
  background: rgba(15, 15, 25, 0.6);
  backdrop-filter: blur(12px);
  padding: 0.75rem 1.5rem;
  border-radius: 2rem;
  border: 1px solid rgba(168,85,247,0.2);
}

.toolbar-left {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-wrapper {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
}

.search-input {
  background: rgba(0,0,0,0.5);
  border: 1px solid #2d2d3d;
  border-radius: 2rem;
  padding: 0.6rem 1rem 0.6rem 2.5rem;
  color: white;
  width: 260px;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #a855f7;
  box-shadow: 0 0 0 2px rgba(168,85,247,0.2);
}

.filter-select {
  background: rgba(0,0,0,0.5);
  border: 1px solid #2d2d3d;
  border-radius: 2rem;
  padding: 0.6rem 1rem;
  color: white;
  cursor: pointer;
}

.btn-primary {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 2rem;
  color: white;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(168,85,247,0.3);
}

.btn-secondary {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  padding: 0.6rem 1.2rem;
  border-radius: 2rem;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: rgba(255,255,255,0.2);
}

/* Карточка таблицы */
.card {
  background: rgba(20, 20, 30, 0.7);
  backdrop-filter: blur(12px);
  border-radius: 1.5rem;
  border: 1px solid rgba(168,85,247,0.2);
  overflow: hidden;
  padding: 0;
  transition: all 0.3s;
}

.table-wrapper {
  overflow-x: auto;
  padding: 0;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  color: #e5e7eb;
}

.users-table th,
.users-table td {
  padding: 1rem 1.2rem;
  text-align: left;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.users-table th {
  background: rgba(0,0,0,0.3);
  font-weight: 600;
  color: #c084fc;
  cursor: pointer;
  user-select: none;
}

.sortable {
  transition: background 0.2s;
}

.sortable:hover {
  background: rgba(168,85,247,0.1);
}

.sortable i {
  margin-left: 0.5rem;
  font-size: 0.8rem;
  opacity: 0.6;
}

.user-row {
  transition: background 0.2s;
}

.user-row:hover {
  background: rgba(168,85,247,0.05);
}

.avatar-cell {
  width: 60px;
}

.avatar-wrapper {
  position: relative;
  width: 44px;
  height: 44px;
}

.user-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(168,85,247,0.5);
}

.avatar-status {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #6b7280;
  border: 2px solid #1e1e2e;
}

.avatar-status.online {
  background: #10b981;
  box-shadow: 0 0 6px #10b981;
}

.role-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.25rem 0.8rem;
  border-radius: 2rem;
  font-size: 0.8rem;
  font-weight: 600;
  background: rgba(0,0,0,0.4);
}

.role-badge.user { background: rgba(59,130,246,0.2); color: #60a5fa; }
.role-badge.author { background: rgba(16,185,129,0.2); color: #34d399; }
.role-badge.admin { background: rgba(168,85,247,0.2); color: #c084fc; }

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.25rem 0.8rem;
  border-radius: 2rem;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.active {
  background: rgba(16,185,129,0.15);
  color: #34d399;
}
.status-badge.blocked {
  background: rgba(239,68,68,0.15);
  color: #f87171;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: rgba(255,255,255,0.05);
  border: none;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  color: #9ca3af;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  transform: scale(1.05);
}
.action-btn.edit:hover { background: #3b82f6; color: white; }
.action-btn.block:hover { background: #ef4444; color: white; }
.action-btn.unblock:hover { background: #10b981; color: white; }
.action-btn.delete:hover { background: #dc2626; color: white; }
.action-btn.stats:hover { background: #8b5cf6; color: white; }

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

/* Пагинация */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-top: 1px solid rgba(255,255,255,0.05);
}

.page-btn {
  background: rgba(0,0,0,0.4);
  border: 1px solid rgba(168,85,247,0.3);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #a855f7;
  border-color: #a855f7;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.9rem;
  color: #c084fc;
}

/* Скелетон */
.skeleton-container {
  padding: 1rem;
}
.skeleton-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.skeleton-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255,255,255,0.05);
  animation: pulse 1.5s infinite;
}
.skeleton-line {
  height: 16px;
  background: rgba(255,255,255,0.05);
  border-radius: 4px;
  flex: 1;
  animation: pulse 1.5s infinite;
}
.skeleton-badge {
  width: 80px;
  height: 24px;
  background: rgba(255,255,255,0.05);
  border-radius: 2rem;
  animation: pulse 1.5s infinite;
}
.skeleton-actions {
  width: 120px;
  height: 34px;
  background: rgba(255,255,255,0.05);
  border-radius: 2rem;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}

/* Модалки */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-container {
  background: #1a1a2a;
  border-radius: 1.5rem;
  border: 1px solid rgba(168,85,247,0.3);
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.modal-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin: 0;
}
.modal-close {
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 1.5rem;
  cursor: pointer;
  transition: color 0.2s;
}
.modal-close:hover {
  color: white;
}
.modal-form {
  padding: 1.5rem;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}
.full-width {
  grid-column: span 2;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.form-group label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #d1d5db;
}
.required {
  color: #ef4444;
}
.optional {
  font-size: 0.7rem;
  color: #6b7280;
  font-weight: normal;
}
.form-input,
.form-select {
  background: rgba(0,0,0,0.5);
  border: 1px solid #2d2d3d;
  border-radius: 0.75rem;
  padding: 0.7rem 1rem;
  color: white;
  transition: all 0.2s;
}
.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #a855f7;
  box-shadow: 0 0 0 2px rgba(168,85,247,0.2);
}
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}
.checkbox {
  width: 18px;
  height: 18px;
  accent-color: #a855f7;
}
.avatar-upload {
  background: rgba(0,0,0,0.3);
  border: 1px dashed rgba(168,85,247,0.5);
  border-radius: 1rem;
  padding: 1rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}
.avatar-upload:hover {
  background: rgba(168,85,247,0.1);
}
.avatar-preview {
  position: relative;
}
.avatar-preview img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  margin: 0 auto;
}
.change-avatar {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: #a855f7;
}
.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: #9ca3af;
}
.upload-placeholder i {
  font-size: 2rem;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

/* Статистика модалка */
.stats-modal {
  max-width: 800px;
}
.stats-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 3rem;
  color: #a855f7;
}
.stats-content {
  padding: 1.5rem;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}
.stat-card {
  background: rgba(0,0,0,0.3);
  border-radius: 1rem;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s;
}
.stat-card:hover {
  transform: translateY(-2px);
  background: rgba(168,85,247,0.1);
}
.stat-icon {
  font-size: 2rem;
  color: #a855f7;
}
.stat-info {
  display: flex;
  flex-direction: column;
}
.stat-label {
  font-size: 0.8rem;
  color: #9ca3af;
}
.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
}
.stats-section {
  margin-top: 1.5rem;
}
.stats-section h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #c084fc;
  margin-bottom: 1rem;
  border-left: 3px solid #a855f7;
  padding-left: 0.75rem;
}
.genres-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.genre-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.genre-name {
  width: 100px;
  font-weight: 500;
}
.genre-bar {
  flex: 1;
  height: 8px;
  background: rgba(255,255,255,0.1);
  border-radius: 4px;
  overflow: hidden;
}
.genre-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #a855f7, #ec4899);
  border-radius: 4px;
}
.genre-count {
  font-size: 0.8rem;
  color: #a855f7;
  min-width: 40px;
  text-align: right;
}
.recent-list {
  list-style: none;
  padding: 0;
}
.recent-list li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.recent-list li i {
  width: 24px;
  color: #a855f7;
}
.recent-list li strong {
  margin-left: auto;
  color: #10b981;
}

/* Адаптив */
@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  .toolbar-left {
    flex-direction: column;
  }
  .search-input {
    width: 100%;
  }
  .form-grid {
    grid-template-columns: 1fr;
  }
  .full-width {
    grid-column: span 1;
  }
  .users-table th,
  .users-table td {
    padding: 0.75rem;
  }
  .actions-cell {
    flex-wrap: wrap;
  }
}
</style>