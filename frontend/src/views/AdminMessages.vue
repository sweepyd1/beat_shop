<template>
  <div class="admin-messages-page">
    <div class="page-header">
      <h1>📬 Сообщения от пользователей</h1>
      <p>Управление сообщениями с сайта</p>
    </div>

    <!-- Фильтры -->
    <div class="filters">
      <button 
        :class="['filter-btn', { active: filter === 'all' }]"
        @click="filter = 'all'"
      >
        Все ({{ messages.length }})
      </button>
      <button 
        :class="['filter-btn', { active: filter === 'unread' }]"
        @click="filter = 'unread'"
      >
        Непрочитанные ({{ unreadCount }})
      </button>
      <button 
        :class="['filter-btn', { active: filter === 'read' }]"
        @click="filter = 'read'"
      >
        Прочитанные
      </button>
    </div>

    <!-- Список сообщений -->
    <div class="messages-list">
      <div v-if="loading" class="loading">
        <i class="fas fa-spinner fa-spin"></i>
        <span>Загрузка...</span>
      </div>
      
      <div v-else-if="filteredMessages.length === 0" class="empty-state">
        <i class="fas fa-inbox"></i>
        <p>Нет сообщений</p>
      </div>

      <div 
        v-for="msg in filteredMessages" 
        :key="msg.id" 
        :class="['message-card', { unread: !msg.is_read }]"
        @click="selectMessage(msg)"
      >
        <div class="message-header">
          <div class="sender-info">
            <span class="sender-name">{{ msg.name }}</span>
            <span class="sender-email">{{ msg.email }}</span>
          </div>
          <span class="message-date">{{ formatDate(msg.created_at) }}</span>
        </div>
        <div class="message-preview">{{ msg.message }}</div>
        <div class="message-actions">
          <button 
            v-if="!msg.is_read" 
            class="btn-mark-read"
            @click.stop="markAsRead(msg.id)"
          >
            <i class="fas fa-check"></i> Отметить как прочитанное
          </button>
          <button class="btn-delete" @click.stop="deleteMessage(msg.id)">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Модальное окно просмотра -->
    <teleport to="body">
      <div v-if="selectedMessage" class="modal-overlay" @click.self="selectedMessage = null">
        <div class="modal-content message-modal">
          <div class="modal-header">
            <h2>Сообщение от {{ selectedMessage.name }}</h2>
            <button @click="selectedMessage = null" class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
            <div class="message-details">
              <p><strong>Email:</strong> {{ selectedMessage.email }}</p>
              <p><strong>Дата:</strong> {{ formatFullDate(selectedMessage.created_at) }}</p>
              <p><strong>Статус:</strong> 
                <span :class="['status-badge', selectedMessage.is_read ? 'read' : 'unread']">
                  {{ selectedMessage.is_read ? 'Прочитано' : 'Не прочитано' }}
                </span>
              </p>
            </div>
            <div class="message-full-text">
              <p>{{ selectedMessage.message }}</p>
            </div>
          </div>
          <div class="modal-footer">
            <button v-if="!selectedMessage.is_read" @click="markAsRead(selectedMessage.id); selectedMessage = null" class="btn-primary">
              <i class="fas fa-check"></i> Отметить как прочитанное
            </button>
            <button @click="deleteMessage(selectedMessage.id); selectedMessage = null" class="btn-danger">
              <i class="fas fa-trash"></i> Удалить
            </button>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '@/api';
import { showSuccess, showError } from '@/utils/alert';

const messages = ref([]);
const loading = ref(true);
const filter = ref('all');
const selectedMessage = ref(null);

const unreadCount = computed(() => messages.value.filter(m => !m.is_read).length);

const filteredMessages = computed(() => {
  if (filter.value === 'unread') return messages.value.filter(m => !m.is_read);
  if (filter.value === 'read') return messages.value.filter(m => m.is_read);
  return messages.value;
});

