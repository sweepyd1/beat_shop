<template>
  <div class="artist-dashboard">
    <!-- Хедер с информацией об авторе -->
    <div class="artist-header">
      <!-- <div class="avatar-wrapper">
        <img :src="authorAvatar" alt="avatar" class="avatar" @error="handleImageError" />
        <div class="avatar-ring"></div>
      </div> -->
      <div class="artist-info">
        <h1>{{ author.full_name }}</h1>
        <div class="bio-wrapper">
          <p v-if="!editingBio" class="bio">
            {{ author.bio || "Автор не заполнил биографию" }}
            <i class="fas fa-pencil-alt edit-icon" @click="startEditBio"></i>
          </p>
          <div v-else class="bio-edit">
            <textarea
              v-model="editBioText"
              rows="3"
              placeholder="Расскажите о себе..."
            ></textarea>
            <div class="edit-actions">
              <button @click="saveBio" class="save-btn">Сохранить</button>
              <button @click="cancelEditBio" class="cancel-btn">Отмена</button>
            </div>
          </div>
        </div>
        <div class="stats">
          <!-- <div class="stat-item">
            <span class="stat-value">{{ formatNumber(author.followers_count || 0) }}</span>
            <span class="stat-label">подписчиков</span>
          </div> -->
          <div class="stat-item">
            <span class="stat-value"
              >{{ formatNumber(author.total_earnings || 0) }} ₽</span
            >
            <span class="stat-label">выручка</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ author.tracks_count || 0 }}</span>
            <span class="stat-label">битов</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Общая статистика (карточки) -->
    <div class="sales-stats">
      <h2><i class="fas fa-chart-line"></i> Общая статистика</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <i class="fas fa-music"></i>
          <div>
            <span class="stat-card-value">{{
              fullStats.total_tracks ?? 0
            }}</span>
            <span class="stat-card-label">треков</span>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-headphones"></i>
          <div>
            <span class="stat-card-value">{{
              formatNumber(fullStats.total_plays ?? 0)
            }}</span>
            <span class="stat-card-label">прослушиваний</span>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-heart"></i>
          <div>
            <span class="stat-card-value">{{
              formatNumber(fullStats.total_favorites ?? 0)
            }}</span>
            <span class="stat-card-label">лайков</span>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-users"></i>
          <div>
            <span class="stat-card-value">{{
              formatNumber(fullStats.total_subscribers ?? 0)
            }}</span>
            <span class="stat-card-label">подписчиков</span>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-ruble-sign"></i>
          <div>
            <span class="stat-card-value"
              >{{ formatNumber(fullStats.total_earnings ?? 0) }} ₽</span
            >
            <span class="stat-card-label">всего выручка</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Графики за 7 дней -->
    <div class="charts-row">
      <div class="chart-card">
        <h3>Продажи за 7 дней</h3>
        <canvas ref="salesChartCanvas"></canvas>
        <div
          v-if="!fullStats.sales_chart_last_7_days?.length"
          class="empty-chart"
        >
          Нет данных
        </div>
      </div>
      <div class="chart-card">
        <h3>Прослушивания за 7 дней</h3>
        <canvas ref="playsChartCanvas"></canvas>
        <div
          v-if="!fullStats.plays_chart_last_7_days?.length"
          class="empty-chart"
        >
          Нет данных
        </div>
      </div>
    </div>

    <!-- Выручка по месяцам (последние 6 месяцев) -->
    <div class="chart-card full-width">
      <h3>Динамика выручки по месяцам</h3>
      <canvas ref="monthlyEarningsCanvas"></canvas>
      <div v-if="!fullStats.earnings_last_6_months?.length" class="empty-chart">
        Нет данных
      </div>
    </div>

    <!-- Топ треков -->
    <div class="top-tracks-row">
      <div class="top-tracks-card">
        <h3>🏆 Топ треков по продажам</h3>
        <div
          v-for="track in fullStats.top_tracks_by_sales"
          :key="track.track_id"
          class="top-track-item"
        >
          <img
            :src="track.cover_url || '/default-cover.jpg'"
            class="top-track-img"
          />
          <div class="top-track-info">
            <div class="top-track-title">{{ track.title }}</div>
            <div class="top-track-stats">
              {{ track.sales_count }} продаж · {{ track.revenue }} ₽
            </div>
          </div>
        </div>
        <div v-if="!fullStats.top_tracks_by_sales?.length" class="empty-state">
          Нет продаж
        </div>
      </div>
      <div class="top-tracks-card">
        <h3>🔥 Топ треков по прослушиваниям</h3>
        <div
          v-for="track in fullStats.top_tracks_by_plays"
          :key="track.track_id"
          class="top-track-item"
        >
          <img
            :src="track.cover_url || '/default-cover.jpg'"
            class="top-track-img"
          />
          <div class="top-track-info">
            <div class="top-track-title">{{ track.title }}</div>
            <div class="top-track-stats">
              {{ formatNumber(track.plays) }} прослушиваний
            </div>
          </div>
        </div>
        <div v-if="!fullStats.top_tracks_by_plays?.length" class="empty-state">
          Нет данных
        </div>
      </div>
    </div>

    <!-- Продажи по типам лицензий -->
    <div class="chart-card">
      <h3>Продажи по типам лицензий</h3>
      <div class="license-stats" v-if="fullStats.sales_by_license?.length">
        <div
          v-for="lic in fullStats.sales_by_license"
          :key="lic.license_type"
          class="license-item"
        >
          <span class="license-name">{{ lic.license_type }}</span>
          <span class="license-count">{{ lic.count }} продаж</span>
          <span class="license-amount">{{ lic.total_amount }} ₽</span>
        </div>
      </div>
      <div v-else class="empty-state">Нет продаж по лицензиям</div>
    </div>

    <!-- Список битов автора -->
    <div class="beats-section">
      <h2><i class="fas fa-drumstick-bite"></i> Мои биты</h2>
      <div class="beats-grid">
        <div v-for="beat in tracks" :key="beat.id" class="beat-card">
          <img
            :src="beat.cover_url"
            :alt="beat.title"
            class="beat-cover"
            @error="handleImageError"
          />
          <div class="beat-overlay">
            <button class="play-btn" @click="playTrack(beat)">
              <i class="fas fa-play"></i>
            </button>
            <button class="like-btn" @click="toggleFavorite(beat.id)">
              <i class="far fa-heart"></i>
            </button>
          </div>
          <div class="beat-info">
            <div>
              <h3>{{ beat.title }}</h3>
              <p class="beat-meta">
                {{ beat.plays || 0 }} прослушиваний ·
                {{ beat.sales || 0 }} продаж
              </p>
            </div>
            <p class="beat-price">{{ beat.price }} ₽</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Ссылка на загрузку нового бита -->
    <div class="upload-link">
      <router-link to="/profile?tab=upload" class="upload-trigger">
        <i class="fas fa-plus-circle"></i> Загрузить новый бит
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject, nextTick } from "vue";
import { Chart, registerables } from "chart.js";
import api from "../api";

