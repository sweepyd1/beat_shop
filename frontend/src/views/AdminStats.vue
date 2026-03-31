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
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-users"></i></div>
        <div class="stat-info">
          <div class="stat-value">{{ metrics.totalUsers }}</div>
          <div class="stat-label">Всего пользователей</div>
          <div class="stat-change positive">
            +{{ metrics.newUsersLastWeek }} за неделю
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-chart-line"></i></div>
        <div class="stat-info">
          <div class="stat-value">{{ metrics.totalRevenue }} ₽</div>
          <div class="stat-label">Общая выручка</div>
          <div class="stat-change positive">+{{ metrics.revenueGrowth }}%</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-shopping-cart"></i></div>
        <div class="stat-info">
          <div class="stat-value">{{ metrics.totalPurchases }}</div>
          <div class="stat-label">Всего покупок</div>
          <div class="stat-change">{{ metrics.avgCheck }} ₽ средний чек</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-headphones"></i></div>
        <div class="stat-info">
          <div class="stat-value">{{ metrics.totalListens }}</div>
          <div class="stat-label">Прослушиваний</div>
          <div class="stat-change">за всё время</div>
        </div>
      </div>
    </div>

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
              <td><img :src="track.cover" class="table-cover" /></td>
              <td>{{ track.title }}</td>
              <td>{{ track.artist }}</td>
              <td>{{ track.genre }}</td>
              <td>{{ track.sales }}</td>
              <td>{{ track.revenue }} ₽</td>
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
Chart.register(...registerables);

// Моковые данные (замените на реальные API-вызовы позже)
const metrics = ref({
  totalUsers: 1248,
  newUsersLastWeek: 87,
  totalRevenue: 245780,
  revenueGrowth: 12.5,
  totalPurchases: 3420,
  avgCheck: 718,
  totalListens: 15890,
});

// Данные для графика продаж по дням (за последние 7 дней)
const salesData = {
  labels: ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
  values: [12500, 14800, 13200, 16700, 18900, 22400, 19800],
};

// Данные для графика новых пользователей
const usersData = {
  labels: ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
  values: [12, 18, 15, 22, 27, 34, 29],
};

// Топ треков для круговой диаграммы (выручка)
const topTracksChartData = {
  labels: [
    "Неоновая мечта",
    "В ритме дождя",
    "Космический вальс",
    "Закат на Марсе",
    "Электрический сон",
  ],
  values: [45200, 38700, 29100, 24500, 19800],
};

// Продажи по жанрам
const genresChartData = {
  labels: ["Электроника", "Рок", "Поп", "Хип-хоп", "Джаз", "Классика"],
  values: [125000, 87000, 65000, 42000, 28000, 15000],
};

// Таблица топ-10 треков
const topTracks = ref([
  {
    id: 1,
    title: "Неоновая мечта",
    artist: "ZOMBIE",
    genre: "Электроника",
    sales: 215,
    revenue: 45200,
    cover: "https://picsum.photos/id/29/60/60",
  },
  {
    id: 2,
    title: "В ритме дождя",
    artist: "Метель",
    genre: "Поп",
    sales: 189,
    revenue: 38700,
    cover: "https://picsum.photos/id/30/60/60",
  },
  {
    id: 3,
    title: "Космический вальс",
    artist: "Orion",
    genre: "Электроника",
    sales: 142,
    revenue: 29100,
    cover: "https://picsum.photos/id/31/60/60",
  },
  {
    id: 4,
    title: "Закат на Марсе",
    artist: "Deep Space",
    genre: "Рок",
    sales: 120,
    revenue: 24500,
    cover: "https://picsum.photos/id/32/60/60",
  },
  {
    id: 5,
    title: "Электрический сон",
    artist: "Volt",
    genre: "Электроника",
    sales: 98,
    revenue: 19800,
    cover: "https://picsum.photos/id/33/60/60",
  },
  {
    id: 6,
    title: "Тишина в нотах",
    artist: "Акустика",
    genre: "Джаз",
    sales: 87,
    revenue: 17400,
    cover: "https://picsum.photos/id/34/60/60",
  },
  {
    id: 7,
    title: "Ритмы улиц",
    artist: "Hip Hop Crew",
    genre: "Хип-хоп",
    sales: 76,
    revenue: 15200,
    cover: "https://picsum.photos/id/35/60/60",
  },
  {
    id: 8,
    title: "Время пришло",
    artist: "Рок-Острова",
    genre: "Рок",
    sales: 68,
    revenue: 13600,
    cover: "https://picsum.photos/id/36/60/60",
  },
  {
    id: 9,
    title: "Мелодия дождя",
    artist: "Piano Man",
    genre: "Классика",
    sales: 54,
    revenue: 10800,
    cover: "https://picsum.photos/id/37/60/60",
  },
  {
    id: 10,
    title: "Бит за битом",
    artist: "DJ Bass",
    genre: "Хип-хоп",
    sales: 49,
    revenue: 9800,
    cover: "https://picsum.photos/id/38/60/60",
  },
]);

