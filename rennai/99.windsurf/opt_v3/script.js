// インタラクティブ要素の実装
document.addEventListener('DOMContentLoaded', function() {
    // モーダル関連の要素を取得
    const emailModal = document.getElementById('emailModal');
    const openModalBtn = document.getElementById('openModalBtn');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const ctaButton = document.getElementById('lineRegisterBtn');

    // モーダルを開く関数
    const openModal = () => {
        if(emailModal) emailModal.style.display = 'flex';
    };

    // モーダルを閉じる関数
    const closeModal = () => {
        if(emailModal) emailModal.style.display = 'none';
    };

    // イベントリスナーの設定
    if(openModalBtn) openModalBtn.addEventListener('click', (e) => {
        e.preventDefault();
        openModal();
    });

    if(closeModalBtn) closeModalBtn.addEventListener('click', closeModal);

    // モーダルの外側をクリックした時に閉じる
    if(emailModal) emailModal.addEventListener('click', (e) => {
        if (e.target === emailModal) {
            closeModal();
        }
    });

    // 既存のCTAボタンもモーダルを開くように変更
    if (ctaButton) {
        ctaButton.addEventListener('click', function(e) {
            e.preventDefault();
            openModal();
        });
    }

    // パーティクルを動的に生成・配置
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        for (let i = 0; i < 30; i++) {
            let particle = document.createElement('div');
            particle.classList.add('particle');
            let size = Math.random() * 3 + 1;
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.top = `${Math.random() * 100}%`;
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.animationDelay = `${Math.random() * 20}s`;
            heroSection.appendChild(particle);
        }
    }

    // テキストのstaggered animation（ずらし表示）
    const fvElements = [
        document.querySelector('.targeting-copy'),
        document.querySelector('.main-copy-vertical'),
        document.querySelector('.sub-copy'),
        document.querySelector('.benefit-copy')
    ];

    fvElements.forEach((el, index) => {
        if (el) {
            setTimeout(() => {
                el.classList.add('is-visible');
            }, 300 * (index + 1));
        }
    });
    
    // スムーズスクロール
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // 強化されたスクロールアニメーション
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    const animationObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });

    animatedElements.forEach(el => {
        animationObserver.observe(el);
    });
    
    // ヒーローセクションの視差効果
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const heroSection = document.querySelector('.hero-section');
        
        if (heroSection) {
            const rate = scrolled * -0.5;
            heroSection.style.transform = `translateY(${rate}px)`;
        }
    });
});

// パフォーマンス最適化
window.addEventListener('load', function() {
    // 画像の遅延読み込み
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
});
