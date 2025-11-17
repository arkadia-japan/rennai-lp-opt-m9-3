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

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const pointerFine = window.matchMedia('(pointer: fine)');
  const tiltElements = Array.prototype.slice.call(document.querySelectorAll('[data-tilt]'));
  const revealElements = Array.prototype.slice.call(document.querySelectorAll('[data-reveal]'));
  const tiltCleanups = new Map();
  let revealObserver = null;

  const attachMediaListener = (mediaQuery, handler) => {
    if (typeof mediaQuery.addEventListener === 'function') {
      mediaQuery.addEventListener('change', handler);
    } else if (typeof mediaQuery.addListener === 'function') {
      mediaQuery.addListener(handler);
    }
  };

  const resetTiltStyles = (element) => {
    element.style.setProperty('--tilt-rotate-x', '0deg');
    element.style.setProperty('--tilt-rotate-y', '0deg');
    element.style.setProperty('--tilt-translate-z', '0px');
    element.removeAttribute('data-tilt-active');
  };

  const enableTilt = () => {
    if (!tiltElements.length || !pointerFine.matches || prefersReducedMotion.matches) {
      return;
    }

    tiltElements.forEach((element) => {
      if (tiltCleanups.has(element)) {
        return;
      }

      const maxTilt = Number(element.dataset.tiltMax) || 12;
      const depth = Number(element.dataset.tiltDepth) || 22;
      let rafId = null;

      const onPointerMove = (event) => {
        if (event.pointerType && event.pointerType !== 'mouse' && event.pointerType !== 'pen') {
          return;
        }

        const rect = element.getBoundingClientRect();
        const pointerX = event.clientX;
        const pointerY = event.clientY;

        if (pointerX == null || pointerY == null) {
          return;
        }

        const xRatio = Math.min(Math.max((pointerX - rect.left) / rect.width, 0), 1);
        const yRatio = Math.min(Math.max((pointerY - rect.top) / rect.height, 0), 1);

        if (rafId) {
          cancelAnimationFrame(rafId);
        }

        rafId = requestAnimationFrame(() => {
          const tiltX = (0.5 - yRatio) * maxTilt;
          const tiltY = (xRatio - 0.5) * maxTilt;

          element.style.setProperty('--tilt-rotate-x', `${tiltX.toFixed(2)}deg`);
          element.style.setProperty('--tilt-rotate-y', `${tiltY.toFixed(2)}deg`);
          element.style.setProperty('--tilt-translate-z', `${depth}px`);
          element.setAttribute('data-tilt-active', 'true');
          rafId = null;
        });
      };

      const onPointerLeave = () => {
        if (rafId) {
          cancelAnimationFrame(rafId);
          rafId = null;
        }
        resetTiltStyles(element);
      };

      element.addEventListener('pointermove', onPointerMove);
      element.addEventListener('pointerleave', onPointerLeave);
      element.addEventListener('pointercancel', onPointerLeave);

      tiltCleanups.set(element, () => {
        element.removeEventListener('pointermove', onPointerMove);
        element.removeEventListener('pointerleave', onPointerLeave);
        element.removeEventListener('pointercancel', onPointerLeave);
        resetTiltStyles(element);
      });
    });
  };

  const disableTilt = () => {
    tiltCleanups.forEach((cleanup) => {
      cleanup();
    });
    tiltCleanups.clear();
  };

  const showAllRevealElements = () => {
    revealElements.forEach((element) => {
      element.classList.add('is-revealed');
      element.style.removeProperty('--reveal-delay');
    });
  };

  const enableReveal = () => {
    if (!revealElements.length || prefersReducedMotion.matches) {
      showAllRevealElements();
      return;
    }

    if (!('IntersectionObserver' in window)) {
      showAllRevealElements();
      return;
    }

    if (revealObserver) {
      revealObserver.disconnect();
    }

    revealObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-revealed');
          entry.target.style.removeProperty('--reveal-delay');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.18, rootMargin: '0px 0px -12%' });

    revealElements.forEach((element, index) => {
      if (element.classList.contains('is-revealed')) {
        return;
      }

      const customDelay = Number(element.dataset.revealDelay);
      const delay = Number.isFinite(customDelay) ? customDelay : Math.min(index * 90, 420);
      element.style.setProperty('--reveal-delay', `${delay}ms`);
      revealObserver.observe(element);
    });
  };

  const disableReveal = () => {
    if (revealObserver) {
      revealObserver.disconnect();
      revealObserver = null;
    }
    revealElements.forEach((element) => {
      element.style.removeProperty('--reveal-delay');
    });
  };

  const applyMotionPreferences = () => {
    disableTilt();

    if (prefersReducedMotion.matches) {
      disableReveal();
      showAllRevealElements();
      return;
    }

    enableTilt();
    enableReveal();
  };

  if (tiltElements.length || revealElements.length) {
    applyMotionPreferences();
    attachMediaListener(prefersReducedMotion, applyMotionPreferences);
    attachMediaListener(pointerFine, applyMotionPreferences);
    window.addEventListener('pagehide', disableTilt);
  }
});
