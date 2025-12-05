// 完全リニューアル - プレミアムJavaScript

document.addEventListener('DOMContentLoaded', function() {
    // ヘッダースクロール効果
    initHeaderScrollEffect();

    // スムーススクロール
    initSmoothScroll();

    // スクロールアニメーション
    initScrollAnimations();

    // 統計カウンターアニメーション
    initCounterAnimations();

    // フォーム処理
    initFormHandling();

    // カウントダウンタイマー
    initCountdownTimer();

    // パララックス効果
    initParallaxEffects();

    // 高度なインタラクション
    initAdvancedInteractions();
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

// 統計カウンターアニメーション
function initCounterAnimations() {
    const counters = document.querySelectorAll('.stat-value, .stat-number');

    const animateCounter = (element) => {
        const target = parseInt(element.textContent.replace(/[^0-9]/g, ''));
        const duration = 2000;
        const increment = target / (duration / 16);
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }

            const originalText = element.textContent;
            const suffix = originalText.replace(/[0-9]/g, '').replace(',', '');
            element.textContent = Math.floor(current).toLocaleString() + suffix;
        }, 16);
    };

    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => {
        counterObserver.observe(counter);
    });
}

// フォーム処理
function initFormHandling() {
    // セミナーフォーム処理
    const seminarForm = document.getElementById('seminar-form');
    const modal = document.getElementById('success-modal');

    if (seminarForm) {
        seminarForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // フォームバリデーション
            const formData = new FormData(seminarForm);
            const name = formData.get('name');
            const email = formData.get('email');

            if (!name || !email) {
                showNotification('すべての項目を入力してください', 'error');
                return;
            }

            if (!isValidEmail(email)) {
                showNotification('正しいメールアドレスを入力してください', 'error');
                return;
            }

            // 送信アニメーション
            const submitButton = seminarForm.querySelector('.submit-btn');
            const originalText = submitButton.innerHTML;

            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> セミナー準備中...';
            submitButton.disabled = true;

            // シミュレートされた送信処理
            setTimeout(() => {
                submitButton.innerHTML = originalText;
                submitButton.disabled = false;

                // 成功モーダル表示
                showModal();

                // フォームリセット
                seminarForm.reset();

                // トラッキング（実際の実装では適切な分析ツールを使用）
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'seminar_signup', {
                        event_category: 'engagement',
                        event_label: 'seminar_form'
                    });
                }
            }, 2000);
        });
    }

    // 診断フォーム処理（既存）
    const diagnosisForm = document.getElementById('diagnosis-form');
    if (diagnosisForm) {
        diagnosisForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // フォームバリデーション
            const formData = new FormData(diagnosisForm);
            const name = formData.get('name');
            const email = formData.get('email');
            const age = formData.get('age');

            if (!name || !email || !age) {
                showNotification('すべての項目を入力してください', 'error');
                return;
            }

            if (!isValidEmail(email)) {
                showNotification('正しいメールアドレスを入力してください', 'error');
                return;
            }

            // 送信アニメーション
            const submitButton = diagnosisForm.querySelector('.submit-btn');
            const originalText = submitButton.innerHTML;

            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 診断結果を準備中...';
            submitButton.disabled = true;

            // シミュレートされた送信処理
            setTimeout(() => {
                submitButton.innerHTML = originalText;
                submitButton.disabled = false;

                // 成功モーダル表示
                showModal();

                // フォームリセット
                diagnosisForm.reset();

                // トラッキング（実際の実装では適切な分析ツールを使用）
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'form_submit', {
                        event_category: 'engagement',
                        event_label: 'diagnosis_form'
                    });
                }
            }, 2000);
        });
    }

    // CTA セクションのフォーム
    const ctaForm = document.getElementById('cta-form');
    if (ctaForm) {
        ctaForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // セミナーフォームにスクロール
            document.getElementById('video-form').scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        });
    }
}

// メールバリデーション
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// カウントダウンタイマー
function initCountdownTimer() {
    const hoursElement = document.getElementById('hours');
    const minutesElement = document.getElementById('minutes');
    const secondsElement = document.getElementById('seconds');

    if (!hoursElement || !minutesElement || !secondsElement) return;

    // 24時間後の終了時刻を設定
    const endTime = new Date();
    endTime.setHours(endTime.getHours() + 24);

    function updateTimer() {
        const now = new Date();
        const timeLeft = endTime - now;

        if (timeLeft > 0) {
            const hours = Math.floor(timeLeft / (1000 * 60 * 60));
            const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

            hoursElement.textContent = hours.toString().padStart(2, '0');
            minutesElement.textContent = minutes.toString().padStart(2, '0');
            secondsElement.textContent = seconds.toString().padStart(2, '0');
        } else {
            // タイマー終了時
            hoursElement.textContent = '00';
            minutesElement.textContent = '00';
            secondsElement.textContent = '00';

            // 固定フッターを非表示にする
            const fixedCta = document.getElementById('fixed-cta');
            if (fixedCta) {
                fixedCta.style.display = 'none';
            }
        }
    }

    // 初回実行
    updateTimer();

    // 1秒ごとに更新
    setInterval(updateTimer, 1000);
}

// 通知表示
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;

    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'error' ? '#ef4444' : '#0ea5e9'};
        color: white;
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        z-index: 10001;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        display: flex;
        align-items: center;
        gap: 12px;
        font-weight: 500;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);

    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// モーダル表示
function showModal() {
    const modal = document.getElementById('success-modal');
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';

        // アニメーション効果
        setTimeout(() => {
            modal.style.opacity = '1';
        }, 50);
    }
}

// モーダル閉じる
function closeModal() {
    const modal = document.getElementById('success-modal');
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
window.closeModal = closeModal;