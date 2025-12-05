// カウントアップアニメーション
function animateCount(el) {
  const target = +el.getAttribute('data-count');
  const duration = 1500; // ms
  const start = 0;
  const startTime = performance.now();

  function update(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const current = Math.floor(progress * (target - start) + start);
    el.textContent = current;
    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }
  requestAnimationFrame(update);
}

// 要素がビューポートに入ったらトリガー
function onScroll() {
  document.querySelectorAll('.stat-number').forEach((el) => {
    if (!el.classList.contains('animated')) {
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight * 0.9) {
        el.classList.add('animated');
        animateCount(el);
      }
    }
  });
}

window.addEventListener('scroll', onScroll);
window.addEventListener('DOMContentLoaded', onScroll);