Chart.register(...registerables);

// Плеер из инжекта
const { playTrack } = inject("player", {
  playTrack: (t) => console.log("play", t),
});
const editingBio = ref(false);
const editBioText = ref('');

const startEditBio = () => {
  editBioText.value = author.value.bio || '';
  editingBio.value = true;
};

const saveBio = async () => {
  try {
    await api.patch('/authors/me', { bio: editBioText.value });
    author.value.bio = editBioText.value;
    editingBio.value = false;
  } catch (err) {
    console.error('Ошибка сохранения биографии', err);
  }
};

const cancelEditBio = () => {
  editingBio.value = false;
};
// Данные
const author = ref({});
const tracks = ref([]);
const fullStats = ref({
  total_tracks: 0,
  total_plays: 0,
  total_favorites: 0,
  total_subscribers: 0,
  total_earnings: 0,
  sales_this_month: 0,
  monthly_earnings: 0,
  sales_chart_last_7_days: [],
  plays_chart_last_7_days: [],
  earnings_last_6_months: [],
  sales_by_license: [],
  top_tracks_by_sales: [],
  top_tracks_by_plays: [],
  average_rating: 0,
});

// Refs для canvas
const salesChartCanvas = ref(null);
const playsChartCanvas = ref(null);
const monthlyEarningsCanvas = ref(null);

let salesChart = null;
let playsChart = null;
let monthlyChart = null;

