
<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click.self="closeModal">
      <div class="modal-container">
        <div class="modal-header">
          <div class="ai-badge">
            <span class="ai-icon">🧠</span>
            <span>AI Рекомендации</span>
          </div>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>

        <div class="modal-body">
          <div v-if="!recommendation && !loading && !error" class="welcome">
            <div class="robot-emoji">🤖</div>
            <h3>Хотите открыть новую музыку?</h3>
            <p>
              Я проанализирую ваши предпочтения и подберу трек, который вам
              понравится.
            </p>
            <button class="get-recommendation-btn" @click="fetchRecommendation">
              ✨ Получить рекомендацию
            </button>
          </div>

          <div v-if="loading" class="loading">
            <div class="spinner"></div>
            <p>Анализируем ваши предпочтения...</p>
          </div>

          <div v-if="error" class="error">
            <p>😕 {{ error }}</p>
            <button class="retry-btn" @click="fetchRecommendation">
              Попробовать снова
            </button>
          </div>

          <div v-if="recommendation && !loading" class="recommendation-result">
            <div class="result-header">
              <span class="magic-icon">✨</span>
              <span>Вам может понравиться</span>
            </div>
            <div class="track-card">
              <img
                :src="recommendation.cover_url || '/default-cover.jpg'"
                class="track-cover"
                @error="handleImageError"
              />
              <div class="track-info">
                <h4>{{ recommendation.title }}</h4>
                <p class="artist">
                  {{
                    recommendation.author?.full_name ||
                    recommendation.author_name ||
                    "Неизвестный автор"
                  }}
                </p>
                <p class="genre">
                  {{ recommendation.genre?.name || recommendation.genre_name }}
                </p>
                <div class="price">
                  {{ formatPrice(recommendation.price) }} ₽
                </div>
              </div>
              <div class="track-actions">
                <button
                  class="play-btn"
                  @click="playTrack(recommendation)"
                  title="Слушать"
                >
                  🎧
                </button>
                <button
                  class="buy-btn"
                  @click="buyTrack(recommendation)"
                  title="Купить"
                >
                  🛒
                </button>
                <button
                  class="next-btn"
                  @click="fetchRecommendation"
                  title="Следующий трек"
                >
                  ⏩
                </button>
              </div>
            </div>
            <div class="explanation">
              <p class="explanation-text">{{ explanationText }}</p>
            </div>
            <div class="action-buttons">
              <button class="another-btn" @click="fetchRecommendation">
                🎲 Другой трек
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from "vue";
import api from "@/api";
import { useAuthStore } from "@/stores/auth";
import { storeToRefs } from "pinia";

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["close"]);

const closeModal = () => {
  emit("close");
  
  setTimeout(() => {
    if (!props.visible) {
      recommendation.value = null;
      error.value = null;
      shownTrackIds.value = [];
    }
  }, 200);
};

const formatPrice = (price) => price?.toFixed(2) || "0.00";
const handleImageError = (e) => {
  e.target.src = "/default-cover.jpg";
};

const recommendation = ref(null);
const loading = ref(false);
const error = ref(null);
const explanationText = ref("");
const shownTrackIds = ref([]);

const authStore = useAuthStore();
const { user } = storeToRefs(authStore);

const playTrack = (track) => {
  if (!track?.id) return;
  const audioUrl = `/api/recommendations/stream/${track.id}`;
  const audio = new Audio(audioUrl);
  audio.play().catch((err) => {
    console.error("Playback error:", err);
    showError("Не удалось воспроизвести трек.");
  });
};

const buyTrack = (track) => {
  showSuccess(`Добавлено в корзину: ${track.title}`);
  
};

const fetchRecommendation = async () => {
  loading.value = true;
  error.value = null;
  recommendation.value = null;
  explanationText.value = "";

  try {
    let url = "/recommendations/personal?limit=1";
    if (shownTrackIds.value.length) {
      url += `&exclude=${shownTrackIds.value.join(",")}`;
    }
    const response = await api.get(url);
    const track = response.data[0];
    if (!track) throw new Error("Нет подходящих треков");

    recommendation.value = track;
    shownTrackIds.value.push(track.id);

    if (user.value) {
      explanationText.value =
        "Я проанализировал(а) ваши любимые жанры и треки. Этот трек идеально подходит под ваш вкус. Попробуйте!";
    } else {
      explanationText.value =
        "Этот трек сейчас популярен среди других слушателей. Надеюсь, вам понравится!";
    }
  } catch (err) {
    console.error("Recommendation error:", err);
    error.value = "Не удалось получить рекомендацию. Попробуйте позже.";
    if (process.env.NODE_ENV === "development") {
      recommendation.value = {
        id: 999,
        title: "Пример трека (демо)",
        author: { full_name: "Demo Artist" },
        genre: { name: "Electronic" },
        price: 99.0,
        cover_url: "/default-cover.jpg",
      };
      explanationText.value =
        "Демонстрационная рекомендация. Подключите бэкенд для реальных треков.";
      error.value = null;
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn 0.2s;
}
.modal-container {
  background: rgba(20, 20, 30, 0.95);
  border-radius: 2rem;
  width: 90%;
  max-width: 550px;
  border: 1px solid rgba(168, 85, 247, 0.3);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
  animation: slideUp 0.3s;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem 1.5rem;
  border-bottom: 1px solid rgba(168, 85, 247, 0.2);
}
.ai-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #a855f7, #3b82f6);
  padding: 0.3rem 1rem;
  border-radius: 40px;
  font-weight: 600;
}
.close-btn {
  background: none;
  border: none;
  color: #a0a0b0;
  font-size: 1.5rem;
  cursor: pointer;
}
.modal-body {
  padding: 1.8rem 1.5rem;
  min-height: 380px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.welcome {
  text-align: center;
}
.robot-emoji {
  font-size: 4rem;
  margin-bottom: 1rem;
}
.get-recommendation-btn {
  background: linear-gradient(45deg, #a855f7, #3b82f6);
  border: none;
  padding: 0.8rem 2rem;
  border-radius: 40px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
}
.loading {
  text-align: center;
}
.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(168, 85, 247, 0.2);
  border-top: 4px solid #a855f7;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem;
}
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
.recommendation-result {
  width: 100%;
}
.track-card {
  background: rgba(30, 30, 40, 0.6);
  border-radius: 1.5rem;
  padding: 1rem;
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
}
.track-cover {
  width: 80px;
  height: 80px;
  border-radius: 1rem;
  object-fit: cover;
}
.track-info {
  flex: 1;
}
.track-info h4 {
  margin: 0 0 0.3rem;
}
.artist,
.genre {
  font-size: 0.85rem;
  color: #a0a0b0;
}
.price {
  font-weight: bold;
  color: #a855f7;
}
.track-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.play-btn,
.buy-btn,
.next-btn {
  background: rgba(168, 85, 247, 0.2);
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.explanation {
  background: rgba(168, 85, 247, 0.1);
  border-radius: 1rem;
  padding: 0.8rem;
  margin: 1rem 0;
  text-align: center;
}
.another-btn {
  width: 100%;
  background: transparent;
  border: 1px solid #a855f7;
  padding: 0.6rem;
  border-radius: 40px;
  color: white;
  cursor: pointer;
}
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>
