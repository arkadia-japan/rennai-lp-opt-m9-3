# Affinger4 → SWELL 変換ルール早見表

## 📊 優先度別変換ルール

### 🔴 優先度A：必須で綺麗に変換（404回 / 74.7%）

| Affinger4 | 回数 | SWELL代替 | 変換方法 | 難易度 | 備考 |
|-----------|------|----------|---------|--------|------|
| `st-card` | 190 | SWELLブログカード | `<!-- wp:swell/blog-card {"postId":ID} /-->` | ⭐ 簡単 | id属性を抽出するだけ |
| `st-mybox` | 116 | SWELLボックス | `<!-- wp:swell/box {"style":"alert","title":"..."} -->` | ⭐⭐ 普通 | 配色→スタイルマッピング必要 |
| `st-midasibox` | 70 | SWELLボックス（solid） | `<!-- wp:swell/box {"style":"solid","title":"..."} -->` | ⭐ 簡単 | タイトルのみ抽出 |
| `st-mybutton` | 28 | SWELLボタン | `<!-- wp:swell/button {"url":"...","text":"..."} /-->` | ⭐⭐ 普通 | URL・テキスト・色を抽出 |
| `st-kaiwa1` | 11 | SWELLふきだし | `<!-- wp:swell/balloon {"align":"right","avatarId":1} -->` | ⭐⭐⭐ やや難 | キャラクター事前登録必要 |
| `st-kaiwa5` | 9 | SWELLふきだし | `<!-- wp:swell/balloon {"align":"right","avatarId":5} -->` | ⭐⭐⭐ やや難 | 同上 |

---

### 🟡 優先度B：最低限崩れなければOK（64回 / 11.8%）

| Affinger4 | 回数 | SWELL代替 | 変換方法 | 難易度 | 備考 |
|-----------|------|----------|---------|--------|------|
| `caption` | 24 | 標準画像ブロック | WordPress自動変換 | ⭐ 簡単 | 変換不要 |
| `star` | 24 | カスタムHTML | `<span class="star-rating">★★★★☆</span>` | ⭐⭐ 普通 | CSS追加必要 |
| `st-minihukidashi` | 15 | SWELLふきだし（小） | `<!-- wp:swell/balloon {"avatarSize":"small"} -->` | ⭐⭐ 普通 | ミニサイズ設定 |
| `st-kaiwa2` | 1 | SWELLふきだし | 手動変換 | ⭐ 簡単 | 低頻度のため手動でOK |
| `st-kaiwa3` | 1 | SWELLふきだし | 手動変換 | ⭐ 簡単 | 同上 |
| `st-kaiwa7` | 1 | SWELLふきだし | 手動変換 | ⭐ 簡単 | 同上 |

---

### ⚪ 優先度C：変換不要または削除（73回 / 13.5%）

| Affinger4 | 回数 | SWELL代替 | 変換方法 | 備考 |
|-----------|------|----------|---------|------|
| `st-mcbutton` | 3 | SWELLボタン（複数） | 手動変換 or 削除 | 使用頻度極小 |
| `With` | 8 | **変換不要** | そのまま | サービス名（誤検出） |
| `Omiai` | 7 | **変換不要** | そのまま | サービス名（誤検出） |
| `Google` | 6 | **変換不要** | そのまま | サービス名（誤検出） |
| `Rooters` | 4 | **変換不要** | そのまま | サービス名（誤検出） |
| その他 | 45 | **変換不要** | そのまま | 日付・人名等の誤検出 |

---

## 🎨 配色マッピング（st-mybox → SWELLボックス）

| Affinger配色 | 用途 | SWELLスタイル | スタイル名 |
|-------------|------|-------------|----------|
| `color="#ef5350"` | 注意・警告 | `"style":"alert"` | アラート（赤） |
| `color="#FFD54F"` | ポイント・重要 | `"style":"point"` | ポイント（黄） |
| `color="#4FC3F7"` | 情報・ヒント | `"style":"info"` | インフォ（青） |
| `color="#66BB6A"` | 成功・完了 | `"style":"success"` | サクセス（緑） |
| その他 | カスタム | `"style":"default"` | デフォルト（グレー） |

---

## 🔄 変換パターン例

### パターン1：st-card（最頻出）

```
【変換前】
[st-card myclass="" id=529 label="" pc_height="" name="" bgcolor="" color="" fontawesome="" readmore="on"]

【変換後】
<!-- wp:swell/blog-card {"postId":529} /-->
```

**正規表現:**
```regex
\[st-card[^\]]*id=(\d+)[^\]]*\]
↓
<!-- wp:swell/blog-card {"postId":$1} /-->
```

---

### パターン2：st-mybox（注意ポイント）

