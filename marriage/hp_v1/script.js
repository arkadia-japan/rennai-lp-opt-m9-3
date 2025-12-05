// DOM要素の取得
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');
const consultationForm = document.getElementById('consultationForm');
const navLinks = document.querySelectorAll('.nav-menu a[href^="#"]');

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', function() {
    initializeAnimations();
    initializeFormValidation();
    initializeScrollEffects();
});

// ハンバーガーメニューの制御
hamburger.addEventListener('click', function() {
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
    document.body.classList.toggle('menu-open');
});

// ナビゲーションリンクのスムーズスクロール
navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        const targetSection = document.querySelector(targetId);
        
        if (targetSection) {
            const headerHeight = document.querySelector('.header').offsetHeight;
            const targetPosition = targetSection.offsetTop - headerHeight;
            
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
            
            // モバイルメニューを閉じる
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
            document.body.classList.remove('menu-open');
        }
    });
});

// スクロール時のヘッダー制御
window.addEventListener('scroll', function() {
    const header = document.querySelector('.header');
    const scrollTop = window.pageYOffset;
    
    if (scrollTop > 100) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

// フォームバリデーションの初期化
function initializeFormValidation() {
    const form = document.getElementById('consultationForm');
    const inputs = form.querySelectorAll('input[required], select[required]');
    
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearError);
    });
    
    form.addEventListener('submit', handleFormSubmit);
}

// 個別フィールドのバリデーション
function validateField(e) {
    const field = e.target;
    const value = field.value.trim();
    const fieldType = field.type;
    const fieldName = field.name;
    
    clearError(e);
    
    if (!value) {
        showError(field, 'この項目は必須です');
        return false;
    }
    
    // メールアドレスのバリデーション
    if (fieldType === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showError(field, '正しいメールアドレスを入力してください');
            return false;
        }
    }
    
    // 電話番号のバリデーション
    if (fieldType === 'tel') {
        const phoneRegex = /^[\d\-\(\)\+\s]+$/;
        if (!phoneRegex.test(value) || value.length < 10) {
            showError(field, '正しい電話番号を入力してください');
            return false;
        }
    }
    
    // 名前のバリデーション
    if (fieldName === 'name') {
        if (value.length < 2) {
            showError(field, '名前は2文字以上で入力してください');
            return false;
        }
    }
    
    return true;
}

// エラー表示
function showError(field, message) {
    const formGroup = field.closest('.form-group');
    let errorElement = formGroup.querySelector('.error-message');
    
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        formGroup.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
    field.classList.add('error');
}

// エラークリア
function clearError(e) {
    const field = e.target;
    const formGroup = field.closest('.form-group');
    const errorElement = formGroup.querySelector('.error-message');
    
    if (errorElement) {
        errorElement.remove();
    }
    field.classList.remove('error');
}

// フォーム送信処理
function handleFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const requiredFields = form.querySelectorAll('input[required], select[required]');
    let isValid = true;
    
    // 全必須フィールドのバリデーション
    requiredFields.forEach(field => {
        const mockEvent = { target: field };
        if (!validateField(mockEvent)) {
            isValid = false;
        }
    });
    
    // プライバシーポリシーの同意確認
    const privacyCheckbox = form.querySelector('#privacy');
    if (!privacyCheckbox.checked) {
        showError(privacyCheckbox, 'プライバシーポリシーに同意してください');
        isValid = false;
    }
    
    if (!isValid) {
        // 最初のエラーフィールドにスクロール
        const firstError = form.querySelector('.error');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        return;
    }
    
    // フォーム送信処理（実際のプロジェクトではサーバーに送信）
    showSuccessMessage();
    form.reset();
}

// 成功メッセージの表示
function showSuccessMessage() {
    const successModal = createSuccessModal();
    document.body.appendChild(successModal);
    
    setTimeout(() => {
        successModal.classList.add('show');
    }, 100);
    
    // 5秒後に自動で閉じる
    setTimeout(() => {
        closeSuccessModal(successModal);
    }, 5000);
}