let salesChartInstance = null;
let usersChartInstance = null;
let topTracksChartInstance = null;
let genresChartInstance = null;

function initCharts() {
  const ctxSales = document.querySelector("#salesChart canvas")
    ? document.querySelector("#salesChart canvas")
    : document.querySelector('canvas[ref="salesChart"]');
  // лучше получать по ref, но проще через getElementById или refs
  // Используем правильный способ: refs
  const salesCanvas =
    document.getElementById("salesChartCanvas") ||
    document.createElement("canvas");
  // но мы не задали id. Давайте переделаем: добавим id в canvas.
  // Прямо в шаблоне неудобно менять, поэтому создадим динамически через ref.
  // Перепишем: используем ref в template. Я сейчас исправлю шаблон.
}

// Так как мы используем ref в шаблоне, надо их объявить и потом примонтировать.
// Сделаем правильно:
const salesChartRef = ref(null);
const usersChartRef = ref(null);
const topTracksChartRef = ref(null);
const genresChartRef = ref(null);

onMounted(() => {
  // График продаж
  if (salesChartRef.value) {
    new Chart(salesChartRef.value, {
      type: "line",
      data: {
        labels: salesData.labels,
        datasets: [
          {
            label: "Выручка (₽)",
            data: salesData.values,
            borderColor: "#a855f7",
            backgroundColor: "rgba(168,85,247,0.1)",
            tension: 0.3,
            fill: true,
          },
        ],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
  }
  // График пользователей
  if (usersChartRef.value) {
    new Chart(usersChartRef.value, {
      type: "bar",
      data: {
        labels: usersData.labels,
        datasets: [
          {
            label: "Новые пользователи",
            data: usersData.values,
            backgroundColor: "#3b82f6",
            borderRadius: 8,
          },
        ],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
  }
  // Топ треков (горизонтальная или круговая? Сделаем горизонтальную бар)
  if (topTracksChartRef.value) {
    new Chart(topTracksChartRef.value, {
      type: "bar",
      data: {
        labels: topTracksChartData.labels,
        datasets: [
          {
            label: "Выручка (₽)",
            data: topTracksChartData.values,
            backgroundColor: "#f97316",
          },
        ],
      },
      options: { indexAxis: "y", responsive: true, maintainAspectRatio: false },
    });
  }
  // Жанры (круговая)
  if (genresChartRef.value) {
    new Chart(genresChartRef.value, {
      type: "doughnut",
      data: {
        labels: genresChartData.labels,
        datasets: [
          {
            data: genresChartData.values,
            backgroundColor: [
              "#a855f7",
              "#3b82f6",
              "#ec4899",
              "#f97316",
              "#10b981",
              "#8b5cf6",
            ],
          },
        ],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
  }
});
</script>

<style scoped>
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
