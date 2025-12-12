# Affinger4 → SWELL 移行ガイド

## 📋 ショートコード変換ルール一覧

| # | Affingerショートコード | 使用回数 | 優先度 | SWELL代替案 | 変換方法 | 備考 |
|---|----------------------|---------|--------|------------|---------|------|
| 1 | `st-card` | 190回 | **A** | SWELLブログカードブロック | `<!-- wp:swell/blog-card {"postId":529} /-->` | 内部リンクカードは完全互換 |
| 2 | `st-mybox` | 116回 | **A** | SWELLキャプション付きブロック | `<!-- wp:swell/box -->` | タイトル・アイコン・配色をスタイル設定で再現 |
| 3 | `st-midasibox` | 70回 | **A** | SWELL見出し付きボックス | `<!-- wp:swell/box style="solid" -->` | シンプルな枠線ボックス |
| 4 | `st-mybutton` | 28回 | **A** | SWELLボタンブロック | `<!-- wp:swell/button -->` | グラデーション・アフィリエイトリンク対応 |
| 5 | `caption` | 24回 | **B** | 標準画像ブロック（キャプション） | `<!-- wp:image --><figcaption>` | WordPress標準機能で自動変換 |
| 6 | `star` | 24回 | **B** | HTML（カスタムCSS） | `<span class="star-rating">★★★★☆</span>` | カスタムCSS追加で実装 |
| 7 | `st-minihukidashi` | 15回 | **B** | SWELLふきだしブロック（ミニ） | `<!-- wp:swell/balloon -->` | ミニサイズ設定で代替 |
| 8 | `st-kaiwa1` | 11回 | **A** | SWELLふきだしブロック | `<!-- wp:swell/balloon {"align":"right"} -->` | キャラクター画像・名前設定で完全再現 |
| 9 | `st-kaiwa5` | 9回 | **A** | SWELLふきだしブロック | `<!-- wp:swell/balloon {"align":"right"} -->` | 別キャラクター設定 |
| 10 | `st-mcbutton` | 3回 | **C** | SWELLボタンブロック（複数配置） | `<!-- wp:buttons -->` | ボタンブロック複数並べて代替 |
| 11 | `st-kaiwa2` | 1回 | **B** | SWELLふきだしブロック | `<!-- wp:swell/balloon -->` | 低頻度・手動変換でOK |
| 12 | `st-kaiwa3` | 1回 | **B** | SWELLふきだしブロック | `<!-- wp:swell/balloon -->` | 低頻度・手動変換でOK |
| 13 | `st-kaiwa7` | 1回 | **B** | SWELLふきだしブロック | `<!-- wp:swell/balloon -->` | 低頻度・手動変換でOK |
| - | `With`, `Omiai`, `Google` 等 | 多数 | **C** | 変換不要 | そのまま（テキスト） | 誤検出・サービス名なので変換しない |

---

## 🎨 優先度別の対応方針

### 🔴 優先度A：必須で綺麗に（合計404回・74.7%）

**完全再現が必要なショートコード**

- ユーザー体験に直結
- 記事の見た目・可読性に大きく影響
- スクリプトで自動変換を推奨

| ショートコード | 対応内容 |
|--------------|---------|
| `st-card` | SWELLブログカードに1:1変換 |
| `st-mybox` | SWELLキャプション付きブロックで完全再現（配色・アイコン含む） |
| `st-midasibox` | SWELL見出し付きボックスで再現 |
| `st-mybutton` | SWELLボタンブロックで完全再現（グラデーション・リンク設定） |
| `st-kaiwa1/5` | SWELLふきだしブロックでキャラクター設定 |

---

### 🟡 優先度B：最低限崩れなければOK（合計64回・11.8%）

**機能は残すが、完全再現は不要**

- 記事に影響はあるが、代替案で許容範囲
- 一部手動調整も可

| ショートコード | 対応内容 |
|--------------|---------|
| `caption` | WordPress標準機能で自動変換（追加作業不要） |
| `star` | シンプルなHTML+CSSで代替 |
| `st-minihukidashi` | SWELLふきだしブロックのミニサイズで代替 |
| `st-kaiwa2/3/7` | 手動変換でOK（使用回数1回） |

---

### ⚪ 優先度C：削除してもいい（合計73回・13.5%）

**変換不要・低影響**

