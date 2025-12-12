# Affinger4 → SWELL 移行プロジェクト

このフォルダには、Affinger4からSWELLへの移行に必要なすべてのファイルが含まれています。

## 📁 ファイル構成

```
affinger-to-swell-migration/
├── README.md                          # このファイル（はじめにお読みください）
├── SHORTCODE_ANALYSIS_REPORT.md       # ショートコード分析レポート
├── CONVERSION_TABLE.md                # 変換ルール早見表（推奨）
├── SWELL_MIGRATION_GUIDE.md           # 詳細な移行ガイド
├── swell_converter.php                # 自動変換スクリプト（実行ファイル）
├── analyze_shortcodes.py              # ショートコード分析スクリプト
└── extract_examples.py                # 使用例抽出スクリプト
```

---

## 🚀 クイックスタート（3ステップ）

### ステップ1：現状を把握する
📄 **SHORTCODE_ANALYSIS_REPORT.md** を読む
- 86記事、541個のショートコードを分析済み
- 使用頻度・優先度が一目でわかる

### ステップ2：変換ルールを確認する
📋 **CONVERSION_TABLE.md** を読む（推奨）
- 各ショートコードのSWELL代替案
- 優先度（A/B/C）と難易度
- 変換パターン例

### ステップ3：変換を実行する
🔧 **swell_converter.php** を実行
- WordPressルートに配置
- ブラウザまたはwp-cliで実行
- DRY_RUN=trueで安全にテスト可能

---

## 📊 変換対象サマリー

| 優先度 | ショートコード数 | 使用回数 | 対応方針 |
|--------|-----------------|---------|---------|
| **A（必須）** | 6種類 | 404回 (74.7%) | スクリプトで自動変換 |
| **B（推奨）** | 6種類 | 64回 (11.8%) | 半自動/手動変換 |
| **C（任意）** | 23種類 | 73回 (13.5%) | 変換不要/削除 |

---

## 🎯 推奨される読む順番

### 初めての方
1. **README.md**（このファイル）
2. **CONVERSION_TABLE.md** ← 変換ルール早見表
3. **swell_converter.php** ← 実行

### 詳しく知りたい方
1. **SHORTCODE_ANALYSIS_REPORT.md** ← 分析結果
2. **SWELL_MIGRATION_GUIDE.md** ← 詳細ガイド
3. **CONVERSION_TABLE.md** ← 変換ルール
4. **swell_converter.php** ← 実行

---

## ⚡ 最速で移行する方法

### 所要時間：約8-13時間

```bash
# 1. バックアップ取得（1時間）
mysqldump -u user -p database > backup.sql
tar -czf wp-content-backup.tar.gz wp-content/

# 2. swell_converter.phpをアップロード（10分）
# WordPressルートディレクトリに配置

# 3. テスト実行（1-2時間）
# ブラウザで https://yourdomain.com/swell_converter.php にアクセス
# DRY_RUN=true で動作確認

# 4. 本番実行（1時間）
# DRY_RUN=false に変更して再実行

# 5. 確認・調整（2-3時間）
# サンプル記事で表示確認

# 6. 完了（残り微調整）
```

---

## 🔴 優先度A：必ず変換すべきショートコード

全体の**74.7%**を占める重要なショートコード：

| # | ショートコード | 使用回数 | SWELL代替 |
|---|---------------|---------|----------|
| 1 | `st-card` | 190回 | SWELLブログカード |
| 2 | `st-mybox` | 116回 | SWELLボックス（装飾） |
| 3 | `st-midasibox` | 70回 | SWELLボックス（見出し） |
| 4 | `st-mybutton` | 28回 | SWELLボタン |
| 5 | `st-kaiwa1/5` | 20回 | SWELLふきだし |

これら5つを変換すれば、**全体の約75%が完了**します。

---

## 🛠️ swell_converter.php の使い方

### 基本的な使用方法

```php
// 1. 設定を確認
define('DRY_RUN', true);  // テスト実行（変更を保存しない）

// 2. 変換対象を指定（オプション）
$POST_TYPES = ['post', 'page'];  // 投稿とページを対象

// 3. 特定のショートコードのみ変換（オプション）
$PRIORITY_FILTER = [];  // 空配列で全変換
// または
$PRIORITY_FILTER = ['st-card', 'st-mybox'];  // 特定のみ
```

### 実行方法

**方法1：ブラウザで実行**
```
1. swell_converter.php をWordPressルートにアップロード
2. https://yourdomain.com/swell_converter.php にアクセス
3. 結果を確認
4. DRY_RUN=false にして本番実行
```

**方法2：WP-CLIで実行**
```bash
cd /path/to/wordpress
wp eval-file swell_converter.php
```

---

