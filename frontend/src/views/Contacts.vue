<template>
  <div class="contacts">
    <h1>Контакты</h1>

    <div class="contacts-grid">
      <div class="contact-info">
        <h2>Свяжитесь с нами</h2>
        <p><i class="fas fa-envelope"></i> support@beatmarket.com</p>
        <p><i class="fas fa-phone"></i> +7 (999) 123-45-67</p>
        <p><i class="fas fa-map-marker-alt"></i> Нижний Новгород, ул. Тверская, д. 7</p>

        <div class="social">
          <a href="#"><i class="fab fa-vk"></i></a>

        </div>
      </div>

      <div class="contact-form">
        <h2>Напишите нам</h2>
        <form @submit.prevent="sendMessage">
          <div class="form-group">
            <label>Имя</label>
            <input type="text" v-model="form.name" required />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="email" v-model="form.email" required />
          </div>
          <div class="form-group">
            <label>Сообщение</label>
            <textarea v-model="form.message" rows="5" required></textarea>
          </div>
          <button type="submit" class="btn-primary">Отправить</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '@/api'; 

import { showError, showSuccess } from '@/utils/alert';  
const form = ref({ name: '', email: '', message: '' });
const isLoading = ref(false);

const sendMessage = async () => {
  isLoading.value = true;
  try {
    const response = await api.post('/contacts/', form.value);
    if (response.status === 201) {
      showSuccess('Сообщение отправлено!');
      form.value = { name: '', email: '', message: '' };
    } else {
      showError('Ошибка при отправке');
    }
  } catch (error) {
    console.error('Ошибка:', error);
    showError('Не удалось отправить сообщение. Проверьте соединение с сервером.');
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.contacts {
  max-width: 1000px;
  margin: 2rem auto;
  padding: 0 2rem;
}

.contacts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-top: 2rem;
}
.btn-primary {
  background: #a855f7;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 0.8rem 1.5rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-primary:hover {
  background: #9333ea;
}
.contact-info, .contact-form {
  background: rgba(255,255,255,0.02);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255,255,255,0.05);
}

.contact-info h2, .contact-form h2 {
  margin-bottom: 1.5rem;
}

.contact-info p {
  margin-bottom: 1rem;
  color: #a0a0a0;
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.contact-info i {
  width: 20px;
  color: #a855f7;
}

.social {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.social a {
  color: #a0a0a0;
  font-size: 1.8rem;
  transition: color 0.2s;
}

.social a:hover {
  color: #a855f7;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.3rem;
  color: #a0a0b0;
}

.form-group input,
.form-group textarea {
  width: 100%;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  padding: 0.8rem 1rem;
  color: white;
  font-family: inherit;
}
</style>