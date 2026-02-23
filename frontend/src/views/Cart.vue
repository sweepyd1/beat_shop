<template>
  <div class="cart">
    <h1>Корзина</h1>

    <div v-if="cartItems.length === 0" class="empty-cart">
      <i class="fas fa-shopping-cart fa-3x"></i>
      <p>Корзина пуста</p>
      <router-link to="/search" class="btn-primary">Перейти к покупкам</router-link>
    </div>

    <div v-else class="cart-content">
      <div class="cart-items">
        <div v-for="item in cartItems" :key="item.id" class="cart-item">
          <img :src="item.cover" alt="" class="item-cover" />
          <div class="item-info">
            <h3>{{ item.title }}</h3>
            <p>{{ item.artist }}</p>
          </div>
          <span class="item-price">{{ item.price }} ₽</span>
          <button class="remove-btn" @click="removeFromCart(item.id)">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>

      <div class="cart-summary">
        <h2>Итого</h2>
        <div class="summary-row">
          <span>Товары ({{ cartItems.length }})</span>
          <span>{{ total }} ₽</span>
        </div>
        <div class="summary-row promo">
          <input type="text" v-model="promoCode" placeholder="Промокод" />
          <button @click="applyPromo">Применить</button>
        </div>
        <div v-if="discount > 0" class="summary-row discount">
          <span>Скидка</span>
          <span>-{{ discount }} ₽</span>
        </div>
        <div class="summary-row total">
          <span>К оплате</span>
          <span>{{ finalTotal }} ₽</span>
        </div>
        <router-link to="/checkout" class="btn-primary checkout-btn">Оформить заказ</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

// Мок-данные корзины (в реальном проекте берутся из store/pinia)
const cartItems = ref([
  { id: 1, title: 'Neon Dreams', artist: 'Arctica', cover: 'https://picsum.photos/200/200?random=1', price: 1.99 },
  { id: 2, title: 'Lost in Space', artist: 'Cosmic', cover: 'https://picsum.photos/200/200?random=2', price: 1.49 },
]);

const promoCode = ref('');
const discount = ref(0);

const total = computed(() => cartItems.value.reduce((sum, item) => sum + item.price, 0));
const finalTotal = computed(() => Math.max(total.value - discount.value, 0));

const removeFromCart = (id) => {
  cartItems.value = cartItems.value.filter(item => item.id !== id);
};

const applyPromo = () => {
  if (promoCode.value === 'BEAT10') {
    discount.value = total.value * 0.1;
  } else {
    alert('Неверный промокод');
  }
};
</script>

<style scoped>
.cart {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 2rem;
}

.empty-cart {
  text-align: center;
  padding: 4rem;
  background: rgba(255,255,255,0.02);
  border-radius: 30px;
}

.empty-cart i {
  color: #a0a0b0;
  margin-bottom: 1rem;
}

.empty-cart p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
}

.cart-content {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 2rem;
}

.cart-items {
  background: rgba(255,255,255,0.02);
  border-radius: 20px;
  padding: 1rem;
}

.cart-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.cart-item:last-child {
  border-bottom: none;
}

.item-cover {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
  margin-right: 1rem;
}

.item-info {
  flex: 1;
}

.item-info h3 {
  font-size: 1rem;
  margin-bottom: 0.2rem;
}

.item-info p {
  font-size: 0.85rem;
  color: #a0a0b0;
}

.item-price {
  font-weight: 600;
  color: #a855f7;
  margin-right: 1rem;
}

.remove-btn {
  background: none;
  border: none;
  color: #a0a0b0;
  font-size: 1.1rem;
  cursor: pointer;
  transition: color 0.2s;
}

.remove-btn:hover {
  color: #ff4d4d;
}

.cart-summary {
  background: rgba(255,255,255,0.02);
  border-radius: 20px;
  padding: 1.5rem;
  height: fit-content;
  border: 1px solid rgba(255,255,255,0.05);
}

.cart-summary h2 {
  margin-bottom: 1.5rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  color: #a0a0b0;
}

.summary-row.total {
  font-size: 1.2rem;
  font-weight: 600;
  color: white;
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: 1rem;
  margin-top: 1rem;
}

.promo {
  display: flex;
  gap: 0.5rem;
  margin: 1rem 0;
}

.promo input {
  flex: 1;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px;
  padding: 0.5rem 1rem;
  color: white;
}

.promo button {
  background: #a855f7;
  border: none;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
}

.discount {
  color: #4caf50;
}

.checkout-btn {
  display: block;
  text-align: center;
  margin-top: 1rem;
  text-decoration: none;
}
</style>