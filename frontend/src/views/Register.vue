<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="auth-title">Создать аккаунт</h1>
      <p class="auth-subtitle">Присоединяйтесь к BeatMarket</p>

      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label for="username">Имя пользователя</label>
          <div class="input-wrapper">
            <i class="fas fa-user"></i>
            <input
              type="text"
              id="username"
              v-model="username"
              placeholder="beatmaker"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <div class="input-wrapper">
            <i class="fas fa-envelope"></i>
            <input
              type="email"
              id="email"
              v-model="email"
              placeholder="your@email.com"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label for="password">Пароль</label>
          <div class="input-wrapper">
            <i class="fas fa-lock"></i>
            <input
              type="password"
              id="password"
              v-model="password"
              placeholder="••••••••"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label for="confirmPassword">Подтверждение пароля</label>
          <div class="input-wrapper">
            <i class="fas fa-lock"></i>
            <input
              type="password"
              id="confirmPassword"
              v-model="confirmPassword"
              placeholder="••••••••"
              required
            />
          </div>
        </div>
         <div class="form-group">
          <label>Роль</label>
          <div class="role-selector">
            <label class="role-option">
              <input type="radio" value="user" v-model="role" />
              <span>Покупатель</span>
            </label>
            <label class="role-option">
              <input type="radio" value="author" v-model="role" />
              <span>Автор</span>
            </label>
          </div>
        </div>
        <div class="form-options">
          <label class="checkbox">
            <input type="checkbox" v-model="agree" required />
            <span>Я принимаю <a href="#" class="terms-link">условия использования</a></span>
          </label>
        </div>

        <button type="submit" class="auth-button">Зарегистрироваться</button>
      </form>

      <div class="auth-footer">
        <p>Уже есть аккаунт?</p>
        <router-link to="/login" class="switch-link">Войти</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import { showError, showSuccess } from '@/utils/alert';  // <-- импорт
const authStore = useAuthStore();
const router = useRouter();

const username = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const role = ref('user');      // по умолчанию "Покупатель"
const agree = ref(false);
const isLoading = ref(false);

const handleRegister = async () => {
  if (password.value !== confirmPassword.value) {
    showError('Пароли не совпадают');
    return;
  }
  if (!agree.value) {
    showError('Примите условия использования');
    return;
  }

  isLoading.value = true;
  try {
    await authStore.register({
      full_name: username.value,
      login: username.value,
      email: email.value,
      password: password.value,
      role: role.value
    });
    showSuccess('Регистрация прошла успешно!');
    router.push('/');
  } catch (error) {
    console.error('Registration error:', error);
    showError(error);   // Функция сама извлечёт понятное сообщение
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>

.auth-page {
  min-height: calc(100vh - 80px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: radial-gradient(circle at 10% 20%, rgba(168, 85, 247, 0.15), transparent 30%),
              radial-gradient(circle at 90% 80%, rgba(59, 130, 246, 0.15), transparent 30%),
              #0a0a0f;
}

.auth-card {
  background: rgba(20, 20, 30, 0.7);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(168, 85, 247, 0.2);
  border-radius: 24px;
  padding: 2.5rem;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(168, 85, 247, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.auth-card:hover {
  box-shadow: 0 25px 50px rgba(168, 85, 247, 0.2);
}

.auth-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #fff, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.auth-subtitle {
  color: #a0a0b0;
  margin-bottom: 2rem;
  font-size: 1rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: #d0d0e0;
  font-weight: 500;
  font-size: 0.9rem;
  letter-spacing: 0.5px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper i {
  position: absolute;
  left: 15px;
  color: #6b6b8b;
  font-size: 1.1rem;
  transition: color 0.2s;
}

.input-wrapper input {
  width: 100%;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid #2a2a3a;
  border-radius: 40px;
  padding: 0.9rem 1rem 0.9rem 3rem;
  color: white;
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-wrapper input:focus {
  outline: none;
  border-color: #a855f7;
  box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.2);
}

.input-wrapper input:focus + i {
  color: #a855f7;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #a0a0b0;
  cursor: pointer;
}

.checkbox input {
  accent-color: #a855f7;
  width: 16px;
  height: 16px;
}

.terms-link {
  color: #a855f7;
  text-decoration: none;
}

.terms-link:hover {
  text-decoration: underline;
}

.auth-button {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border: none;
  border-radius: 40px;
  padding: 1rem;
  color: white;
  font-weight: 600;
  font-size: 1.1rem;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3);
  margin-top: 0.5rem;
}

.auth-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(168, 85, 247, 0.5);
}

.auth-footer {
  margin-top: 2rem;
  text-align: center;
  color: #a0a0b0;
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

.switch-link {
  color: #a855f7;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}

.switch-link:hover {
  color: #c084fc;
  text-decoration: underline;
}

@media (max-width: 480px) {
  .auth-page { padding: 1rem; }
  .auth-card { padding: 2rem; }
  .auth-title { font-size: 1.8rem; }
}
</style>