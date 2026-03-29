<!-- components/PurchaseModal.vue -->
<template>
  <div v-if="modelValue" class="modal-overlay" @click.self="close">
    <div class="modal-container">
      <div class="modal-header">
        <h2>Оформление покупки</h2>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      <div class="modal-body">
        <div class="track-summary">
          <img :src="coverUrl" alt="cover" class="mini-cover" />
          <div>
            <p class="track-title">{{ track.title }}</p>
            <p class="track-author">{{ track.author?.name || 'Автор' }}</p>
            <p class="track-price">{{ track.price }} ₽</p>
          </div>
        </div>

        <form @submit.prevent="submitPurchase">
          <div class="form-group">
            <label>Ваше имя *</label>
            <input type="text" v-model="form.name" required placeholder="Иван Иванов" />
          </div>
          <div class="form-group">
            <label>Email *</label>
            <input type="email" v-model="form.email" required placeholder="ivan@example.com" />
          </div>
          <div class="form-group">
            <label>Тип лицензии *</label>
            <select v-model="form.licenseType" required>
              <option value="standard">Стандартная (для YouTube, SoundCloud)</option>
              <option value="extended">Расширенная (для коммерческого использования, стриминг)</option>
              <option value="exclusive">Эксклюзивная (полные права)</option>
            </select>
          </div>
          <div class="form-group">
            <label>Комментарий (необязательно)</label>
            <textarea v-model="form.comment" rows="3" placeholder="Ваши пожелания или дополнительная информация"></textarea>
          </div>
          <div class="form-group checkbox">
            <input type="checkbox" v-model="form.agree" required />
            <label>Я согласен с условиями <a href="#" @click.prevent="showTerms">лицензионного договора</a></label>
          </div>

          <button type="submit" class="submit-btn" :disabled="loading">
            <i v-if="loading" class="fas fa-spinner fa-spin"></i>
            <span v-else>Оплатить и получить договор</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import api from '../api';

const props = defineProps({
  modelValue: Boolean,
  track: Object
});
const emit = defineEmits(['update:modelValue', 'purchase-complete']);

const form = ref({
  name: '',
  email: '',
  licenseType: 'standard',
  comment: '',
  agree: false
});
const loading = ref(false);

const coverUrl = computed(() => {
  if (!props.track) return '';
  const url = props.track.cover_url;
  if (!url) return '/default-cover.jpg';
  if (url.startsWith('http')) return url;
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  return `${baseUrl}${url}`;
});

const close = () => {
  emit('update:modelValue', false);
};

const submitPurchase = async () => {
  if (!form.value.agree) {
    alert('Необходимо согласиться с условиями договора');
    return;
  }
  loading.value = true;
  try {
    // Здесь должен быть реальный запрос к API для создания покупки и генерации договора
    const payload = {
      track_id: props.track.id,
      buyer_name: form.value.name,
      buyer_email: form.value.email,
      license_type: form.value.licenseType,
      comment: form.value.comment
    };
    const response = await api.post('/purchases', payload);
    // После успешной покупки можно получить ссылку на договор (PDF)
    emit('purchase-complete', {
      ...response.data,
      email: form.value.email
    });
    close();
  } catch (error) {
    console.error('Ошибка при покупке:', error);
    alert('Произошла ошибка при оформлении покупки. Попробуйте позже.');
  } finally {
    loading.value = false;
  }
};

const showTerms = () => {
  // Открыть модальное окно с текстом договора или ссылку на отдельную страницу
  alert('Здесь будет текст лицензионного договора');
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: var(--bg-secondary);
  border-radius: 32px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
  border: 1px solid var(--border-color);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h2 {
  font-size: 1.5rem;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.8rem;
  cursor: pointer;
  color: var(--text-secondary);
  transition: color 0.2s;
}

.close-btn:hover {
  color: var(--text-primary);
}

.modal-body {
  padding: 1.5rem;
}

.track-summary {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.mini-cover {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  object-fit: cover;
}

.track-title {
  font-weight: 600;
  margin-bottom: 0.2rem;
}

.track-author {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.track-price {
  color: var(--accent);
  font-weight: 600;
  margin-top: 0.2rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.3rem;
  font-size: 0.9rem;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.6rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--accent);
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox input {
  width: auto;
  margin-right: 0.5rem;
}

.submit-btn {
  width: 100%;
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border: none;
  padding: 0.8rem;
  border-radius: 40px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  margin-top: 1rem;
  transition: opacity 0.2s;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>