// 成功モーダルの作成
function createSuccessModal() {
    const modal = document.createElement('div');
    modal.className = 'success-modal';
    modal.innerHTML = `
        <div class="success-modal-content">
            <div class="success-icon">
                <i class="fas fa-check-circle"></i>
            </div>
            <h3>お申し込みありがとうございます</h3>
            <p>
                無料相談のお申し込みを受け付けました。<br>
                24時間以内に担当者よりご連絡いたします。
            </p>
            <button class="btn-primary" onclick="closeSuccessModal(this.closest('.success-modal'))">
                閉じる
            </button>
        </div>
    `;
    
    return modal;
}

// 成功モーダルを閉じる
function closeSuccessModal(modal) {
    modal.classList.remove('show');
    setTimeout(() => {
        if (modal.parentNode) {
            modal.parentNode.removeChild(modal);
        }
    }, 300);
}

// スクロールエフェクトの初期化
function initializeScrollEffects() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // アニメーション対象要素の監視
    const animateElements = document.querySelectorAll(
        '.problem-card, .feature, .stat-card, .testimonial, .step, .plan'
    );
    
    animateElements.forEach(element => {
        observer.observe(element);
    });
}

// 初期アニメーションの設定
function initializeAnimations() {
    // ヒーローセクションのアニメーション
    const heroElements = document.querySelectorAll('.hero-title, .hero-subtitle, .hero-stats, .hero-cta');
    heroElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 200);
    });
}

// 統計数値のカウントアップアニメーション
function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        
        if (target.toString().includes('%')) {
            element.textContent = Math.floor(current) + '%';
        } else if (target.toString().includes('ヶ月')) {
            element.textContent = Math.floor(current) + 'ヶ月';
        } else {
            element.textContent = Math.floor(current) + '+';
        }
    }, 16);
}

// 統計セクションが表示されたときのカウントアップ
const statsObserver = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const statNumbers = entry.target.querySelectorAll('.stat-number, .stat-big');
            statNumbers.forEach(stat => {
                const text = stat.textContent;
                if (text.includes('%')) {
                    const num = parseInt(text);
                    animateCounter(stat, num);
                } else if (text.includes('ヶ月')) {
                    const num = parseFloat(text);
                    animateCounter(stat, num);
                } else if (text.includes('+')) {
                    const num = parseInt(text);
                    animateCounter(stat, num);
                }
            });
            statsObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

// 統計セクションを監視
document.addEventListener('DOMContentLoaded', function() {
    const heroStats = document.querySelector('.hero-stats');
    const successStats = document.querySelector('.success-stats');
    
    if (heroStats) statsObserver.observe(heroStats);
    if (successStats) statsObserver.observe(successStats);
});

// ページトップへ戻るボタン
function createBackToTopButton() {
    const button = document.createElement('button');
    button.className = 'back-to-top';
    button.innerHTML = '<i class="fas fa-chevron-up"></i>';
    button.setAttribute('aria-label', 'ページトップへ戻る');
    
    button.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    document.body.appendChild(button);
    
    // スクロール時の表示制御
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            button.classList.add('show');
        } else {
            button.classList.remove('show');
        }
    });
}

// ページトップボタンの初期化
document.addEventListener('DOMContentLoaded', createBackToTopButton);

// レスポンシブ対応：ウィンドウリサイズ時の処理
window.addEventListener('resize', function() {
    // モバイルメニューが開いている状態でデスクトップサイズになった場合
    if (window.innerWidth > 768) {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
        document.body.classList.remove('menu-open');
    }
});

// パフォーマンス最適化：スクロールイベントのスロットリング
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

// スクロールイベントをスロットリング
window.addEventListener('scroll', throttle(function() {
    // ヘッダーのスクロール効果
    const header = document.querySelector('.header');
    const scrollTop = window.pageYOffset;
    
    if (scrollTop > 100) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
}, 100));