- 誤検出（サービス名等）
- 使用頻度が極端に低い

| ショートコード | 対応内容 |
|--------------|---------|
| `With`, `Omiai`, `Google` 等 | テキストなので変換不要 |
| `st-mcbutton` | 手動変換または削除（3回のみ） |

---

## 🔄 具体的な変換ルール

### 1. st-card（190回）→ SWELLブログカードブロック

**変換前（Affinger4）:**
```
[st-card myclass="" id=529 label="" pc_height="" name="" bgcolor="" color="" fontawesome="" readmore="on"]
```

**変換後（SWELL）:**
```html
<!-- wp:swell/blog-card {"postId":529} /-->
```

**変換ロジック:**
```javascript
// id属性を抽出してpostIdに設定
const postId = shortcode.match(/id=(\d+)/)?.[1];
return `<!-- wp:swell/blog-card {"postId":${postId}} /-->`;
```

**注意点:**
- `readmore`、`bgcolor`等の属性は無視（SWELLでテーマ設定から一括管理）
- 外部リンクの場合は`<!-- wp:swell/external-link -->`を使用

---

### 2. st-mybox（116回）→ SWELLキャプション付きブロック

**変換前（Affinger4）:**
```
[st-mybox title="注意ポイント" fontawesome="fa-exclamation-circle" color="#ef5350" bordercolor="#ef9a9a" bgcolor="#ffebee" borderwidth="2" borderradius="5" titleweight="bold"]
コンテンツ
[/st-mybox]
```

**変換後（SWELL）:**
```html
<!-- wp:swell/box {"style":"alert","title":"注意ポイント","icon":"fa-exclamation-circle"} -->
<div class="wp-block-swell-box swell-block-box is-style-alert">
  <div class="swell-block-box__title">
    <span class="swell-block-box__icon"><i class="fa fa-exclamation-circle"></i></span>
    注意ポイント
  </div>
  <div class="swell-block-box__body">
    コンテンツ
  </div>
</div>
<!-- /wp:swell/box -->
```

**変換ロジック:**
```javascript
// タイトル・アイコン・配色をマッピング
const colorMap = {
  '#ef5350': 'alert',    // 赤 → アラートスタイル
  '#FFD54F': 'point',    // 黄色 → ポイントスタイル
  '#4FC3F7': 'info',     // 青 → インフォスタイル
};

const style = colorMap[attributes.color] || 'default';
```

**注意点:**
- SWELLには4つのプリセットスタイルがある（alert/point/info/success）
- カスタム配色はCSSで追加実装が必要

---

### 3. st-midasibox（70回）→ SWELL見出し付きボックス

**変換前（Affinger4）:**
```
[st-midasibox title="ポイント" fontawesome="" bordercolor="" color="" bgcolor="" borderwidth="" borderradius="" titleweight="bold"]
コンテンツ
[/st-midasibox]
```

**変換後（SWELL）:**
```html
<!-- wp:swell/box {"style":"solid","title":"ポイント"} -->
<div class="wp-block-swell-box swell-block-box is-style-solid">
  <div class="swell-block-box__title">ポイント</div>
  <div class="swell-block-box__body">
    コンテンツ
  </div>
</div>
<!-- /wp:swell/box -->
```

**変換ロジック:**
```javascript
// シンプルな枠線スタイル（solid）を適用
return {
  blockName: 'swell/box',
  attrs: {
    style: 'solid',
    title: attributes.title
  }
};
```

---

### 4. st-mybutton（28回）→ SWELLボタンブロック

**変換前（Affinger4）:**
```
[st-mybutton url="https://example.com" title="無料でダウンロードしてみる" color="#fff" bgcolor="#F48FB1" bgcolor_top="#F06292" bordercolor="#E91E63" borderwidth="1" borderradius="5" fontweight="bold" target="_blank"]
```

**変換後（SWELL）:**
```html
<!-- wp:swell/button {"url":"https://example.com","text":"無料でダウンロードしてみる","target":"_blank","backgroundColor":"#F48FB1","textColor":"#fff","borderRadius":"5"} /-->
```

**変換ロジック:**
```javascript
return {
  blockName: 'swell/button',
  attrs: {
    url: attributes.url,
    text: attributes.title,
    target: attributes.target || '_self',
    backgroundColor: attributes.bgcolor,
    textColor: attributes.color,
    borderRadius: attributes.borderradius
  }
};
```

