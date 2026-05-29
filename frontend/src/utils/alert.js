import Swal from 'sweetalert2';

// Базовая настройка SweetAlert2 (единоразово)
const Toast = Swal.mixin({
  toast: true,
  position: 'top-end',
  showConfirmButton: false,
  timer: 3000,
  timerProgressBar: true,
  background: '#1e1e2e',
  color: '#ffffff',
  customClass: {
    popup: 'swal2-popup-custom'
  }
});

/**
 * Показать сообщение об ошибке
 * @param {string|Error} error - текст ошибки или объект ошибки (Axios, JS)
 */
export function showError(error) {
  let message = 'Произошла неизвестная ошибка';

  if (typeof error === 'string') {
    message = error;
  } else if (error.response) {
    const data = error.response.data;

    // FastAPI: ошибка может быть {"detail": "строка"} или {"detail": [...]}
    if (data.detail) {
      if (typeof data.detail === 'string') {
        message = data.detail;
      } else if (Array.isArray(data.detail)) {
        // Массив объектов ошибок валидации: [{msg: "...", loc: [...]}, ...]
        message = data.detail
          .map(err => {
            // Формируем читаемое сообщение: поле (если есть) + текст ошибки
            const field = err.loc?.slice(1).join('.') || ''; // убираем "body"
            return field ? `${field}: ${err.msg}` : err.msg;
          })
          .join('; ');
      } else {
        // На всякий случай – любой другой объект
        message = JSON.stringify(data.detail);
      }
    } else if (data.message) {
      message = data.message;
    } else {
      message = JSON.stringify(data);
    }
  } else if (error.message) {
    message = error.message;
  }

  Swal.fire({
    icon: 'error',
    title: 'Ошибка',
    text: message,
    background: '#1e1e2e',
    color: '#ffffff',
    confirmButtonColor: '#a855f7',
    customClass: {
      popup: 'swal2-popup-custom'
    }
  });
}


export function showSuccess(message) {
  Toast.fire({
    icon: 'success',
    title: message
  });
}

/**
 * Показать предупреждение
 */
export function showWarning(message) {
  Toast.fire({
    icon: 'warning',
    title: message
  });
}