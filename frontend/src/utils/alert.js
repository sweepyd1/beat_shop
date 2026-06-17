import Swal from 'sweetalert2';


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

    
    if (data.detail) {
      if (typeof data.detail === 'string') {
        message = data.detail;
      } else if (Array.isArray(data.detail)) {
        
        message = data.detail
          .map(err => {
            
            const field = err.loc?.slice(1).join('.') || ''; 
            return field ? `${field}: ${err.msg}` : err.msg;
          })
          .join('; ');
      } else {
        
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