**注意点:**
- `bgcolor_top`（グラデーション）はSWELLカスタマイザーで設定
- アフィリエイトリンクは`rel="nofollow"`を追加推奨

---

### 5. caption（24回）→ 標準画像ブロック

**変換前（WordPress標準）:**
```
[caption id="attachment_584" align="aligncenter" width="512"]
<img src="..." alt="..." />
キャプション文
[/caption]
```

**変換後（Gutenberg標準）:**
```html
<!-- wp:image {"id":584,"align":"center","width":512} -->
<figure class="wp-block-image aligncenter size-full is-resized">
  <img src="..." alt="..." class="wp-image-584" width="512"/>
  <figcaption>キャプション文</figcaption>
</figure>
<!-- /wp:image -->
```

**変換ロジック:**
- WordPress 5.0以降は自動変換（プラグイン不要）
- 手動変換は不要

---

### 6. st-minihukidashi（15回）→ SWELLふきだしブロック

**変換前（Affinger4）:**
```
[st-minihukidashi fontawesome="fa-exclamation-circle" fontsize="90" fontweight="bold" bgcolor="#ef5350" color="#fff" margin="0 0 0 0"]
ここに注意！
[/st-minihukidashi]
```

**変換後（SWELL）:**
```html
<!-- wp:swell/balloon {"balloonType":"thinking","avatarSize":"small","backgroundColor":"#ef5350","textColor":"#fff"} -->
<div class="wp-block-swell-balloon">
  <div class="swell-balloon-icon">
    <i class="fa fa-exclamation-circle"></i>
  </div>
  <div class="swell-balloon-content">ここに注意！</div>
</div>
<!-- /wp:swell/balloon -->
```

**変換ロジック:**
```javascript
return {
  blockName: 'swell/balloon',
  attrs: {
    balloonType: 'thinking', // ミニ吹き出し風
    avatarSize: 'small',
    backgroundColor: attributes.bgcolor,
    textColor: attributes.color
  }
};
```

---

### 7. st-kaiwa1/st-kaiwa5（計20回）→ SWELLふきだしブロック

**変換前（Affinger4）:**
```
[st-kaiwa1 r]
キャラクターのセリフ
[/st-kaiwa1]
```

**変換後（SWELL）:**
```html
<!-- wp:swell/balloon {"align":"right","avatarId":1,"name":"キャラクター1"} -->
<div class="wp-block-swell-balloon is-right">
  <div class="swell-balloon-avatar">
    <img src="character1.png" alt="キャラクター1" />
  </div>
  <div class="swell-balloon-content">
    キャラクターのセリフ
  </div>
</div>
<!-- /wp:swell/balloon -->
```

**変換ロジック:**
```javascript
// st-kaiwa1 → キャラクター1, st-kaiwa5 → キャラクター5
const characterMap = {
  'st-kaiwa1': { avatarId: 1, name: 'キャラクター1' },
  'st-kaiwa2': { avatarId: 2, name: 'キャラクター2' },
  'st-kaiwa3': { avatarId: 3, name: 'キャラクター3' },
  'st-kaiwa5': { avatarId: 5, name: 'キャラクター5' },
  'st-kaiwa7': { avatarId: 7, name: 'キャラクター7' },
};

const character = characterMap[shortcodeName];
const align = attributes.r ? 'right' : 'left';

return {
  blockName: 'swell/balloon',
  attrs: {
    align,
    avatarId: character.avatarId,
    name: character.name
  }
};
```

**事前準備:**
- SWELLエディター設定 → ふきだし管理で各キャラクターを登録
- アバター画像をメディアライブラリにアップロード

---

### 8. star（24回）→ HTML（カスタムCSS）

**変換前（Affinger4）:**
```
[star 4.5]
```

**変換後（HTML + CSS）:**
```html
<span class="star-rating" data-rating="4.5">
  <span class="stars">★★★★☆</span>
</span>
```

**CSS（functions.phpまたはカスタマイザーに追加）:**
```css
.star-rating {
  display: inline-block;
  color: #FFD700;
  font-size: 1.2em;
}
.star-rating .stars {
  letter-spacing: 2px;
}
```

