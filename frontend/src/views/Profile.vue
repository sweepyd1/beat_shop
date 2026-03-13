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
              <img :src="user.avatar" alt="" />
            </div>
            <div class="details">
              <p><strong>Имя:</strong> {{ user.name }}</p>
              <p><strong>Email:</strong> {{ user.email }}</p>
              <p><strong>Дата регистрации:</strong> {{ formatDate(user.registered) }}</p>
              <button class="btn-secondary" @click="openEditModal">Редактировать</button>
            </div>
          </div>
        </div>

        <!-- Мои покупки -->
        <div v-if="activeTab === 'purchases'" class="tab-pane">
          <div v-if="purchases.length === 0" class="empty">
            <p>У вас ещё нет покупок.</p>
            <router-link to="/search" class="btn-primary">Найти биты</router-link>
          </div>
          <div v-else class="purchases-list">
            <div v-for="item in purchases" :key="item.id" class="purchase-item">
              <img :src="item.cover" alt="" />
              <div class="info">
                <h4>{{ item.title }}</h4>
                <p>{{ item.artist }}</p>
              </div>
              <span class="date">{{ formatDate(item.purchase_date) }}</span>
              <span class="price">{{ item.price }} ₽</span>
              <button class="download-btn" @click="downloadTrack(item.id)"><i class="fas fa-download"></i></button>
            </div>
          </div>
        </div>

        <!-- Избранное -->
        <div v-if="activeTab === 'favorites'" class="tab-pane">
          <div class="track-grid">
            <TrackCard
              v-for="track in favorites"
              :key="track.id"
              :track="track"
            />
          </div>
        </div>

        <!-- Подписки на артистов -->
        <div v-if="activeTab === 'subscriptions'" class="tab-pane">
          <div class="artists-list">
            <div v-for="artist in subscriptions" :key="artist.id" class="artist-sub">
              <img :src="artist.avatar" alt="" />
              <div class="info">
                <h4>{{ artist.name }}</h4>
                <p>{{ artist.followers_count }} подписчиков</p>
              </div>
              <button class="unsubscribe" @click="unsubscribe(artist.id)">Отписаться</button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
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
  downloadTrack,
  unsubscribe,
} = useProfile();

// Форматирование даты (пример)
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU');
};

// Загружаем данные при монтировании
onMounted(() => {
  fetchAll();
});

// Редактирование профиля (можно реализовать модальное окно)
const openEditModal = () => {
  // ...
};
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

.purchases-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.purchase-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(255,255,255,0.03);
  padding: 1rem;
  border-radius: 12px;
}

.purchase-item img {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  object-fit: cover;
}

.purchase-item .info {
  flex: 1;
}

.purchase-item .info h4 {
  font-size: 1rem;
  margin-bottom: 0.2rem;
}

.purchase-item .info p {
  font-size: 0.85rem;
  color: #a0a0b0;
}

.purchase-item .date,
.purchase-item .price {
  color: #a0a0b0;
  min-width: 80px;
}

.purchase-item .price {
  color: #a855f7;
  font-weight: 600;
}

.download-btn {
  background: none;
  border: none;
  color: #a0a0b0;
  font-size: 1.2rem;
  cursor: pointer;
  transition: color 0.2s;
}

.download-btn:hover {
  color: #a855f7;
}

.empty {
  text-align: center;
  padding: 2rem;
}

.artists-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.artist-sub {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(255,255,255,0.03);
  padding: 1rem;
  border-radius: 12px;
}

.artist-sub img {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
}

.artist-sub .info {
  flex: 1;
}

.artist-sub .info h4 {
  font-size: 1rem;
}

.artist-sub .info p {
  font-size: 0.85rem;
  color: #a0a0b0;
}

.unsubscribe {
  background: rgba(255,77,77,0.1);
  border: 1px solid #ff4d4d;
  color: #ff4d4d;
  padding: 0.4rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.unsubscribe:hover {
  background: #ff4d4d;
  color: white;
}

.track-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 2rem;
}
</style>