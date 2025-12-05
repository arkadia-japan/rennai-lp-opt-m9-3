// script.js
// Author: Windsurf AI generated
// Description: Handles modal interactions, CTA triggers, and accordion UI

// ===== Modal Handling =====
const modal = document.getElementById('modal');
const overlay = document.getElementById('modal-overlay');
const modalCloseBtn = document.getElementById('modal-close');
const ctaHero = document.getElementById('cta-hero');
const ctaFinal = document.getElementById('cta-final');

function openModal() {
  modal.classList.remove('hidden');
  overlay.classList.remove('hidden');
  document.body.style.overflow = 'hidden'; // Prevent background scroll
}

function closeModal() {
  modal.classList.add('hidden');
  overlay.classList.add('hidden');
  document.body.style.overflow = '';
}

ctaHero?.addEventListener('click', openModal);
ctaFinal?.addEventListener('click', openModal);
modalCloseBtn?.addEventListener('click', closeModal);
overlay?.addEventListener('click', closeModal);

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
    closeModal();
  }
});

// ===== Accordion Handling (改) =====
const accordion = document.getElementById('accordion');

if (accordion) {
  accordion.addEventListener('click', (e) => {
    const header = e.target.closest('.accordion-header');
    if (!header) return;

    const item = header.parentElement;
    const body = item.querySelector('.accordion-body');
    const isOpen = item.classList.contains('is-open');

    // すべて閉じる
    accordion.querySelectorAll('.accordion-item').forEach((openItem) => {
      openItem.classList.remove('is-open');
      openItem.querySelector('.accordion-body').style.maxHeight = null;
    });

    // 閉じていた場合のみ開く
    if (!isOpen) {
      item.classList.add('is-open');
      body.style.maxHeight = body.scrollHeight + 'px';
    }
  });
}