**変換ロジック:**
```javascript
const rating = parseFloat(attributes[0]);
const fullStars = Math.floor(rating);
const hasHalfStar = rating % 1 >= 0.5;
const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

const stars = '★'.repeat(fullStars) + (hasHalfStar ? '⯨' : '') + '☆'.repeat(emptyStars);

return `<span class="star-rating">${stars}</span>`;
```

---

## 🛠️ 実装方法

### 方法1：プラグインを使用（推奨）

**おすすめプラグイン:**
- **[Shortcode Block](https://ja.wordpress.org/plugins/shortcodes-blocks/)** - ショートコードをブロックとして編集可能に
- **[Reusable Blocks Extended](https://ja.wordpress.org/plugins/reusable-blocks-extended/)** - 一括置換機能あり

### 方法2：SQL一括置換（上級者向け）

**注意:** 必ずバックアップを取ってから実行

```sql
-- st-card → SWELLブログカード
UPDATE wp_posts
SET post_content = REGEXP_REPLACE(
  post_content,
  '\\[st-card[^\\]]*id=([0-9]+)[^\\]]*\\]',
  '<!-- wp:swell/blog-card {"postId":$1} /-->'
)
WHERE post_type = 'post';

-- st-mybox → SWELLボックス（注意スタイル）
UPDATE wp_posts
SET post_content = REGEXP_REPLACE(
  post_content,
  '\\[st-mybox title="([^"]*)"[^\\]]*color="#ef5350"[^\\]]*\\]([^\\[]*)\\[/st-mybox\\]',
  '<!-- wp:swell/box {"style":"alert","title":"$1"} --><div class="wp-block-swell-box is-style-alert"><div class="swell-block-box__title">$1</div><div class="swell-block-box__body">$2</div></div><!-- /wp:swell/box -->'
)
WHERE post_type = 'post';
```

### 方法3：PHPスクリプト（最も柔軟）

次のセクションで詳細なスクリプトを提供します。

---

## 📊 変換優先度サマリー

| 優先度 | ショートコード数 | 使用回数 | 対応方針 |
|--------|-----------------|---------|---------|
| **A（必須）** | 6種類 | 404回 (74.7%) | スクリプトで自動変換 |
| **B（推奨）** | 6種類 | 64回 (11.8%) | 半自動 or 手動変換 |
| **C（任意）** | 23種類 | 73回 (13.5%) | 変換不要 or 削除 |

---

## ✅ 移行チェックリスト

### 事前準備
- [ ] 全記事・データベースの完全バックアップ
- [ ] ローカル環境またはステージング環境でテスト
- [ ] SWELLテーマの最新版をインストール
- [ ] SWELLふきだしブロックにキャラクター登録

### 変換作業
- [ ] st-card（190回）→ SWELLブログカード
- [ ] st-mybox（116回）→ SWELLキャプション付きブロック
- [ ] st-midasibox（70回）→ SWELL見出し付きボックス
- [ ] st-mybutton（28回）→ SWELLボタン
- [ ] st-kaiwa1/5（20回）→ SWELLふきだし
- [ ] caption（24回）→ 標準画像ブロック（自動変換確認）
- [ ] star（24回）→ カスタムHTML
- [ ] st-minihukidashi（15回）→ SWELLふきだし

### 確認作業
- [ ] 記事のビジュアル確認（最低10記事サンプリング）
- [ ] モバイル表示確認
- [ ] リンク動作確認（特にボタン・カード）
- [ ] 画像・キャプション表示確認
- [ ] 吹き出しキャラクター表示確認
- [ ] SEO要素確認（meta description、OGP等）
- [ ] ページ速度確認（Lighthouse/PageSpeed Insights）

### 本番移行
- [ ] 最終バックアップ
- [ ] 本番環境で変換実行
- [ ] 全記事目視確認（またはスクリプトで自動チェック）
- [ ] Google Search Consoleでエラー確認
- [ ] アナリティクスで離脱率・滞在時間確認

---

## 🚀 次のステップ

1. **変換スクリプト作成** → `SWELL_CONVERTER.php` を生成
2. **テスト実行** → ステージング環境で変換テスト
3. **本番移行** → バックアップ取得後に本番実行

**推定作業時間:**
- スクリプト準備: 2-3時間
- テスト・調整: 3-4時間
- 本番移行: 1-2時間
- **合計: 6-9時間**

---

**作成日**: 2025-12-08
**対象**: Affinger4 → SWELL移行プロジェクト
**記事数**: 86記事 / 541ショートコード
