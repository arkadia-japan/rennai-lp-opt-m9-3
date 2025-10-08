document.addEventListener('DOMContentLoaded', () => {
  const hoursEl = document.getElementById('countdown-hours');
  const minutesEl = document.getElementById('countdown-minutes');
  const secondsEl = document.getElementById('countdown-seconds');

  if (hoursEl && minutesEl && secondsEl) {
    const storageKey = 'rennaiCountdownDeadlineV2';
    const fallbackDurationHours = 12;
    const now = Date.now();
    let deadline = now + fallbackDurationHours * 60 * 60 * 1000;

    try {
      const stored = window.localStorage.getItem(storageKey);
      if (stored) {
        const parsed = parseInt(stored, 10);
        if (!Number.isNaN(parsed) && parsed > now) {
          deadline = parsed;
        }
      } else {
        window.localStorage.setItem(storageKey, String(deadline));
      }
    } catch (error) {
      // localStorage unavailable; proceed with fallback deadline
    }

    const updateCountdown = () => {
      const diff = deadline - Date.now();
      if (diff <= 0) {
        hoursEl.textContent = '00';
        minutesEl.textContent = '00';
        secondsEl.textContent = '00';
        return;
      }

      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      hoursEl.textContent = String(hours).padStart(2, '0');
      minutesEl.textContent = String(minutes).padStart(2, '0');
      secondsEl.textContent = String(seconds).padStart(2, '0');
    };

    updateCountdown();
    setInterval(updateCountdown, 1000);
  }

  const modal = document.getElementById('form-modal');
  const openButtons = document.querySelectorAll('.js-open-form');

  if (modal && openButtons.length) {
    const body = document.body;
    const focusableSelector = 'a[href], button:not([disabled]), textarea, input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])';
    const closeTriggers = modal.querySelectorAll('[data-modal-close]');
    let previouslyFocusedElement = null;

    const setRefererFields = () => {
      const referer = document.referrer || '';
      const currentUrl = window.location.href;
      const refererFields = modal.querySelectorAll('.UserRefererUrl');
      const formUrlFields = modal.querySelectorAll('.UserRefererFormUrl');

      refererFields.forEach((field) => {
        field.value = referer;
      });

      formUrlFields.forEach((field) => {
        field.value = currentUrl;
      });
    };

    const getFocusableElements = () => {
      return Array.from(modal.querySelectorAll(focusableSelector)).filter(
        (el) => el.offsetParent !== null || modal === el
      );
    };

    const trapFocus = (event) => {
      if (event.key !== 'Tab') {
        return;
      }

      const focusableElements = getFocusableElements();

      if (!focusableElements.length) {
        event.preventDefault();
        return;
      }

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      if (event.shiftKey && document.activeElement === firstElement) {
        event.preventDefault();
        lastElement.focus();
      } else if (!event.shiftKey && document.activeElement === lastElement) {
        event.preventDefault();
        firstElement.focus();
      }
    };

    const closeModal = () => {
      modal.classList.remove('is-open');
      modal.setAttribute('aria-hidden', 'true');
      body.classList.remove('modal-open');
      document.removeEventListener('keydown', handleKeydown);

      if (previouslyFocusedElement && typeof previouslyFocusedElement.focus === 'function') {
        previouslyFocusedElement.focus();
      }
    };

    const focusFirstField = () => {
      const firstField = modal.querySelector('input, select, textarea, button');
      if (firstField) {
        firstField.focus();
      }
    };

    const openModal = (event) => {
      event.preventDefault();
      previouslyFocusedElement = document.activeElement;
      modal.classList.add('is-open');
      modal.setAttribute('aria-hidden', 'false');
      body.classList.add('modal-open');
      setRefererFields();
      focusFirstField();
      document.addEventListener('keydown', handleKeydown);
    };

    const handleKeydown = (event) => {
      if (event.key === 'Escape') {
        closeModal();
        return;
      }

      trapFocus(event);
    };

    openButtons.forEach((button) => {
      button.addEventListener('click', openModal);
    });

    closeTriggers.forEach((trigger) => {
      trigger.addEventListener('click', (event) => {
        event.preventDefault();
        closeModal();
      });
    });
  }
});
