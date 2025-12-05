(function() {
    'use strict';

    // カウントダウンの終了日時（現在から72時間後）
    const DEADLINE = new Date(Date.now() + 72 * 60 * 60 * 1000);

    // DOM要素の取得
    const countdownElement = document.getElementById('countdown');
    const countdownDisplay = document.getElementById('countdown-display');
    const liveMessage = document.getElementById('live-message');

    /**
     * CTAセクションへのスムーズスクロール
     */
    function scrollToCTA() {
        const ctaSection = document.getElementById('cta');
        if (ctaSection) {
            ctaSection.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }

    /**
     * 時間を2桁表示にフォーマット
     * @param {number} time - フォーマットする時間
     * @returns {string} - 2桁でフォーマットされた時間
     */
    function formatTime(time) {
        return time.toString().padStart(2, '0');
    }

    /**
     * カウントダウンの更新
     */
    function updateCountdown() {
        const now = new Date().getTime();
        const distance = DEADLINE.getTime() - now;

        // 時間が経過した場合
        if (distance < 0) {
            showLiveMessage();
            return;
        }

        // 残り時間を計算
        const hours = Math.floor(distance / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // カウントダウン表示を更新
        if (countdownDisplay) {
            countdownDisplay.textContent = `${hours}時間${formatTime(minutes)}分${formatTime(seconds)}秒`;
        }
    }

    /**
     * 公開中メッセージを表示
     */
    function showLiveMessage() {
        if (countdownElement) {
            countdownElement.style.display = 'none';
        }
        if (liveMessage) {
            liveMessage.style.display = 'block';
        }

        // カウントダウンタイマーを停止
        clearInterval(countdownTimer);
    }

    /**
     * スクロールアニメーションの実装
     */
    function initScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, observerOptions);

        // アニメーション対象要素を選択
        const animateElements = document.querySelectorAll('.lesson-card, .result-card, .benefits__title, .benefits__description, .profile__title');

        animateElements.forEach(function(element, index) {
            element.classList.add('fade-in');
            element.style.transitionDelay = `${index * 0.1}s`;
            observer.observe(element);
        });
    }

    /**
     * マイクロインタラクションの実装
     */
    function initMicroInteractions() {
        // ボタンのリップル効果
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                const ripple = document.createElement('span');
                const rect = button.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;

                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                ripple.classList.add('ripple');

                button.appendChild(ripple);

                setTimeout(function() {
                    ripple.remove();
                }, 600);
            });
        });

        // カードのパララックス効果
        const cards = document.querySelectorAll('.lesson-card, .result-card');
        cards.forEach(function(card) {
            card.addEventListener('mousemove', function(e) {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                const rotateX = (y - centerY) / 10;
                const rotateY = (centerX - x) / 10;

                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
            });

            card.addEventListener('mouseleave', function() {
                card.style.transform = '';
            });
        });
    }

    /**
     * パフォーマンス最適化
     */
    function optimizePerformance() {
        // 画像の遅延読み込み（今回は画像なしだが、将来的な拡張用）
        if ('IntersectionObserver' in window) {
            // スクロールアニメーション用のObserverを既に実装済み
        }

        // フォントの最適化
        if ('fonts' in document) {
            document.fonts.ready.then(function() {
                document.body.classList.add('fonts-loaded');
            });
        }
    }

    /**
     * 初期化処理
     */
    function init() {
        // グローバル関数として登録（ボタンのonclick用）
        window.scrollToCTA = scrollToCTA;

        // カウントダウンの初期表示
        updateCountdown();

        // 1秒ごとにカウントダウンを更新
        window.countdownTimer = setInterval(updateCountdown, 1000);

        // スクロールアニメーションの初期化
        initScrollAnimations();

        // マイクロインタラクションの初期化
        initMicroInteractions();

        // パフォーマンス最適化
        optimizePerformance();

        // キーボードアクセシビリティの向上
        document.addEventListener('keydown', function(event) {
            // Enterキーでボタンをクリック
            if (event.key === 'Enter' && event.target.classList.contains('btn')) {
                event.target.click();
            }
        });

        // すべてのボタンにaria-labelを追加
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(function(button) {
            if (!button.getAttribute('aria-label')) {
                button.setAttribute('aria-label', button.textContent.trim());
            }
        });
    }

    // DOMが読み込まれたら初期化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

// リップル効果のCSS（動的に追加）
const rippleCSS = `
.btn {
    position: relative;
    overflow: hidden;
}

.ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.4);
    transform: scale(0);
    animation: ripple-animation 0.6s linear;
    pointer-events: none;
}

@keyframes ripple-animation {
    to {
        transform: scale(2);
        opacity: 0;
    }
}

.fonts-loaded {
    font-display: swap;
}
`;

// CSSを動的に追加
const style = document.createElement('style');
style.textContent = rippleCSS;
document.head.appendChild(style);