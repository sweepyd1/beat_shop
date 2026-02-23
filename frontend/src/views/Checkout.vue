<template>
  <div class="checkout">
    <h1>Оформление заказа</h1>

    <div class="checkout-content">
      <div class="order-form">
        <h2>Контактные данные</h2>
        <form @submit.prevent="submitOrder">
          <div class="form-group">
            <label>Имя</label>
            <input type="text" v-model="form.name" required />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="email" v-model="form.email" required />
          </div>
          <div class="form-group">
            <label>Телефон</label>
            <input type="tel" v-model="form.phone" />
          </div>

          <h2>Способ оплаты</h2>
          <div class="payment-methods">
            <label class="payment-option">
              <input type="radio" value="card" v-model="form.payment" />
              <span>Банковская карта</span>
            </label>
            <label class="payment-option">
              <input type="radio" value="paypal" v-model="form.payment" />
              <span>PayPal</span>
            </label>
          </div>

          <h2>Ваш заказ</h2>
          <div class="order-items">
            <div v-for="item in cartItems" :key="item.id" class="order-item">
              <span>{{ item.title }} – {{ item.artist }}</span>
              <span>{{ item.price }} ₽</span>
            </div>
          </div>
          <div class="order-total">
            <strong>Итого: {{ total }} ₽</strong>
          </div>

          <button type="submit" class="btn-primary">Подтвердить заказ</button>
        </form>
      </div>

      <div class="order-summary">
        <h3>Детали заказа</h3>
        <p>После оплаты вы сможете скачать треки в личном кабинете.</p>
        <p>На указанный email придёт чек и ссылки на скачивание.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const cartItems = ref([
  { id: 1, title: 'Neon Dreams', artist: 'Arctica', price: 1.99 },
  { id: 2, title: 'Lost in Space', artist: 'Cosmic', price: 1.49 },
]);

const total = computed(() => cartItems.value.reduce((sum, item) => sum + item.price, 0));

const form = ref({
  name: '',
  email: '',
  phone: '',
  payment: 'card',
});

const submitOrder = () => {
  console.log('Order submitted', form.value);
  alert('Заказ оформлен! (имитация)');
  // здесь будет отправка на бэкенд и перенаправление на страницу успеха
};
</script>

<style scoped>
.checkout {
  max-width: 1000px;
  margin: 2rem auto;
  padding: 0 2rem;
}

.checkout-content {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 2rem;
  margin-top: 2rem;
}

.order-form {
  background: rgba(255,255,255,0.02);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255,255,255,0.05);
}

.order-form h2 {
  font-size: 1.2rem;
  margin: 1.5rem 0 1rem;
}

.order-form h2:first-of-type {
  margin-top: 0;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.3rem;
  color: #a0a0b0;
  font-size: 0.9rem;
}

.form-group input {
  width: 100%;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  padding: 0.8rem 1rem;
  color: white;
  font-size: 1rem;
}

.payment-methods {
  display: flex;
  gap: 2rem;
  margin: 1rem 0;
}

.payment-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.order-items {
  background: rgba(0,0,0,0.2);
  border-radius: 10px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.order-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px dashed rgba(255,255,255,0.05);
}

.order-item:last-child {
  border-bottom: none;
}

.order-total {
  font-size: 1.2rem;
  text-align: right;
  margin: 1rem 0;
}

.order-summary {
  background: rgba(168,85,247,0.1);
  border-radius: 20px;
  padding: 1.5rem;
  height: fit-content;
  border: 1px solid rgba(168,85,247,0.2);
}

.order-summary h3 {
  color: #a855f7;
  margin-bottom: 1rem;
}

.order-summary p {
  color: #a0a0b0;
  line-height: 1.5;
}
</style>