const fetchMessages = async () => {
  try {
    const { data } = await api.get('/contacts/admin/', {
      params: { limit: 100 }
    });
    messages.value = data;
  } catch (error) {
    console.error('Ошибка загрузки сообщений:', error);
    showError('Не удалось загрузить сообщения');
  } finally {
    loading.value = false;
  }
};

const markAsRead = async (id) => {
  try {
    await api.patch(`/contacts/admin/${id}/read`);
    const msg = messages.value.find(m => m.id === id);
    if (msg) msg.is_read = true;
    showSuccess('Сообщение отмечено как прочитанное');
  } catch (error) {
    showError('Ошибка при обновлении статуса');
  }
};

const deleteMessage = async (id) => {
  if (!confirm('Вы уверены, что хотите удалить это сообщение?')) return;
  try {
    await api.delete(`/contacts/admin/${id}`);
    messages.value = messages.value.filter(m => m.id !== id);
    if (selectedMessage.value?.id === id) selectedMessage.value = null;
    showSuccess('Сообщение удалено');
  } catch (error) {
    console.error(error);
    showError('Ошибка при удалении');
  }
};

const selectMessage = (msg) => {
  selectedMessage.value = msg;
  if (!msg.is_read) {
    markAsRead(msg.id);
  }
};

const formatDate = (dateStr) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
};

const formatFullDate = (dateStr) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' });
};

onMounted(fetchMessages);
</script>

<style scoped>
.admin-messages-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  background: linear-gradient(135deg, #a855f7, #ec4899);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}

.page-header p {
  color: #9ca3af;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.filter-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(168, 85, 247, 0.3);
  color: #9ca3af;
  cursor: pointer;
  transition: all 0.3s;
}

.filter-btn:hover {
  background: rgba(168, 85, 247, 0.2);
}

.filter-btn.active {
  background: linear-gradient(135deg, #a855f7, #ec4899);
  color: white;
  border-color: transparent;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #9ca3af;
}

.loading i {
  font-size: 2rem;
  margin-right: 1rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #9ca3af;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.message-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(168, 85, 247, 0.2);
  border-radius: 1rem;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s;
}

.message-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(168, 85, 247, 0.4);
}

.message-card.unread {
  border-left: 3px solid #a855f7;
  background: rgba(168, 85, 247, 0.1);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.sender-info {
  display: flex;
  flex-direction: column;
}

.sender-name {
  font-weight: 600;
  color: white;
}

.sender-email {
  font-size: 0.85rem;
  color: #9ca3af;
}

.message-date {
  font-size: 0.85rem;
  color: #6b7280;
}

.message-preview {
  color: #d1d5db;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.message-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-mark-read {
  padding: 0.5rem 1rem;
  background: rgba(16, 185, 129, 0.2);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #34d399;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.3s;
}

.btn-mark-read:hover {
  background: rgba(16, 185, 129, 0.3);
}

.btn-delete {
  padding: 0.5rem 1rem;
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #f87171;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-delete:hover {
  background: rgba(239, 68, 68, 0.3);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #1a1a2e;
  border-radius: 1rem;
  padding: 2rem;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-header h2 {
  color: white;
  font-size: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 2rem;
  cursor: pointer;
}

.message-details {
  background: rgba(255, 255, 255, 0.03);
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.message-details p {
  margin: 0.5rem 0;
  color: #d1d5db;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.85rem;
}

.status-badge.read {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
}

.status-badge.unread {
  background: rgba(168, 85, 247, 0.2);
  color: #c084fc;
}

.message-full-text {
  background: rgba(255, 255, 255, 0.03);
  padding: 1rem;
  border-radius: 0.5rem;
  color: #d1d5db;
  line-height: 1.6;
}

.modal-footer {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
  justify-content: flex-end;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #a855f7, #ec4899);
  border: none;
  border-radius: 0.5rem;
  color: white;
  cursor: pointer;
  font-weight: 600;
}

.btn-danger {
  padding: 0.75rem 1.5rem;
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 0.5rem;
  color: #f87171;
  cursor: pointer;
}
</style>
