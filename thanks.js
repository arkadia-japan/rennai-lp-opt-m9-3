document.addEventListener('DOMContentLoaded', () => {
  const countdown = document.querySelector('.thanks-countdown');
  if (!countdown) {
    return;
  }

  const hoursEl = countdown.querySelector('[data-countdown-hours]');
  const minutesEl = countdown.querySelector('[data-countdown-minutes-display]');
  const secondsEl = countdown.querySelector('[data-countdown-seconds]');

  if (!hoursEl || !minutesEl || !secondsEl) {
    return;
  }

  const minutesSetting = parseInt(countdown.dataset.countdownMinutes || '30', 10);
  const durationMs = Number.isNaN(minutesSetting) ? 30 * 60 * 1000 : minutesSetting * 60 * 1000;
  const storageKey = `rennaiThanksCountdownDeadline:${window.location.pathname}`;
  const now = Date.now();

  let deadline = now + durationMs;

  try {
    const storedDeadline = window.localStorage.getItem(storageKey);
    if (storedDeadline) {
      const parsed = parseInt(storedDeadline, 10);
      if (!Number.isNaN(parsed) && parsed > now) {
        deadline = parsed;
      }
    } else {
      window.localStorage.setItem(storageKey, String(deadline));
    }
  } catch (error) {
    // localStorage unavailable; proceed with calculated deadline
  }

  const updateDisplay = (diff) => {
    if (diff <= 0) {
      hoursEl.textContent = '00';
      minutesEl.textContent = '00';
      secondsEl.textContent = '00';
      countdown.classList.add('is-finished');
      return;
    }

    const remainingHours = Math.floor(diff / (1000 * 60 * 60));
    const remainingMinutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const remainingSeconds = Math.floor((diff % (1000 * 60)) / 1000);

    hoursEl.textContent = String(remainingHours).padStart(2, '0');
    minutesEl.textContent = String(remainingMinutes).padStart(2, '0');
    secondsEl.textContent = String(remainingSeconds).padStart(2, '0');
  };

  updateDisplay(deadline - Date.now());

  setInterval(() => {
    updateDisplay(deadline - Date.now());
  }, 1000);
});
