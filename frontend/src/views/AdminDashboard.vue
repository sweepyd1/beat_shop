<template>
  <div class="admin-dashboard">
    <!-- Анимированный фон -->
    <div class="dashboard-glow"></div>

    <div class="container">
      <!-- Заголовок -->
      <div class="dashboard-header" data-aos="fade-up">
        <div class="badge">Административная панель</div>
        <h1 class="title">
          <span class="gradient-text">Управление проектом</span>
        </h1>
        <p class="subtitle">Быстрый доступ к основным функциям управления</p>
      </div>

      <!-- Сетка карточек -->
      <div class="cards-grid" data-aos="fade-up" data-aos-delay="100">
        <!-- Карточка: Треки -->
        <router-link to="/admin/tracks" class="dashboard-card">
          <div class="card-icon music">
            <i class="fas fa-headphones"></i>
          </div>
          <h3>Управление треками</h3>
          <p>Добавление, редактирование, удаление треков. Управление жанрами и исполнителями.</p>
          <span class="card-link">Перейти →</span>
        </router-link>

        <!-- Карточка: Статистика -->
        <router-link to="/admin/stats" class="dashboard-card">
          <div class="card-icon stats">
            <i class="fas fa-chart-line"></i>
          </div>
          <h3>Общая статистика</h3>
          <p>Динамика регистраций, доходы, популярные треки, активность пользователей.</p>
          <span class="card-link">Перейти →</span>
        </router-link>

        <!-- Карточка: Статистика пользователей -->
        <router-link to="/admin/user-stats" class="dashboard-card">
          <div class="card-icon user-stats">
            <i class="fas fa-users"></i>
          </div>
          <h3>Статистика пользователей</h3>
          <p>Топ покупатели, распределение по ролям, активность за период.</p>
          <span class="card-link">Перейти →</span>
        </router-link>

        <!-- Карточка: Пользователи -->
        <router-link to="/admin/users" class="dashboard-card">
          <div class="card-icon users">
            <i class="fas fa-user-cog"></i>
          </div>
          <h3>Управление пользователями</h3>
          <p>Просмотр, создание, блокировка, редактирование профилей пользователей.</p>
          <span class="card-link">Перейти →</span>
        </router-link>
      </div>

      <!-- Блок с дополнительной информацией (опционально) -->
      <div class="info-section" data-aos="fade-up" data-aos-delay="200">
        <div class="info-card">
          <i class="fas fa-shield-alt"></i>
          <div>
            <h4>Права доступа</h4>
            <p>Вам доступны все функции управления. Будьте внимательны при изменении данных.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Если используется AOS для анимаций, можно подключить, но не обязательно
// import AOS from 'aos'; onMounted(() => AOS.refresh());
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a0f 0%, #12121a 100%);
  padding: 3rem 1rem;
  position: relative;
  overflow-x: hidden;
}

.dashboard-glow {
  position: fixed;
  top: -20%;
  left: -20%;
  width: 140%;
  height: 140%;
  background: radial-gradient(circle at 20% 30%, rgba(168,85,247,0.15), transparent 70%);
  pointer-events: none;
  z-index: 0;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 4rem;
}

.badge {
  display: inline-block;
  background: rgba(168,85,247,0.2);
  backdrop-filter: blur(4px);
  padding: 0.3rem 1.2rem;
  border-radius: 2rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #c084fc;
  border: 1px solid rgba(168,85,247,0.3);
  margin-bottom: 1rem;
}

.title {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 1rem;
}

.gradient-text {
  background: linear-gradient(135deg, #a855f7, #ec4899, #3b82f6);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
}

.subtitle {
  color: #9ca3af;
  font-size: 1.2rem;
}

/* Сетка карточек */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.dashboard-card {
  background: rgba(20, 20, 30, 0.7);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(168,85,247,0.2);
  border-radius: 1.5rem;
  padding: 2rem;
  text-decoration: none;
  color: inherit;
  transition: all 0.3s cubic-bezier(0.2, 0.9, 0.4, 1.1);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

.dashboard-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #a855f7, #ec4899);
  transform: scaleX(0);
  transition: transform 0.3s;
}

.dashboard-card:hover::before {
  transform: scaleX(1);
}

.dashboard-card:hover {
  transform: translateY(-8px);
  border-color: rgba(168,85,247,0.5);
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.5);
}

.card-icon {
  width: 64px;
  height: 64px;
  border-radius: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  margin-bottom: 1.5rem;
  background: rgba(0, 0, 0, 0.3);
  transition: all 0.3s;
}

.dashboard-card:hover .card-icon {
  transform: scale(1.05);
}

.card-icon.music { background: linear-gradient(135deg, #3b82f6, #8b5cf6); }
.card-icon.stats { background: linear-gradient(135deg, #10b981, #34d399); }
.card-icon.user-stats { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
.card-icon.users { background: linear-gradient(135deg, #ef4444, #f97316); }

.dashboard-card h3 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  color: white;
}

.dashboard-card p {
  color: #9ca3af;
  line-height: 1.5;
  margin-bottom: 1.5rem;
  flex-grow: 1;
}

.card-link {
  color: #c084fc;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: gap 0.2s;
}

.dashboard-card:hover .card-link {
  gap: 1rem;
}

/* Инфо блок */
.info-section {
  margin-top: 2rem;
}

.info-card {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 1rem;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid rgba(168,85,247,0.2);
  backdrop-filter: blur(8px);
}

.info-card i {
  font-size: 2rem;
  color: #a855f7;
}

.info-card h4 {
  margin: 0 0 0.25rem 0;
  color: white;
}

.info-card p {
  margin: 0;
  font-size: 0.9rem;
  color: #9ca3af;
}

/* Адаптив */
@media (max-width: 768px) {
  .title {
    font-size: 2rem;
  }
  .cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>