// Аватар автора
const authorAvatar = computed(() => {
  if (!author.value.photo_url) return "/default-avatar.png";
  if (author.value.photo_url.startsWith("http")) return author.value.photo_url;
  const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
  return `${baseUrl}${author.value.photo_url}`;
});

// Форматирование чисел
const formatNumber = (num) => {
  return new Intl.NumberFormat("ru-RU").format(num);
};

// Обработчик ошибок изображений
const handleImageError = (e) => {
  e.target.src = "/default-cover.jpg";
};

// Загрузка профиля и треков (существующие методы)
const fetchAuthorData = async () => {
  try {
    const { data: authorData } = await api.get("/authors/me");
    author.value = authorData;
    const { data: tracksData } = await api.get("/authors/me/tracks");
    tracks.value = tracksData;
  } catch (err) {
    console.error("Ошибка загрузки данных автора", err);
  }
};

// Загрузка расширенной статистики
const fetchFullStats = async () => {
  try {
    const { data } = await api.get("/authors/me/full-stats");
    fullStats.value = data;
    await nextTick();
    renderCharts();
  } catch (err) {
    console.error("Ошибка загрузки полной статистики", err);
  }
};

// Отрисовка графиков через Chart.js
const renderCharts = () => {
  // Продажи за 7 дней (bar)
  if (
    salesChartCanvas.value &&
    fullStats.value.sales_chart_last_7_days?.length
  ) {
    if (salesChart) salesChart.destroy();
    salesChart = new Chart(salesChartCanvas.value, {
      type: "bar",
      data: {
        labels: [
          "День 1",
          "День 2",
          "День 3",
          "День 4",
          "День 5",
          "День 6",
          "Сегодня",
        ],
        datasets: [
          {
            label: "Продажи",
            data: fullStats.value.sales_chart_last_7_days,
            backgroundColor: "#a855f7",
            borderRadius: 8,
            barPercentage: 0.7,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: { legend: { position: "top" } },
      },
    });
  }

  // Прослушивания за 7 дней (line)
  if (
    playsChartCanvas.value &&
    fullStats.value.plays_chart_last_7_days?.length
  ) {
    if (playsChart) playsChart.destroy();
    playsChart = new Chart(playsChartCanvas.value, {
      type: "line",
      data: {
        labels: [
          "День 1",
          "День 2",
          "День 3",
          "День 4",
          "День 5",
          "День 6",
          "Сегодня",
        ],
        datasets: [
          {
            label: "Прослушивания",
            data: fullStats.value.plays_chart_last_7_days,
            borderColor: "#3b82f6",
            backgroundColor: "rgba(59,130,246,0.1)",
            tension: 0.3,
            fill: true,
            pointBackgroundColor: "#3b82f6",
          },
        ],
      },
      options: { responsive: true, maintainAspectRatio: true },
    });
  }

  // Выручка по месяцам
  if (
    monthlyEarningsCanvas.value &&
    fullStats.value.earnings_last_6_months?.length
  ) {
    if (monthlyChart) monthlyChart.destroy();
    const months = fullStats.value.earnings_last_6_months.map(
      (m) => m.month?.slice(5) || m.month
    );
    const amounts = fullStats.value.earnings_last_6_months.map((m) => m.amount);
    monthlyChart = new Chart(monthlyEarningsCanvas.value, {
      type: "line",
      data: {
        labels: months,
        datasets: [
          {
            label: "Выручка (₽)",
            data: amounts,
            borderColor: "#10b981",
            backgroundColor: "rgba(16,185,129,0.1)",
            tension: 0.2,
            fill: true,
          },
        ],
      },
      options: { responsive: true, maintainAspectRatio: true },
    });
  }
};

// Лайк (заглушка)
const toggleFavorite = (trackId) => {
  console.log("toggle favorite", trackId);
};

onMounted(() => {
  fetchAuthorData();
  fetchFullStats();
});
</script>

<style scoped>
.artist-dashboard {
  max-width: 100%;
  margin: 0 auto;
}

.artist-header {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  align-items: center;
  background: linear-gradient(
    145deg,
    rgba(168, 85, 247, 0.1),
    rgba(59, 130, 246, 0.05)
  );
  padding: 1.5rem;
  border-radius: 40px;
  border: 1px solid rgba(168, 85, 247, 0.2);
  backdrop-filter: blur(10px);
}

.avatar-wrapper {
  position: relative;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  overflow: hidden;
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: relative;
  z-index: 2;
}

.avatar-ring {
  position: absolute;
  top: -5px;
  left: -5px;
  right: -5px;
  bottom: -5px;
  border-radius: 50%;
  background: linear-gradient(45deg, #a855f7, #3b82f6, #a855f7);
  animation: rotate 4s linear infinite;
  z-index: 1;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.artist-info {
  flex: 1;
}

.artist-info h1 {
  font-size: 2rem;
  background: linear-gradient(135deg, #fff, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}

.bio {
  color: #a0a0b0;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.stats {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #fff;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.8rem;
  color: #a0a0b0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sales-stats {
  margin-bottom: 2rem;
}

.sales-stats h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.03);
  padding: 1rem;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-card i {
  font-size: 2rem;
  color: #a855f7;
}

.stat-card-value {
  display: block;
  font-size: 1.2rem;
  font-weight: 700;
}

.stat-card-label {
  font-size: 0.8rem;
  color: #a0a0b0;
}

.charts-row {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.chart-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 20px;
  padding: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  flex: 1;
  min-width: 250px;
}

.chart-card h3 {
  margin-bottom: 1rem;
  font-size: 1.2rem;
  color: #e0e0e0;
}

.full-width {
  width: 100%;
  margin-bottom: 2rem;
}

.top-tracks-row {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.top-tracks-card {
  flex: 1;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 20px;
  padding: 1rem;
}

.top-track-item {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.top-track-img {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  object-fit: cover;
}

.top-track-info {
  flex: 1;
}

.top-track-title {
  font-weight: 600;
  font-size: 0.9rem;
}

.top-track-stats {
  font-size: 0.75rem;
  color: #a0a0b0;
}

.license-stats {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.license-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
}

.license-name {
  text-transform: capitalize;
  font-weight: 600;
  color: #c084fc;
}

.empty-state,
.empty-chart {
  color: #a0a0b0;
  text-align: center;
  padding: 1rem;
}

.beats-section {
  margin: 2rem 0;
}

.beats-section h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.beats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1rem;
}

.beat-card {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s;
  border: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
}

.beat-card:hover {
  transform: translateY(-5px);
  border-color: #a855f7;
  box-shadow: 0 10px 20px rgba(168, 85, 247, 0.2);
}

.beat-cover {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
}

.beat-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.8rem;
  opacity: 0;
  transition: opacity 0.3s;
}

.beat-card:hover .beat-overlay {
  opacity: 1;
}

.play-btn,
.like-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: #a855f7;
  color: white;
  font-size: 1rem;
  cursor: pointer;
  transition: transform 0.2s;
}

.like-btn {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(5px);
}

.play-btn:hover,
.like-btn:hover {
  transform: scale(1.1);
}

.beat-info {
  padding: 0.8rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.beat-info h3 {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.2rem;
}

.beat-meta {
  font-size: 0.7rem;
  color: #a0a0b0;
}

.beat-price {
  color: #a855f7;
  font-weight: 700;
  font-size: 1rem;
}

.upload-link {
  text-align: center;
  margin-top: 2rem;
}

.upload-trigger {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  color: white;
  padding: 0.6rem 1.5rem;
  border-radius: 40px;
  text-decoration: none;
  font-weight: 600;
  transition: transform 0.2s;
}

.upload-trigger:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(168, 85, 247, 0.4);
}

@media (max-width: 768px) {
  .artist-header {
    flex-direction: column;
    text-align: center;
  }
  .stats {
    justify-content: center;
  }
  .charts-row {
    flex-direction: column;
  }
}
.edit-icon {
  margin-left: 10px;
  font-size: 0.9rem;
  cursor: pointer;
  opacity: 0.6;
  transition: 0.2s;
}
.edit-icon:hover {
  opacity: 1;
}
.bio-edit textarea {
  width: 100%;
  background: #1e1e2f;
  border: 1px solid #a855f7;
  border-radius: 12px;
  padding: 8px 12px;
  color: white;
  font-family: inherit;
}
.edit-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}
.save-btn, .cancel-btn {
  padding: 4px 16px;
  border-radius: 20px;
  border: none;
  cursor: pointer;
}
.save-btn {
  background: #a855f7;
  color: white;
}
.cancel-btn {
  background: #2a2a3a;
  color: #ccc;
}
</style>
