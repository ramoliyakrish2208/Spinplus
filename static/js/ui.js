/**
 * Spin & Win SaaS Platform - Bento UI Utilities (Toasts & Popup Modals)
 */

// Toast System
function showToast(message, type = 'info', duration = 3500) {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 10000;
      display: flex;
      flex-direction: column;
      gap: 10px;
      max-width: 380px;
      width: calc(100vw - 48px);
      pointer-events: none;
    `;
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  const bgColors = {
    success: 'linear-gradient(135deg, #10b981, #059669)',
    error: 'linear-gradient(135deg, #ef4444, #dc2626)',
    warning: 'linear-gradient(135deg, #f59e0b, #d97706)',
    info: 'linear-gradient(135deg, #6d28d9, #4c1d95)'
  };

  const icons = {
    success: '<i data-lucide="check-circle-2"></i>',
    error: '<i data-lucide="alert-circle"></i>',
    warning: '<i data-lucide="alert-triangle"></i>',
    info: '<i data-lucide="info"></i>'
  };

  toast.style.cssText = `
    background: ${bgColors[type] || bgColors.info};
    color: #ffffff;
    padding: 14px 20px;
    border-radius: 14px;
    font-family: inherit;
    font-size: 0.9rem;
    font-weight: 600;
    box-shadow: 0 12px 30px -5px rgba(0,0,0,0.4);
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    pointer-events: auto;
    display: flex;
    align-items: center;
    gap: 12px;
  `;

  toast.innerHTML = `<span style="display:flex;align-items:center;">${icons[type] || icons.info}</span> <div style="flex:1;">${message}</div>`;
  container.appendChild(toast);

  if (window.lucide) {
    lucide.createIcons();
  }

  requestAnimationFrame(() => {
    toast.style.opacity = '1';
    toast.style.transform = 'translateY(0)';
  });

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// Accessible Bento Popup Alert Modal System
function showAlertModal(title, message, type = 'info', onOk = null) {
  if (typeof title === 'string' && !message) {
    message = title;
    title = 'Notification';
  }

  let backdrop = document.getElementById('customAlertModalBackdrop');
  if (backdrop) backdrop.remove();

  backdrop = document.createElement('div');
  backdrop.id = 'customAlertModalBackdrop';
  backdrop.style.cssText = `
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.75);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    z-index: 10005;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
  `;

  const iconMarkup = {
    info: '<i data-lucide="info" style="width: 26px; height: 26px; color: var(--color-primary);"></i>',
    success: '<i data-lucide="check-circle-2" style="width: 26px; height: 26px; color: var(--color-success);"></i>',
    error: '<i data-lucide="alert-circle" style="width: 26px; height: 26px; color: var(--color-danger);"></i>',
    warning: '<i data-lucide="alert-triangle" style="width: 26px; height: 26px; color: var(--color-accent);"></i>'
  }[type] || '<i data-lucide="info" style="width: 26px; height: 26px; color: var(--color-primary);"></i>';

  backdrop.innerHTML = `
    <div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-xl); padding: 32px; width: 100%; max-width: 440px; text-align: center; box-shadow: var(--shadow-lg); animation: modalIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);">
      <div style="width: 52px; height: 52px; border-radius: 50%; background: var(--bg-elevated); border: 1px solid var(--border-subtle); display: flex; align-items: center; justify-content: center; margin: 0 auto 16px;">
        ${iconMarkup}
      </div>
      <h3 style="font-size: 1.3rem; font-weight: 800; color: var(--text-primary); margin-bottom: 8px;">${title}</h3>
      <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 24px; line-height: 1.6; white-space: pre-line;">${message}</p>
      <div style="display: flex; justify-content: center;">
        <button id="alertModalOkBtn" class="btn-primary" style="width: 100%; max-width: 200px;">OK</button>
      </div>
    </div>
  `;

  document.body.appendChild(backdrop);
  if (window.lucide) lucide.createIcons();

  const handleEsc = (e) => {
    if (e.key === 'Escape' || e.key === 'Enter') {
      backdrop.remove();
      document.removeEventListener('keydown', handleEsc);
      if (onOk) onOk();
    }
  };
  document.addEventListener('keydown', handleEsc);

  document.getElementById('alertModalOkBtn').onclick = () => {
    backdrop.remove();
    document.removeEventListener('keydown', handleEsc);
    if (onOk) onOk();
  };
}

// Accessible Confirmation Popup Modal System
function showConfirmModal(title, message, onConfirm, onCancel = null, confirmText = 'Confirm', confirmClass = 'btn-primary') {
  let backdrop = document.getElementById('customModalBackdrop');
  if (backdrop) backdrop.remove();

  backdrop = document.createElement('div');
  backdrop.id = 'customModalBackdrop';
  backdrop.style.cssText = `
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.75);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    z-index: 10000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
  `;

  backdrop.innerHTML = `
    <div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-xl); padding: 32px; width: 100%; max-width: 440px; text-align: center; box-shadow: var(--shadow-lg); animation: modalIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);">
      <div style="width: 52px; height: 52px; border-radius: 50%; background: rgba(109, 40, 217, 0.12); border: 1px solid rgba(109, 40, 217, 0.3); display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; color: var(--color-primary);">
        <i data-lucide="help-circle" style="width: 26px; height: 26px;"></i>
      </div>
      <h3 style="font-size: 1.3rem; font-weight: 800; color: var(--text-primary); margin-bottom: 8px;">${title}</h3>
      <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 24px; line-height: 1.6; white-space: pre-line;">${message}</p>
      <div style="display: flex; gap: 12px; justify-content: center;">
        <button id="modalCancelBtn" class="btn-secondary" style="flex: 1;">Cancel</button>
        <button id="modalConfirmBtn" class="${confirmClass}" style="flex: 1;">${confirmText}</button>
      </div>
    </div>
  `;

  document.body.appendChild(backdrop);
  if (window.lucide) lucide.createIcons();

  const handleEsc = (e) => {
    if (e.key === 'Escape') {
      backdrop.remove();
      document.removeEventListener('keydown', handleEsc);
      if (onCancel) onCancel();
    }
  };
  document.addEventListener('keydown', handleEsc);

  document.getElementById('modalCancelBtn').onclick = () => {
    backdrop.remove();
    document.removeEventListener('keydown', handleEsc);
    if (onCancel) onCancel();
  };
  document.getElementById('modalConfirmBtn').onclick = () => {
    backdrop.remove();
    document.removeEventListener('keydown', handleEsc);
    if (onConfirm) onConfirm();
  };
}

// Global Browser Alert Intercept (Replaces default browser alert dialogs with Bento Popup Modal)
window.alert = function(message) {
  showAlertModal('Notice', message, 'info');
};

// =========================================================
// 1-CLICK BUTTON DISABLE & MULTIPLE REQUEST PREVENTION SYSTEM
// =========================================================
(function initDoubleSubmitPrevention() {
  function attachProtection() {
    // 1. Intercept all Form Submissions across the entire SaaS platform
    document.addEventListener('submit', function(e) {
      const form = e.target;
      if (!form || form.tagName !== 'FORM') return;

      // If form has HTML5 constraint validation and fails, do not disable
      if (typeof form.checkValidity === 'function' && !form.checkValidity()) {
        return;
      }

      // Find all submit buttons associated with this form
      const submitButtons = form.querySelectorAll('button[type="submit"], input[type="submit"], .btn-submit-action');
      
      submitButtons.forEach(btn => {
        // Guard against duplicate submission triggers
        if (btn.dataset.isSubmitting === 'true' || btn.disabled) {
          e.preventDefault();
          e.stopImmediatePropagation();
          return;
        }

        btn.dataset.isSubmitting = 'true';
        btn.dataset.originalHtml = btn.innerHTML;
        
        // Preserve exact button dimensions to prevent layout shifts
        const rect = btn.getBoundingClientRect();
        if (rect.width > 0) {
          btn.style.width = `${Math.ceil(rect.width)}px`;
          btn.style.minWidth = `${Math.ceil(rect.width)}px`;
        }

        // Apply disabled state & visual feedback
        btn.disabled = true;
        btn.style.pointerEvents = 'none';
        btn.style.opacity = '0.72';
        btn.style.cursor = 'not-allowed';

        // Add sleek loading spinner
        if (btn.tagName === 'BUTTON') {
          const hasSpinner = btn.querySelector('.btn-submit-spinner');
          if (!hasSpinner) {
            btn.innerHTML = `<span style="display:inline-flex;align-items:center;justify-content:center;gap:8px;"><svg class="btn-submit-spinner" style="animation:spinBtnLoader 0.9s linear infinite;width:14px;height:14px;flex-shrink:0;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle><path d="M12 2a10 10 0 0 1 10 10" stroke-opacity="1"></path></svg> <span>Processing...</span></span>`;
          }
        }
      });

      // 8-second safety fallback (re-enables button if page is not redirected or file download occurs)
      setTimeout(() => {
        submitButtons.forEach(btn => {
          if (btn.dataset.isSubmitting === 'true') {
            btn.dataset.isSubmitting = 'false';
            btn.disabled = false;
            btn.style.pointerEvents = '';
            btn.style.opacity = '';
            btn.style.cursor = '';
            btn.style.width = '';
            btn.style.minWidth = '';
            if (btn.dataset.originalHtml) {
              btn.innerHTML = btn.dataset.originalHtml;
            }
          }
        });
      }, 8000);
    }, true);

    // 2. Intercept standalone 1-click action buttons (e.g. AJAX triggers, modal action confirms)
    document.addEventListener('click', function(e) {
      const btn = e.target.closest('button[data-single-click="true"], .btn-single-click, [data-prevent-double-click="true"]');
      if (!btn) return;

      if (btn.disabled || btn.dataset.isClicked === 'true') {
        e.preventDefault();
        e.stopImmediatePropagation();
        return false;
      }

      btn.dataset.isClicked = 'true';
      btn.disabled = true;
      btn.style.pointerEvents = 'none';
      btn.style.opacity = '0.65';
      btn.style.cursor = 'not-allowed';

      setTimeout(() => {
        btn.dataset.isClicked = 'false';
        btn.disabled = false;
        btn.style.pointerEvents = '';
        btn.style.opacity = '';
        btn.style.cursor = '';
      }, 3500);
    }, true);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', attachProtection);
  } else {
    attachProtection();
  }
})();
