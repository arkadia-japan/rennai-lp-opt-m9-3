// THE ONLY ONE - 恋愛講座LP JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // ヘッダースクロール効果
    initHeaderScrollEffect();

    // スムーススクロール
    initSmoothScroll();

    // スクロールアニメーション
    initScrollAnimations();

    // カウントダウンタイマー
    initCountdownTimer();

    // 動画モーダル
    initVideoModal();

    // パララックス効果
    initParallaxEffects();

    // 高度なインタラクション
    initAdvancedInteractions();

    // 固定フッターCTAを常に表示
    const fixedFooterCta = document.querySelector('.fixed-footer-cta');
    if (fixedFooterCta) {
        fixedFooterCta.style.transform = 'translateY(0)';
    }
});

// ヘッダースクロール効果
function initHeaderScrollEffect() {
    const header = document.getElementById('header');
    let lastScrollY = window.scrollY;

    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;

        if (currentScrollY > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }

        // ヘッダーの表示/非表示
        if (currentScrollY > lastScrollY && currentScrollY > 200) {
            header.style.transform = 'translateY(-100%)';
        } else {
            header.style.transform = 'translateY(0)';
        }

        lastScrollY = currentScrollY;
    });
}

// スムーススクロール
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = target.offsetTop - headerHeight;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// スクロールアニメーション
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');

                // 連続アニメーション
                if (entry.target.classList.contains('stagger-animation')) {
                    const children = entry.target.querySelectorAll('.animate-on-scroll');
                    children.forEach((child, index) => {
                        setTimeout(() => {
                            child.classList.add('visible');
                        }, index * 100);
                    });
                }
            }
        });
    }, observerOptions);

    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });

    // セクション全体のアニメーション
    document.querySelectorAll('section').forEach(section => {
        observer.observe(section);
    });
}

// カウントダウンタイマー
function initCountdownTimer() {
    const hoursElement = document.getElementById('hours');
    const minutesElement = document.getElementById('minutes');
    const secondsElement = document.getElementById('seconds');

    if (!hoursElement || !minutesElement || !secondsElement) return;

    // 24時間後の時刻を設定
    const targetTime = new Date().getTime() + (24 * 60 * 60 * 1000);

    function updateTimer() {
        const now = new Date().getTime();
        const timeLeft = targetTime - now;

        if (timeLeft > 0) {
            const hours = Math.floor(timeLeft / (1000 * 60 * 60));
            const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

            hoursElement.textContent = hours.toString().padStart(2, '0');
            minutesElement.textContent = minutes.toString().padStart(2, '0');
            secondsElement.textContent = seconds.toString().padStart(2, '0');
        } else {
            // タイマー終了時の処理
            hoursElement.textContent = '00';
            minutesElement.textContent = '00';
            secondsElement.textContent = '00';
        }
    }

    // 初回実行
    updateTimer();

    // 1秒ごとに更新
    setInterval(updateTimer, 1000);
}

// 動画モーダル
function initVideoModal() {
    const modal = document.getElementById('video-modal');
    const ctaButtons = document.querySelectorAll('a[href="#cta"], .btn-primary');

    // CTAボタンクリック時にモーダルを開く
    ctaButtons.forEach(button => {
        if (button.onclick || button.getAttribute('onclick')) return; // 既にonclickが設定されている場合はスキップ
        
        button.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#cta' || this.classList.contains('btn-primary')) {
                e.preventDefault();
                openVideoModal();
            }
        });
    });

    // モーダル外クリックで閉じる
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeVideoModal();
            }
        });
    }
}

// 動画モーダルを開く
function openVideoModal() {
    const modal = document.getElementById('video-modal');
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        
        // アニメーション効果
        setTimeout(() => {
            modal.style.opacity = '1';
        }, 50);

        // トラッキング
        if (typeof gtag !== 'undefined') {
            gtag('event', 'video_modal_open', {
                event_category: 'engagement',
                event_label: 'the_only_one_method'
            });
        }
    }
}

// 動画モーダルを閉じる
function closeVideoModal() {
    const modal = document.getElementById('video-modal');
    if (modal) {
        modal.style.opacity = '0';
        document.body.style.overflow = 'auto';
        
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }
}


// パララックス効果
function initParallaxEffects() {
    const parallaxElements = document.querySelectorAll('.hero, .cta-section');

    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;

        parallaxElements.forEach(element => {
            if (element.classList.contains('hero')) {
                element.style.transform = `translateY(${rate}px)`;
            }
        });
    });
}