## 📋 変換前チェックリスト

### 必須
- [ ] **データベースバックアップ取得**
- [ ] **wp-contentフォルダバックアップ取得**
- [ ] **ステージング環境でテスト実行**
- [ ] **DRY_RUNで動作確認**

### 推奨
- [ ] SWELLテーマインストール済み
- [ ] SWELLふきだしにキャラクター登録済み
- [ ] ロールバック手順の確認
- [ ] 変換前後のスクリーンショット取得

---

## 🎨 追加が必要なカスタムCSS

変換後、以下のCSSを追加してください：

**SWELL → カスタマイザー → 追加CSS** に貼り付け：

```css
/* 星評価 */
.star-rating {
  display: inline-block;
  color: #FFD700;
  font-size: 1.2em;
  letter-spacing: 2px;
}

/* ミニ吹き出し */
.mini-fukidashi {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.9em;
  font-weight: bold;
  margin-right: 8px;
}
.mini-fukidashi i {
  margin-right: 4px;
}
```

---

## 🔧 トラブルシューティング

### Q1: スクリプトが動かない
**A:** PHPのエラーログを確認してください：
```bash
tail -f /var/log/apache2/error.log
# または
tail -f /var/log/php-fpm/error.log
```

### Q2: 変換されたが表示が崩れる
**A:** 以下を確認：
1. SWELLテーマが有効化されているか
2. カスタムCSSが追加されているか
3. キャッシュプラグインをクリアしたか

### Q3: 一部のショートコードが変換されない
**A:** `$PRIORITY_FILTER` の設定を確認：
```php
$PRIORITY_FILTER = [];  // 空にすると全変換
```

### Q4: 本番で実行したいが不安
**A:** 段階的に実行：
```php
// ステップ1: st-cardのみ変換
$PRIORITY_FILTER = ['st-card'];

// ステップ2: st-myboxを追加
$PRIORITY_FILTER = ['st-card', 'st-mybox'];

// ステップ3: 全変換
$PRIORITY_FILTER = [];
```

---

## 📞 サポート

### 問題が発生した場合

1. **CONVERSION_TABLE.md** で変換ルールを確認
2. **SWELL_MIGRATION_GUIDE.md** で詳細手順を確認
3. バックアップから復元

### 追加の変換ルールが必要な場合

`analyze_shortcodes.py` を再実行して、新しいショートコードを検出：

```bash
python3 analyze_shortcodes.py
```

---

## 📊 実行ログの見方

スクリプト実行後、以下の情報が表示されます：

```
変換対象投稿数: 35 / 86
総置換数: 428

[ID:123] st-card x 5回変換
[ID:123] st-mybox x 3回変換
[ID:456] st-card x 2回変換
...
```

- **変換対象投稿数**: ショートコードが含まれていた記事数
- **総置換数**: 全ショートコードの変換回数
- **詳細ログ**: 各記事でどのショートコードが何回変換されたか

---

## ⏱️ 作業時間の目安

| タスク | 時間 | 難易度 |
|--------|------|--------|
| バックアップ取得 | 0.5-1時間 | ⭐ 簡単 |
| ファイル確認 | 0.5時間 | ⭐ 簡単 |
| テスト実行 | 1-2時間 | ⭐⭐ 普通 |
| 本番実行 | 0.5-1時間 | ⭐⭐ 普通 |
| 確認・調整 | 2-3時間 | ⭐⭐ 普通 |
| カスタムCSS追加 | 0.5時間 | ⭐ 簡単 |
| 最終チェック | 1-2時間 | ⭐⭐ 普通 |
| **合計** | **6-11時間** | - |

---

## ✅ 完了確認チェックリスト

### 変換完了後
- [ ] 全記事でショートコードが変換されている
- [ ] ビジュアルが崩れていない
- [ ] リンク・ボタンが正しく動作する
- [ ] モバイル表示が正常
- [ ] ページ速度が維持されている

### SEO確認
- [ ] Google Search Consoleでエラーなし
- [ ] meta descriptionが保持されている
- [ ] OGP画像が表示される
- [ ] 内部リンクが正しく動作

### 最終チェック
- [ ] アナリティクスで離脱率を確認
- [ ] 直帰率が大きく変化していない
- [ ] ユーザーからのフィードバック確認

---

## 🎉 移行完了後

おめでとうございます！移行が完了しました。

### 次にやること
1. **バックアップファイルを安全な場所に保管**
2. **swell_converter.phpを削除**（セキュリティのため）
3. **パフォーマンス最適化**（キャッシュ・画像圧縮等）
4. **ユーザーフィードバック収集**

---

**作成日**: 2025-12-08
**対象記事**: 86記事
**対象ショートコード**: 541個
**バージョン**: 1.0.0
