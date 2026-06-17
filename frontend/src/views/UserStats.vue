<template>
  <div class="stats-container">
    <div class="header">
      <h1
        class="text-3xl font-bold bg-gradient-to-r from-blue-400 to-indigo-600 bg-clip-text text-transparent"
      >
        👥 Статистика пользователей
      </h1>
      <p class="text-gray-400">
        Аналитика аудитории, активность, подписки и покупательское поведение
      </p>
    </div>

    
    <div class="stats-grid" v-if="!loading.metrics">
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-users"></i></div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(metrics.total_users) }}</div>
          <div class="stat-label">Всего пользователей</div>
          <div class="stat-change positive">+{{ metrics.new_users_last_week }} за неделю</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-user-check"></i></div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(metrics.active_users_last_month) }}</div>
          <div class="stat-label">Активны за месяц</div>
          <div class="stat-change">{{ Math.round(metrics.active_users_last_month / metrics.total_users * 100) }}% от всех</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-heart"></i></div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(metrics.total_subscriptions) }}</div>
          <div class="stat-label">Подписок на авторов</div>
          <div class="stat-change">всего</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-shopping-cart"></i></div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(metrics.total_purchases_amount) }} ₽</div>
          <div class="stat-label">Общая выручка от пользователей</div>
          <div class="stat-change">{{ metrics.avg_purchases_per_user.toFixed(1) }} покупок на покупателя</div>
        </div>
      </div>
    </div>
    <div v-else class="loading-placeholder">Загрузка метрик...</div>

    
    <div class="charts-row">
      <div class="chart-card">
        <h3>Регистрации по дням (последние 30 дней)</h3>
        <canvas ref="registrationsChartRef"></canvas>
      </div>
      <div class="chart-card">
        <h3>Покупки по дням</h3>
        <canvas ref="purchasesChartRef"></canvas>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <h3>Распределение по ролям</h3>
        <canvas ref="rolesChartRef"></canvas>
      </div>
      <div class="chart-card">
        <h3>Топ-10 покупателей по сумме</h3>
        <canvas ref="topBuyersChartRef"></canvas>
      </div>
    </div>

    
    <div class="card">
      <h3>🎧 Топ-10 самых активных слушателей</h3>
      <div class="table-wrapper">
        <table class="stats-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Имя</th>
              <th>Логин</th>
              <th>Прослушиваний</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="listener in topListeners" :key="listener.user_id">
              <td>{{ listener.user_id }}</td>
              <td>{{ listener.full_name }}</td>
              <td>{{ listener.login }}</td>
              <td>{{ formatNumber(listener.listen_count) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    
    <div class="card">
      <h3>💰 Топ-10 покупателей по сумме трат</h3>
      <div class="table-wrapper">
        <table class="stats-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Имя</th>
              <th>Логин</th>
              <th>Сумма трат</th>
              <th>Кол-во покупок</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="buyer in topBuyers" :key="buyer.user_id">
              <td>{{ buyer.user_id }}</td>
              <td>{{ buyer.full_name }}</td>
              <td>{{ buyer.login }}</td>
              <td>{{ formatNumber(buyer.total_spent) }} ₽</td>
              <td>{{ buyer.purchases_count }}</td>
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
import api from "../api";

Chart.register(...registerables);


const metrics = ref({
  total_users: 0,
  new_users_last_week: 0,
  active_users_last_month: 0,
  total_subscriptions: 0,
  avg_purchases_per_user: 0,
  total_purchases_amount: 0,
});
const dailyRegistrations = ref([]);   
const dailyPurchases = ref([]);       
const roleDistribution = ref([]);     
const topBuyers = ref([]);            
const topListeners = ref([]);         

const loading = ref({
  metrics: true,
  registrations: true,
  purchases: true,
  roles: true,
  topBuyers: true,
  topListeners: true,
});


const registrationsChartRef = ref(null);
const purchasesChartRef = ref(null);
const rolesChartRef = ref(null);
const topBuyersChartRef = ref(null);

let registrationsChart = null;
let purchasesChart = null;
let rolesChart = null;
let topBuyersChart = null;

const formatNumber = (num) => {
  if (num === undefined || num === null) return '0';
  return new Intl.NumberFormat('ru-RU').format(num);
};


const fetchUserMetrics = async () => {
  try {
    const { data } = await api.get('/admin/stats/user-metrics');
    metrics.value = data;
  } catch (err) {
    console.error('Ошибка загрузки метрик пользователей:', err);
  } finally {
    loading.value.metrics = false;
  }
};


const fetchDailyRegistrations = async () => {
  try {
    const { data } = await api.get('/admin/stats/user-daily-registrations?days=30');
    dailyRegistrations.value = data;
  } catch (err) {
    console.error('Ошибка загрузки регистраций:', err);
  } finally {
    loading.value.registrations = false;
  }
};


const fetchDailyPurchases = async () => {
  try {
    const { data } = await api.get('/admin/stats/user-daily-purchases?days=30');
    dailyPurchases.value = data;
  } catch (err) {
    console.error('Ошибка загрузки покупок по дням:', err);
  } finally {
    loading.value.purchases = false;
  }
};


const fetchRoleDistribution = async () => {
  try {
    const { data } = await api.get('/admin/stats/user-role-distribution');
    roleDistribution.value = data;
  } catch (err) {
    console.error('Ошибка загрузки ролей:', err);
  } finally {
    loading.value.roles = false;
  }
};


const fetchTopBuyers = async () => {
  try {
    const { data } = await api.get('/admin/stats/user-top-buyers?limit=10');
    topBuyers.value = data;
  } catch (err) {
    console.error('Ошибка загрузки топ покупателей:', err);
  } finally {
    loading.value.topBuyers = false;
  }
};


const fetchTopListeners = async () => {
  try {
    const { data } = await api.get('/admin/stats/user-top-listeners?limit=10');
    topListeners.value = data;
  } catch (err) {
    console.error('Ошибка загрузки топ слушателей:', err);
  } finally {
    loading.value.topListeners = false;
  }
};


const initCharts = () => {
  
  if (dailyRegistrations.value.length && registrationsChartRef.value) {
    const labels = dailyRegistrations.value.map(item => {
      const d = new Date(item.date);
      return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
    });
    const counts = dailyRegistrations.value.map(item => item.count);
    if (registrationsChart) registrationsChart.destroy();
    registrationsChart = new Chart(registrationsChartRef.value, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Новые пользователи',
          data: counts,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59,130,246,0.1)',
          tension: 0.3,
          fill: true,
        }]
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }

  
  if (dailyPurchases.value.length && purchasesChartRef.value) {
    const labels = dailyPurchases.value.map(item => {
      const d = new Date(item.date);
      return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
    });
    const purchaseCounts = dailyPurchases.value.map(item => item.purchase_count);
    const amounts = dailyPurchases.value.map(item => item.total_amount);
    if (purchasesChart) purchasesChart.destroy();
    purchasesChart = new Chart(purchasesChartRef.value, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Количество покупок',
            data: purchaseCounts,
            backgroundColor: '#10b981',
            yAxisID: 'y',
          },
          {
            label: 'Сумма (₽)',
            data: amounts,
            type: 'line',
            borderColor: '#f97316',
            backgroundColor: 'transparent',
            tension: 0.3,
            yAxisID: 'y1',
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          tooltip: { callbacks: { label: (ctx) => `${ctx.dataset.label}: ${ctx.raw}` } }
        },
        scales: {
          y: { title: { display: true, text: 'Кол-во покупок' } },
          y1: { position: 'right', title: { display: true, text: 'Сумма (₽)' } }
        }
      }
    });
  }

  
  if (roleDistribution.value.length && rolesChartRef.value) {
    const labels = roleDistribution.value.map(r => r.role);
    const counts = roleDistribution.value.map(r => r.count);
    const colors = ['#a855f7', '#3b82f6', '#ec4899'];
    if (rolesChart) rolesChart.destroy();
    rolesChart = new Chart(rolesChartRef.value, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{ data: counts, backgroundColor: colors }]
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }

  
  if (topBuyers.value.length && topBuyersChartRef.value) {
    const labels = topBuyers.value.map(b => b.full_name.length > 20 ? b.full_name.slice(0,20)+'…' : b.full_name);
    const amounts = topBuyers.value.map(b => b.total_spent);
    if (topBuyersChart) topBuyersChart.destroy();
    topBuyersChart = new Chart(topBuyersChartRef.value, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Сумма трат (₽)',
          data: amounts,
          backgroundColor: '#f59e0b',
        }]
      },
      options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false }
    });
  }
};


const loadAllData = async () => {
  await Promise.all([
    fetchUserMetrics(),
    fetchDailyRegistrations(),
    fetchDailyPurchases(),
    fetchRoleDistribution(),
    fetchTopBuyers(),
    fetchTopListeners(),
  ]);
  initCharts();
};

onMounted(() => {
  loadAllData();
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
  border: 1px solid rgba(59,130,246,0.2);
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
  color: #3b82f6;
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
  border: 1px solid rgba(59,130,246,0.2);
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
  color: #3b82f6;
  font-weight: 600;
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