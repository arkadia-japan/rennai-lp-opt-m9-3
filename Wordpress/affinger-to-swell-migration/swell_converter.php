<?php
/**
 * Affinger4 → SWELL ショートコード変換スクリプト
 *
 * 使用方法:
 * 1. WordPressルートディレクトリに配置
 * 2. ブラウザで直接アクセス: https://yourdomain.com/swell_converter.php
 * 3. または wp-cli: wp eval-file swell_converter.php
 *
 * 注意:
 * - 必ずバックアップを取ってから実行
 * - ステージング環境でテスト推奨
 * - 本番実行前に DRY_RUN = true で動作確認
 *
 * @version 1.0.0
 * @date 2025-12-08
 */

// WordPress環境を読み込み
require_once('wp-load.php');

// ========================================
// 設定
// ========================================

// DRY RUN（変更を実際には保存しない）
define('DRY_RUN', true); // 本番実行時は false に変更

// 変換対象の投稿タイプ
$POST_TYPES = ['post', 'page'];

// 変換優先度フィルタ（空配列で全変換）
// 例: ['st-card', 'st-mybox'] で特定のショートコードのみ変換
$PRIORITY_FILTER = [];

// ログ出力
$LOG = [];

// ========================================
// 変換ルール定義
// ========================================

class AffingerToSwellConverter {

    /**
     * st-card → SWELLブログカード
     */
    public static function convert_st_card($content) {
        $pattern = '/\[st-card[^\]]*id=(\d+)[^\]]*\]/';
        $replacement = '<!-- wp:swell/blog-card {"postId":$1} /-->';
        return preg_replace($pattern, $replacement, $content);
    }

    /**
     * st-mybox → SWELLボックス（配色マッピング）
     */
    public static function convert_st_mybox($content) {
        // 配色 → スタイルマッピング
        $color_styles = [
            '#ef5350' => 'alert',   // 赤 → アラート
            '#FFD54F' => 'point',   // 黄 → ポイント
            '#4FC3F7' => 'info',    // 青 → インフォ
            '#66BB6A' => 'success', // 緑 → サクセス
        ];

        // パターン1: 注意ポイント（赤）
        $content = preg_replace_callback(
            '/\[st-mybox title="([^"]*)"[^\]]*color="#ef5350"[^\]]*\](.*?)\[\/st-mybox\]/s',
            function($matches) {
                $title = $matches[1];
                $body = trim($matches[2]);
                return self::build_swell_box('alert', $title, $body, 'fa-exclamation-circle');
            },
            $content
        );

        // パターン2: ポイント（黄）
        $content = preg_replace_callback(
            '/\[st-mybox title="([^"]*)"[^\]]*color="#FFD54F"[^\]]*\](.*?)\[\/st-mybox\]/s',
            function($matches) {
                $title = $matches[1];
                $body = trim($matches[2]);
                return self::build_swell_box('point', $title, $body, 'fa-check-circle');
            },
            $content
        );

        // パターン3: その他（デフォルト）
        $content = preg_replace_callback(
            '/\[st-mybox title="([^"]*)"[^\]]*\](.*?)\[\/st-mybox\]/s',
            function($matches) {
                $title = $matches[1];
                $body = trim($matches[2]);
                return self::build_swell_box('default', $title, $body);
            },
            $content
        );

        return $content;
    }

    /**
     * st-midasibox → SWELL見出しボックス
     */
    public static function convert_st_midasibox($content) {
        $content = preg_replace_callback(
            '/\[st-midasibox title="([^"]*)"[^\]]*\](.*?)\[\/st-midasibox\]/s',
            function($matches) {
                $title = $matches[1];
                $body = trim($matches[2]);
                return self::build_swell_box('solid', $title, $body);
            },
            $content
        );
        return $content;
    }

    /**
     * st-mybutton → SWELLボタン
     */
    public static function convert_st_mybutton($content) {
        $content = preg_replace_callback(
            '/\[st-mybutton url="([^"]*)" title="([^"]*)"[^\]]*\]/s',
            function($matches) {
                $url = $matches[1];
                $text = $matches[2];

                // target="_blank" を検出
                $target = strpos($matches[0], 'target="_blank"') !== false ? '_blank' : '_self';

                // 配色を抽出（オプション）
                preg_match('/bgcolor="([^"]*)"/', $matches[0], $bgcolor_match);
                $bgcolor = $bgcolor_match[1] ?? '#F48FB1';

                preg_match('/color="([^"]*)"/', $matches[0], $color_match);
                $color = $color_match[1] ?? '#fff';

                return self::build_swell_button($url, $text, $target, $bgcolor, $color);
            },
            $content
        );
        return $content;
    }