// 高度なインタラクション
function initAdvancedInteractions() {
    // カードホバー効果
    initCardHoverEffects();

    // プログレスバー
    initProgressBars();

    // 視差効果
    initParallaxCards();

    // マウス追従効果
    initMouseFollowEffects();
}

// カードホバー効果
function initCardHoverEffects() {
    const cards = document.querySelectorAll('.stat-card, .problem-card, .feature-card, .testimonial-card');

    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-12px) scale(1.02)';
            this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });

        // 3D効果
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;

            this.style.transform = `translateY(-12px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) rotateX(0) rotateY(0) scale(1)';
        });
    });
}

// プログレスバー
function initProgressBars() {
    const progressElements = document.querySelectorAll('.progress-bar');

    const progressObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const progress = entry.target;
                const width = progress.getAttribute('data-width') || '0';

                setTimeout(() => {
                    progress.style.width = width + '%';
                }, 500);

                progressObserver.unobserve(progress);
            }
        });
    });

    progressElements.forEach(element => {
        progressObserver.observe(element);
    });
}

// 視差カード
function initParallaxCards() {
    const cards = document.querySelectorAll('.point-card');

    window.addEventListener('scroll', () => {
        cards.forEach((card, index) => {
            const rect = card.getBoundingClientRect();
            const speed = 0.1 + (index * 0.05);
            const yPos = -(window.pageYOffset * speed);

            if (rect.bottom >= 0 && rect.top <= window.innerHeight) {
                card.style.transform = `translateY(${yPos}px)`;
            }
        });
    });
}

// マウス追従効果
function initMouseFollowEffects() {
    const hero = document.querySelector('.hero');

    if (hero) {
        hero.addEventListener('mousemove', (e) => {
            const x = e.clientX / window.innerWidth;
            const y = e.clientY / window.innerHeight;

            const moveX = (x - 0.5) * 50;
            const moveY = (y - 0.5) * 50;

            hero.style.backgroundPosition = `${50 + moveX}% ${50 + moveY}%`;
        });
    }
}

// フォーム入力エンハンスメント
function initFormEnhancements() {
    const inputs = document.querySelectorAll('.form-group input, .form-group select');

    inputs.forEach(input => {
        // フォーカス効果
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
            if (this.value) {
                this.parentElement.classList.add('filled');
            } else {
                this.parentElement.classList.remove('filled');
            }
        });

        // リアルタイムバリデーション
        input.addEventListener('input', function() {
            validateField(this);
        });
    });
}

// フィールドバリデーション
function validateField(field) {
    const value = field.value.trim();
    const type = field.type;
    const name = field.name;

    let isValid = true;
    let message = '';

    switch (name) {
        case 'name':
            isValid = value.length >= 2;
            message = '名前は2文字以上で入力してください';
            break;
        case 'email':
            isValid = isValidEmail(value);
            message = '正しいメールアドレスを入力してください';
            break;
        case 'age':
            isValid = value !== '';
            message = '年齢を選択してください';
            break;
    }

    const formGroup = field.parentElement;
    const errorElement = formGroup.querySelector('.field-error');

    if (errorElement) {
        errorElement.remove();
    }

    if (!isValid && value !== '') {
        const error = document.createElement('div');
        error.className = 'field-error';
        error.textContent = message;
        error.style.cssText = `
            color: #ef4444;
            font-size: 0.875rem;
            margin-top: 4px;
            font-weight: 500;
        `;
        formGroup.appendChild(error);

        field.style.borderColor = '#ef4444';
    } else {
        field.style.borderColor = '#e5e7eb';
        if (isValid && value !== '') {
            field.style.borderColor = '#10b981';
        }
    }

    return isValid;
}

// パフォーマンス最適化
function initPerformanceOptimizations() {
    // 画像遅延読み込み
    const images = document.querySelectorAll('img[loading="lazy"]');

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// 初期化完了後の追加設定
window.addEventListener('load', function() {
    initFormEnhancements();
    initPerformanceOptimizations();

    // ページ読み込み完了アニメーション
    document.body.classList.add('loaded');
});

// ユーティリティ関数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// スクロール最適化
window.addEventListener('scroll', throttle(() => {
    // スクロール関連の処理
}, 16));

// リサイズ最適化
window.addEventListener('resize', debounce(() => {
    // リサイズ関連の処理
}, 250));

// グローバル関数として公開
window.openVideoModal = openVideoModal;
window.closeVideoModal = closeVideoModal;