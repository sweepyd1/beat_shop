<template>
  <div class="stats-container">
    <div class="header">
      <h1
        class="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent"
      >
        📊 Статистика магазина
      </h1>
      <p class="text-gray-400">
        Аналитика продаж, популярные треки и активность пользователей
      </p>
    </div>

    <!-- Карточки с ключевыми метриками -->
    <div class="stats-grid" v-if="!loading.metrics">
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-users"></i></div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(metrics.total_users) }}</div>
          <div class="stat-label">Всего пользователей</div>
          <div class="stat-change positive">
            +{{ metrics.new_users_last_week }} за неделю
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-chart-line"></i></div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(metrics.total_revenue) }} ₽</div>
          <div class="stat-label">Общая выручка</div>
          <div class="stat-change positive">+{{ metrics.revenue_growth }}%</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-shopping-cart"></i></div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(metrics.total_purchases) }}</div>
          <div class="stat-label">Всего покупок</div>
          <div class="stat-change">{{ formatNumber(metrics.avg_check) }} ₽ средний чек</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-headphones"></i></div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(metrics.total_listens) }}</div>
          <div class="stat-label">Прослушиваний</div>
          <div class="stat-change">за всё время</div>
        </div>
      </div>
    </div>
    <div v-else class="loading-placeholder">Загрузка метрик...</div>

    <!-- Графики -->
    <div class="charts-row">
      <div class="chart-card">
        <h3>Продажи по дням (последние 7 дней)</h3>
        <canvas ref="salesChartRef"></canvas>
      </div>
      <div class="chart-card">
        <h3>Новые пользователи по дням</h3>
        <canvas ref="usersChartRef"></canvas>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <h3>Топ-5 треков по выручке</h3>
        <canvas ref="topTracksChartRef"></canvas>
      </div>
      <div class="chart-card">
        <h3>Продажи по жанрам</h3>
        <canvas ref="genresChartRef"></canvas>
      </div>
    </div>

    <!-- Таблица топ треков -->
    <div class="card">
      <h3>🏆 Топ-10 самых продаваемых треков</h3>
      <div class="table-wrapper">
        <table class="stats-table">
          <thead>
            <tr>
              <th>Обложка</th>
              <th>Название</th>
              <th>Автор</th>
              <th>Жанр</th>
              <th>Продажи</th>
              <th>Выручка</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="track in topTracks" :key="track.id">
              <td><img :src="track.cover_url || '/default-cover.jpg'" class="table-cover" @error="handleImageError" /></td>
              <td>{{ track.title }}</td>
              <td>{{ track.author_name }}</td>
              <td>{{ track.genre_name }}</td>
              <td>{{ track.sales_count }}</td>
              <td>{{ formatNumber(track.revenue) }} ₽</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { Chart, registerables } from "chart.js";
import api from "../api"; // путь к вашему API-клиенту

Chart.register(...registerables);

// Состояния
const metrics = ref({
  total_users: 0,
  new_users_last_week: 0,
  total_revenue: 0,
  revenue_growth: 0,
  total_purchases: 0,
  avg_check: 0,
  total_listens: 0,
});
const topTracks = ref([]);
const dailySales = ref([]);      // массив объектов { date, revenue }
const dailyUsers = ref([]);      // массив объектов { date, count }
const genreSales = ref([]);      // массив объектов { genre_name, revenue }

const loading = ref({
  metrics: true,
  topTracks: true,
  sales: true,
  users: true,
  genres: true,
});

// Рефы для графиков
const salesChartRef = ref(null);
const usersChartRef = ref(null);
const topTracksChartRef = ref(null);
const genresChartRef = ref(null);

let salesChartInstance = null;
let usersChartInstance = null;
let topTracksChartInstance = null;
let genresChartInstance = null;

// Форматирование чисел
const formatNumber = (num) => {
  if (num === undefined || num === null) return '0';
  return new Intl.NumberFormat('ru-RU').format(num);
};

const handleImageError = (e) => {
  e.target.src = '/default-cover.jpg';
};

// Загрузка метрик
const fetchMetrics = async () => {
  try {
    const { data } = await api.get('/admin/stats/metrics');
    metrics.value = data;
  } catch (err) {
    console.error('Ошибка загрузки метрик:', err);
  } finally {
    loading.value.metrics = false;
  }
};

// Загрузка топ треков
const fetchTopTracks = async () => {
  try {
    const { data } = await api.get('/admin/stats/top-tracks?limit=10');
    topTracks.value = data;
  } catch (err) {
    console.error('Ошибка загрузки топ треков:', err);
  } finally {
    loading.value.topTracks = false;
  }
};

// Загрузка продаж по дням
const fetchDailySales = async () => {
  try {
    const { data } = await api.get('/admin/stats/sales-daily?days=7');
    dailySales.value = data;
  } catch (err) {
    console.error('Ошибка загрузки дневных продаж:', err);
  } finally {
    loading.value.sales = false;
  }
};

// Загрузка новых пользователей по дням
const fetchDailyUsers = async () => {
  try {
    const { data } = await api.get('/admin/stats/users-daily?days=7');
    dailyUsers.value = data;
  } catch (err) {
    console.error('Ошибка загрузки дневных пользователей:', err);
  } finally {
    loading.value.users = false;
  }
};