    /**
     * st-kaiwa1/2/3/5/7 → SWELLふきだし
     */
    public static function convert_st_kaiwa($content) {
        // キャラクターマッピング
        $characters = [
            'st-kaiwa1' => ['id' => 1, 'name' => 'キャラクター1'],
            'st-kaiwa2' => ['id' => 2, 'name' => 'キャラクター2'],
            'st-kaiwa3' => ['id' => 3, 'name' => 'キャラクター3'],
            'st-kaiwa5' => ['id' => 5, 'name' => 'キャラクター5'],
            'st-kaiwa7' => ['id' => 7, 'name' => 'キャラクター7'],
        ];

        foreach ($characters as $shortcode => $char) {
            // 右寄せ（r属性あり）
            $content = preg_replace_callback(
                "/\[{$shortcode}\s+r\](.*?)\[\/{$shortcode}\]/s",
                function($matches) use ($char) {
                    return self::build_swell_balloon($matches[1], $char['id'], $char['name'], 'right');
                },
                $content
            );

            // 左寄せ（デフォルト）
            $content = preg_replace_callback(
                "/\[{$shortcode}\](.*?)\[\/{$shortcode}\]/s",
                function($matches) use ($char) {
                    return self::build_swell_balloon($matches[1], $char['id'], $char['name'], 'left');
                },
                $content
            );
        }

        return $content;
    }

    /**
     * st-minihukidashi → SWELLふきだし（ミニ）
     */
    public static function convert_st_minihukidashi($content) {
        $content = preg_replace_callback(
            '/\[st-minihukidashi[^\]]*\](.*?)\[\/st-minihukidashi\]/s',
            function($matches) {
                $text = trim($matches[1]);

                // アイコンを抽出
                preg_match('/fontawesome="([^"]*)"/', $matches[0], $icon_match);
                $icon = $icon_match[1] ?? 'fa-info-circle';

                // 配色を抽出
                preg_match('/bgcolor="([^"]*)"/', $matches[0], $bgcolor_match);
                $bgcolor = $bgcolor_match[1] ?? '#ef5350';

                preg_match('/color="([^"]*)"/', $matches[0], $color_match);
                $color = $color_match[1] ?? '#fff';

                return self::build_swell_mini_balloon($text, $icon, $bgcolor, $color);
            },
            $content
        );
        return $content;
    }

    /**
     * star → HTML（カスタムCSS）
     */
    public static function convert_star($content) {
        $content = preg_replace_callback(
            '/\[star\s+([0-9\.]+)\]/',
            function($matches) {
                $rating = floatval($matches[1]);
                $full_stars = floor($rating);
                $has_half_star = ($rating - $full_stars) >= 0.5;
                $empty_stars = 5 - $full_stars - ($has_half_star ? 1 : 0);

                $stars = str_repeat('★', $full_stars);
                if ($has_half_star) $stars .= '⯨';
                $stars .= str_repeat('☆', $empty_stars);

                return '<span class="star-rating" data-rating="' . $rating . '">' . $stars . '</span>';
            },
            $content
        );
        return $content;
    }

    // ========================================
    // ビルダーヘルパー
    // ========================================

    private static function build_swell_box($style, $title, $body, $icon = '') {
        $icon_html = $icon ? '<i class="fa ' . $icon . '"></i> ' : '';

        return <<<HTML
<!-- wp:swell/box {"style":"{$style}","title":"{$title}"} -->
<div class="wp-block-swell-box is-style-{$style}">
  <div class="swell-block-box__title">{$icon_html}{$title}</div>
  <div class="swell-block-box__body">{$body}</div>
</div>
<!-- /wp:swell/box -->
HTML;
    }

    private static function build_swell_button($url, $text, $target, $bgcolor, $color) {
        return <<<HTML
<!-- wp:swell/button {"url":"{$url}","text":"{$text}","target":"{$target}","backgroundColor":"{$bgcolor}","textColor":"{$color}"} /-->
HTML;
    }

    private static function build_swell_balloon($content, $avatar_id, $name, $align) {
        return <<<HTML
<!-- wp:swell/balloon {"align":"{$align}","avatarId":{$avatar_id},"name":"{$name}"} -->
<div class="wp-block-swell-balloon is-{$align}">
  <div class="swell-balloon-content">{$content}</div>
</div>
<!-- /wp:swell/balloon -->
HTML;
    }

