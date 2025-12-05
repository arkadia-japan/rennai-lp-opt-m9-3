// THE ONLY ONE LP scripts
(function () {
  'use strict';

  // Smooth scroll for [data-scroll]
  const scrollLinks = document.querySelectorAll('[data-scroll]');
  for (const link of scrollLinks) {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      if (href && href.startsWith('#')) {
        const target = document.querySelector(href);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    });
  }

  // Accordion behavior
  const items = document.querySelectorAll('.accordion__item');
  items.forEach((item) => {
    const header = item.querySelector('.accordion__header');
    const panel = item.querySelector('.accordion__panel');
    if (!header || !panel) return;

    header.addEventListener('click', () => toggle(item, header, panel));
    header.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        toggle(item, header, panel);
      }
    });
  });

  function toggle(item, header, panel) {
    const expanded = header.getAttribute('aria-expanded') === 'true';
    header.setAttribute('aria-expanded', String(!expanded));
    panel.setAttribute('aria-hidden', String(expanded));
  }

  // Reveal on scroll (fade-in)
  const revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.1 });

    revealEls.forEach((el) => io.observe(el));
  } else {
    // Fallback for older browsers
    revealEls.forEach((el) => el.classList.add('is-visible'));
  }

  // Opt-in form simple validation
  const form = document.querySelector('.optin__form');
  if (form) {
    const input = form.querySelector('input[type="email"]');
    const note = form.querySelector('.optin__note');

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = (input?.value || '').trim();
      if (!isValidEmail(email)) {
        input?.focus();
        if (note) note.textContent = '正しいメールアドレスを入力してください。';
        return;
      }
      if (note) note.textContent = 'ありがとうございます。入力いただいたメールアドレスに講座のご案内をお送りします。';
      form.reset();
    });
  }

  function isValidEmail(email) {
    // シンプルなメール検証（HTML5のバリデーションに加えて軽く確認）
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }
})();