// Загрузка продаж по жанрам
const fetchGenreSales = async () => {
  try {
    const { data } = await api.get('/admin/stats/genres');
    genreSales.value = data;
  } catch (err) {
    console.error('Ошибка загрузки продаж по жанрам:', err);
  } finally {
    loading.value.genres = false;
  }
};

// Инициализация графиков после получения данных
const initCharts = () => {
  if (!dailySales.value.length || !dailyUsers.value.length || !topTracks.value.length || !genreSales.value.length) return;

  // 1. График продаж (линия)
  const salesLabels = dailySales.value.map(item => {
    const d = new Date(item.date);
    return d.toLocaleDateString('ru-RU', { weekday: 'short' });
  });
  const salesValues = dailySales.value.map(item => item.revenue);

  if (salesChartRef.value) {
    if (salesChartInstance) salesChartInstance.destroy();
    salesChartInstance = new Chart(salesChartRef.value, {
      type: 'line',
      data: {
        labels: salesLabels,
        datasets: [{
          label: 'Выручка (₽)',
          data: salesValues,
          borderColor: '#a855f7',
          backgroundColor: 'rgba(168,85,247,0.1)',
          tension: 0.3,
          fill: true,
        }]
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }

  // 2. График новых пользователей (столбцы)
  const userLabels = dailyUsers.value.map(item => {
    const d = new Date(item.date);
    return d.toLocaleDateString('ru-RU', { weekday: 'short' });
  });
  const userValues = dailyUsers.value.map(item => item.count);

  if (usersChartRef.value) {
    if (usersChartInstance) usersChartInstance.destroy();
    usersChartInstance = new Chart(usersChartRef.value, {
      type: 'bar',
      data: {
        labels: userLabels,
        datasets: [{
          label: 'Новые пользователи',
          data: userValues,
          backgroundColor: '#3b82f6',
          borderRadius: 8,
        }]
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }

  // 3. Топ-5 треков по выручке (горизонтальная бар)
  const top5 = topTracks.value.slice(0, 5);
  const trackLabels = top5.map(t => t.title);
  const trackValues = top5.map(t => t.revenue);

  if (topTracksChartRef.value) {
    if (topTracksChartInstance) topTracksChartInstance.destroy();
    topTracksChartInstance = new Chart(topTracksChartRef.value, {
      type: 'bar',
      data: {
        labels: trackLabels,
        datasets: [{
          label: 'Выручка (₽)',
          data: trackValues,
          backgroundColor: '#f97316',
        }]
      },
      options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false }
    });
  }

  // 4. Продажи по жанрам (пончик)
  const genreLabels = genreSales.value.map(g => g.genre_name);
  const genreValues = genreSales.value.map(g => g.revenue);
  const backgroundColors = ['#a855f7', '#3b82f6', '#ec4899', '#f97316', '#10b981', '#8b5cf6', '#06b6d4', '#ef4444'];

  if (genresChartRef.value) {
    if (genresChartInstance) genresChartInstance.destroy();
    genresChartInstance = new Chart(genresChartRef.value, {
      type: 'doughnut',
      data: {
        labels: genreLabels,
        datasets: [{
          data: genreValues,
          backgroundColor: backgroundColors.slice(0, genreLabels.length),
        }]
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }
};

// Загрузка всех данных и инициализация графиков
const loadAllData = async () => {
  await Promise.all([
    fetchMetrics(),
    fetchTopTracks(),
    fetchDailySales(),
    fetchDailyUsers(),
    fetchGenreSales()
  ]);
  initCharts();
};

onMounted(() => {
  loadAllData();
});
</script>

<style scoped>
/* Ваши стили остаются без изменений (из исходного компонента) */
.stats-container {
  max-width: 1400px;
  margin: 2rem auto;
  padding: 0 1rem;
}
.header {
  text-align: center;
  margin-bottom: 2rem;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}
.stat-card {
  background: rgba(20, 20, 30, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(168, 85, 247, 0.2);
  border-radius: 1.5rem;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s;
}
.stat-card:hover {
  transform: translateY(-4px);
}
.stat-icon {
  font-size: 2.5rem;
  color: #a855f7;
}
.stat-info {
  flex: 1;
}
.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: white;
}
.stat-label {
  color: #a0a0b0;
  font-size: 0.9rem;
}
.stat-change {
  font-size: 0.8rem;
  margin-top: 0.25rem;
}
.stat-change.positive {
  color: #10b981;
}
.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}
.chart-card,
.card {
  background: rgba(20, 20, 30, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(168, 85, 247, 0.2);
  border-radius: 1.5rem;
  padding: 1.5rem;
}
.chart-card h3,
.card h3 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  color: #e2e8f0;
}
.chart-card canvas {
  max-height: 300px;
  width: 100%;
}
.table-wrapper {
  overflow-x: auto;
}
.stats-table {
  width: 100%;
  border-collapse: collapse;
}
.stats-table th,
.stats-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.stats-table th {
  color: #a855f7;
  font-weight: 600;
}
.table-cover {
  width: 40px;
  height: 40px;
  border-radius: 0.5rem;
  object-fit: cover;
}
.loading-placeholder {
  text-align: center;
  padding: 2rem;
  color: #a0a0b0;
}
@media (max-width: 768px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
  .stat-card {
    flex-direction: column;
    text-align: center;
  }
}
</style>