    private static function build_swell_mini_balloon($text, $icon, $bgcolor, $color) {
        return <<<HTML
<span class="mini-fukidashi" style="background-color:{$bgcolor};color:{$color};">
  <i class="fa {$icon}"></i> {$text}
</span>
HTML;
    }
}

// ========================================
// メイン処理
// ========================================

function run_conversion() {
    global $POST_TYPES, $PRIORITY_FILTER, $LOG;

    echo "<h1>Affinger4 → SWELL 変換スクリプト</h1>\n";
    echo "<p>実行モード: <strong>" . (DRY_RUN ? 'DRY RUN（変更なし）' : '本番実行') . "</strong></p>\n";
    echo "<hr>\n";

    // 変換関数マッピング
    $converters = [
        'st-card' => 'AffingerToSwellConverter::convert_st_card',
        'st-mybox' => 'AffingerToSwellConverter::convert_st_mybox',
        'st-midasibox' => 'AffingerToSwellConverter::convert_st_midasibox',
        'st-mybutton' => 'AffingerToSwellConverter::convert_st_mybutton',
        'st-kaiwa' => 'AffingerToSwellConverter::convert_st_kaiwa',
        'st-minihukidashi' => 'AffingerToSwellConverter::convert_st_minihukidashi',
        'star' => 'AffingerToSwellConverter::convert_star',
    ];

    // フィルタ適用
    if (!empty($PRIORITY_FILTER)) {
        $converters = array_filter($converters, function($key) use ($PRIORITY_FILTER) {
            return in_array($key, $PRIORITY_FILTER);
        }, ARRAY_FILTER_USE_KEY);
    }

    // 投稿を取得
    $args = [
        'post_type' => $POST_TYPES,
        'posts_per_page' => -1,
        'post_status' => 'any',
    ];
    $posts = get_posts($args);

    echo "<p>対象投稿数: <strong>" . count($posts) . "</strong></p>\n";
    echo "<hr>\n";

    $converted_count = 0;
    $total_replacements = 0;

    foreach ($posts as $post) {
        $original_content = $post->post_content;
        $new_content = $original_content;
        $post_replacements = 0;

        // 各変換を適用
        foreach ($converters as $name => $converter) {
            $before = $new_content;
            $new_content = call_user_func($converter, $new_content);

            // 変更があった場合
            if ($before !== $new_content) {
                $count = substr_count($before, '[' . $name) - substr_count($new_content, '[' . $name);
                if ($count > 0) {
                    $post_replacements += $count;
                    $LOG[] = "[ID:{$post->ID}] {$name} x {$count}回変換";
                }
            }
        }

        // 変更があった場合のみ保存
        if ($original_content !== $new_content) {
            $converted_count++;
            $total_replacements += $post_replacements;

            echo "<div style='border:1px solid #ccc; padding:10px; margin:10px 0;'>\n";
            echo "<h3>[ID:{$post->ID}] {$post->post_title}</h3>\n";
            echo "<p>変換数: <strong>{$post_replacements}</strong></p>\n";

            if (!DRY_RUN) {
                wp_update_post([
                    'ID' => $post->ID,
                    'post_content' => $new_content,
                ]);
                echo "<p style='color:green;'>✓ 保存しました</p>\n";
            } else {
                echo "<p style='color:orange;'>⚠ DRY RUNのため保存していません</p>\n";
            }

            echo "</div>\n";
        }
    }

    // サマリー
    echo "<hr>\n";
    echo "<h2>変換完了</h2>\n";
    echo "<ul>\n";
    echo "<li>変換対象投稿数: <strong>{$converted_count}</strong> / " . count($posts) . "</li>\n";
    echo "<li>総置換数: <strong>{$total_replacements}</strong></li>\n";
    echo "</ul>\n";

    if (DRY_RUN) {
        echo "<p style='color:red; font-weight:bold;'>⚠ これはDRY RUNです。実際には保存されていません。</p>\n";
        echo "<p>本番実行する場合は、スクリプト内の DRY_RUN を false に変更してください。</p>\n";
    }

    // ログ詳細
    if (!empty($LOG)) {
        echo "<hr>\n";
        echo "<h3>変換ログ</h3>\n";
        echo "<textarea style='width:100%; height:300px;'>" . implode("\n", $LOG) . "</textarea>\n";
    }
}

// 実行
run_conversion();

?>