```
【変換前】
[st-mybox title="注意ポイント" fontawesome="fa-exclamation-circle" color="#ef5350" bordercolor="#ef9a9a" bgcolor="#ffebee" borderwidth="2" borderradius="5" titleweight="bold"]
ここに注意してください
[/st-mybox]

【変換後】
<!-- wp:swell/box {"style":"alert","title":"注意ポイント","icon":"fa-exclamation-circle"} -->
<div class="wp-block-swell-box is-style-alert">
  <div class="swell-block-box__title">
    <i class="fa fa-exclamation-circle"></i> 注意ポイント
  </div>
  <div class="swell-block-box__body">
    ここに注意してください
  </div>
</div>
<!-- /wp:swell/box -->
```

---

### パターン3：st-mybutton（アフィリエイトボタン）

```
【変換前】
[st-mybutton url="https://example.com" title="無料登録はこちら" color="#fff" bgcolor="#F48FB1" target="_blank"]

【変換後】
<!-- wp:swell/button {"url":"https://example.com","text":"無料登録はこちら","target":"_blank","backgroundColor":"#F48FB1","textColor":"#fff"} /-->
```

---

### パターン4：st-kaiwa1（会話吹き出し）

```
【変換前】
[st-kaiwa1 r]
これはどういう意味ですか?
[/st-kaiwa1]

【変換後】
<!-- wp:swell/balloon {"align":"right","avatarId":1,"name":"キャラクター1"} -->
<div class="wp-block-swell-balloon is-right">
  <div class="swell-balloon-avatar">
    <img src="/wp-content/uploads/character1.png" alt="キャラクター1" />
  </div>
  <div class="swell-balloon-content">
    これはどういう意味ですか?
  </div>
</div>
<!-- /wp:swell/balloon -->
```

---

## 🛠️ 変換ツール比較

| 方法 | 難易度 | 時間 | メリット | デメリット |
|------|--------|------|---------|----------|
| **プラグイン** | ⭐ 簡単 | 1-2時間 | GUIで直感的 | 細かい調整不可 |
| **SQL一括置換** | ⭐⭐⭐ 難しい | 2-3時間 | 高速・一括処理 | リスク高・ロールバック困難 |
| **PHPスクリプト** | ⭐⭐ 普通 | 3-5時間 | 柔軟・段階実行可能 | スクリプト作成必要 |
| **手動変換** | ⭐ 簡単 | 20-30時間 | 確実・リスクなし | 時間がかかる |

**推奨:** PHPスクリプト（段階的に変換、ロールバック可能）

---

## 📋 作業手順（推奨）

### ステップ1：事前準備
1. ✅ バックアップ取得（DB + ファイル）
2. ✅ ステージング環境構築
3. ✅ SWELLテーマインストール
4. ✅ キャラクター画像登録（ふきだし用）

### ステップ2：優先度A変換（スクリプト）
1. ✅ `st-card` → SWELLブログカード（190回）
2. ✅ `st-mybox` → SWELLボックス（116回）
3. ✅ `st-midasibox` → SWELL見出しボックス（70回）
4. ✅ `st-mybutton` → SWELLボタン（28回）
5. ✅ `st-kaiwa1/5` → SWELLふきだし（20回）

### ステップ3：優先度B変換（半自動/手動）
1. ✅ `caption` → 自動変換確認（24回）
2. ✅ `star` → HTML+CSS（24回）
3. ✅ `st-minihukidashi` → SWELLふきだし（15回）

### ステップ4：確認・調整
1. ✅ サンプル記事確認（10記事）
2. ✅ モバイル表示確認
3. ✅ リンク・ボタン動作確認
4. ✅ SEO要素確認

### ステップ5：本番移行
1. ✅ 最終バックアップ
2. ✅ 本番環境で変換実行
3. ✅ 全記事目視確認
4. ✅ Search Console確認

---

## ⏱️ 作業時間見積もり

| フェーズ | 時間 | 備考 |
|---------|------|------|
| 事前準備 | 1-2時間 | バックアップ・環境構築 |
| スクリプト作成 | 2-3時間 | PHPスクリプト作成・テスト |
| 優先度A変換 | 1-2時間 | スクリプト実行 |
| 優先度B変換 | 1-2時間 | 半自動/手動変換 |
| 確認・調整 | 2-3時間 | ビジュアル確認・微調整 |
| 本番移行 | 1時間 | 本番実行・最終確認 |
| **合計** | **8-13時間** | 86記事の場合 |

---

## 🚨 注意事項

### リスクが高い変換
- ❌ SQL直接編集（ロールバック困難）
- ❌ 本番環境での直接変換（バックアップなし）
- ❌ 一括置換後の確認なし

### 必ずやること
- ✅ **バックアップ取得**（DB + wp-content）
- ✅ **ステージング環境でテスト**
- ✅ **段階的に変換**（一気に全部変換しない）
- ✅ **変換前後のスクリーンショット保存**
- ✅ **ロールバック手順の確認**

---

**作成日:** 2025-12-08
**対象記事数:** 86記事
**総ショートコード数:** 541回
**対応必須ショートコード:** 6種類（404回）
