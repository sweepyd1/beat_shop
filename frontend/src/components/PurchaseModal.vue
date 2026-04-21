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
            <div class="price-block">
              <!-- Зачёркнутая базовая цена (стандартная) показывается только если выбрана не стандартная лицензия -->
              <span v-if="form.licenseType !== 'standard'" class="old-price">
                {{ formatPrice(basePrice) }} ₽
              </span>
              <span class="current-price">{{ formatPrice(currentPrice) }} ₽</span>
            </div>
            <p class="license-hint">{{ licenseHint }}</p>
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
              <option value="standard">Стандартная (для YouTube, SoundCloud) – {{ formatPrice(prices.standard) }} ₽</option>
              <option value="extended">Расширенная (для коммерческого использования, стриминг) – {{ formatPrice(prices.extended) }} ₽</option>
              <option value="exclusive">Эксклюзивная (полные права) – {{ formatPrice(prices.exclusive) }} ₽</option>
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

// Форматирование цены с разделителями тысяч
const formatPrice = (value) => {
  return Number(value).toLocaleString('ru-RU');
};

// URL обложки трека
const coverUrl = computed(() => {
  if (!props.track) return '';
  const url = props.track.cover_url;
  if (!url) return '/default-cover.jpg';
  if (url.startsWith('http')) return url;
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  return `${baseUrl}${url}`;
});

// Цены для разных лицензий на основе базовой цены трека и коэффициентов
const prices = computed(() => {
  const base = props.track?.price || 0;
  return {
    standard: base,
    extended: base * 2.0,    // коэффициент расширенной лицензии
    exclusive: base * 5.0    // коэффициент эксклюзивной лицензии
  };
});

// Базовая (стандартная) цена — всегда используется для зачёркивания
const basePrice = computed(() => prices.value.standard);

// Текущая цена в зависимости от выбранной лицензии
const currentPrice = computed(() => {
  return prices.value[form.value.licenseType] || prices.value.standard;
});

// Текст‑подсказка о выбранной лицензии
const licenseHint = computed(() => {
  const hints = {
    standard: 'Базовая стоимость (стандартная лицензия)',
    extended: 'Расширенная лицензия (+100% к базовой)',
    exclusive: 'Эксклюзивная лицензия (+400% к базовой)'
  };
  return hints[form.value.licenseType] || '';
});

// Закрытие модального окна
const close = () => {
  emit('update:modelValue', false);
};

// Отправка формы покупки
const submitPurchase = async () => {
  if (!form.value.agree) {
    alert('Необходимо согласиться с условиями договора');
    return;
  }
  loading.value = true;
  try {
    const payload = {
      track_id: props.track.id,
      buyer_name: form.value.name,
      buyer_email: form.value.email,
      license_type: form.value.licenseType,
      comment: form.value.comment
    };
    const response = await api.post('/purchase/purchases', payload);
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

// Показ условий лицензионного договора
const showTerms = () => {
  // Здесь можно открыть модальное окно с текстом или перейти на страницу
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

.price-block {
  margin-top: 0.25rem;
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.old-price {
  text-decoration: line-through;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.current-price {
  color: var(--accent);
  font-weight: 600;
  font-size: 1.2rem;
}

.license-hint {
  font-size: 0.75rem;
  color: var(--text-secondary);
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