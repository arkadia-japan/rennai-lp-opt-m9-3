# ファイルガイド

このフォルダ内の各ファイルの役割と読む順番を説明します。

---

## 📁 フォルダ構成（7ファイル）

```
affinger-to-swell-migration/
│
├── README.md ⭐⭐⭐
│   └─ はじめにお読みください（クイックスタートガイド）
│
├── FILE_GUIDE.md ⭐⭐
│   └─ このファイル（各ファイルの説明）
│
├── CONVERSION_TABLE.md ⭐⭐⭐ 【推奨】
│   └─ 変換ルール早見表（優先度・変換方法・パターン例）
│
├── SHORTCODE_ANALYSIS_REPORT.md ⭐⭐
│   └─ ショートコード分析レポート（使用頻度・統計）
│
├── SWELL_MIGRATION_GUIDE.md ⭐⭐
│   └─ 詳細な移行ガイド（変換ロジック・チェックリスト）
│
├── swell_converter.php ⭐⭐⭐ 【実行ファイル】
│   └─ 自動変換スクリプト（PHPで実行）
│
├── analyze_shortcodes.py
│   └─ ショートコード分析スクリプト（Python・参考用）
│
└── extract_examples.py
    └─ 使用例抽出スクリプト（Python・参考用）
```

---

## 🎯 推奨される読む順番

### 🚀 最速で移行したい方（3ステップ）

1. **README.md**（5分）
   - 全体像を把握
   - クイックスタート確認

2. **CONVERSION_TABLE.md**（10分） ← 最重要
   - 各ショートコードの変換方法
   - 優先度A/B/Cの確認
   - 変換パターン例を確認

3. **swell_converter.php を実行**（1-2時間）
   - DRY_RUN=true でテスト
   - 結果確認後、本番実行

---

### 📚 詳しく知りたい方（じっくり学習）

1. **README.md**（5分）
   - プロジェクト概要

2. **FILE_GUIDE.md**（このファイル、3分）
   - ファイル構成確認

3. **SHORTCODE_ANALYSIS_REPORT.md**（10分）
   - 現状分析を理解
   - 使用頻度・カテゴリ別統計

4. **SWELL_MIGRATION_GUIDE.md**（20分）
   - 詳細な変換ロジック
   - 各ショートコードの変換方法
   - チェックリスト

5. **CONVERSION_TABLE.md**（10分）
   - 変換ルール早見表で総復習

6. **swell_converter.php を実行**（1-2時間）
   - 理解した上で実行

---

## 📄 各ファイル詳細

### 1. README.md ⭐⭐⭐【必読】

**目的:** プロジェクト全体のクイックスタートガイド

**内容:**
- フォルダ構成
- 3ステップで移行する方法
- 変換対象サマリー
- 優先度A（必須）ショートコード一覧
- swell_converter.phpの使い方
- トラブルシューティング
- 作業時間の目安

**こんな人におすすめ:**
- 初めて移行する方
- 全体像を把握したい方
- 最速で移行したい方

**所要時間:** 5分

---

### 2. FILE_GUIDE.md ⭐⭐

**目的:** 各ファイルの役割と読む順番の説明

**内容:**
- ファイル構成の説明
- 推奨される読む順番（最速 / じっくり）
- 各ファイルの詳細解説

**こんな人におすすめ:**
- どのファイルから読めばいいか迷っている方
- 各ファイルの役割を知りたい方

**所要時間:** 3分

---

### 3. CONVERSION_TABLE.md ⭐⭐⭐【最重要・推奨】

**目的:** 変換ルールの早見表

**内容:**
- 優先度別（A/B/C）変換ルール表
- 各ショートコードの難易度
- SWELL代替案
- 配色マッピング（st-mybox）
- 変換パターン例（変換前/変換後）
- 変換ツール比較
- 作業手順（ステップバイステップ）
- 作業時間見積もり
- 注意事項

**こんな人におすすめ:**
- 実際に変換作業をする方（必読）
- どのショートコードをどう変換するか知りたい方
- 変換パターンを見たい方

**所要時間:** 10分

**🔍 特に重要なセクション:**
- 優先度A変換表（6種類・404回）
- 変換パターン例
- 作業手順

---

### 4. SHORTCODE_ANALYSIS_REPORT.md ⭐⭐

**目的:** 現状のショートコード使用状況を把握

**内容:**
- 分析サマリー（86記事・541ショートコード）
- 使用頻度ランキング TOP 15
- カテゴリ別使用状況
- 主要ショートコード詳細（属性・見た目）
- 誤検出の注意事項
- 移行時の優先度

**こんな人におすすめ:**
- 現状を詳しく知りたい方
- 各ショートコードの属性・用途を知りたい方
- データに基づいて判断したい方

**所要時間:** 10分

**🔍 特に重要なセクション:**
- 使用頻度ランキング
- カテゴリ別使用状況（35.1%がカード表示）

---

### 5. SWELL_MIGRATION_GUIDE.md ⭐⭐

**目的:** 詳細な移行手順とロジック解説

**内容:**
- ショートコード変換ルール一覧表
- 優先度別の対応方針（A/B/C）
- 具体的な変換ルール（7パターン詳細）
  - st-card（190回）
  - st-mybox（116回）
  - st-midasibox（70回）
  - st-mybutton（28回）
  - caption（24回）
  - st-minihukidashi（15回）
  - st-kaiwa1/5（20回）
- 実装方法（プラグイン/SQL/PHP）
- 変換優先度サマリー
- 移行チェックリスト
- 次のステップ

**こんな人におすすめ:**
- 変換ロジックを理解したい方
- カスタマイズしたい方
- 技術的な詳細が知りたい方

**所要時間:** 20分

**🔍 特に重要なセクション:**
- 具体的な変換ルール（変換前/変換後のコード）
- 移行チェックリスト

---

### 6. swell_converter.php ⭐⭐⭐【実行ファイル】

**目的:** 実際にショートコードを変換するPHPスクリプト

**内容:**
- 7種類のショートコード変換関数
  - st-card
  - st-mybox
  - st-midasibox
  - st-mybutton
  - st-kaiwa1/2/3/5/7
  - st-minihukidashi
  - star
- DRY RUNモード（安全テスト）
- 優先度フィルタ（特定のショートコードのみ変換）
- ログ出力機能

**こんな人におすすめ:**
- 実際に変換を実行する方（必須）
- 自動変換したい方

**所要時間:** 1-2時間（実行時間）

**🔍 重要な設定:**
```php
define('DRY_RUN', true);  // 最初はtrueでテスト
$PRIORITY_FILTER = [];     // 空で全変換
```

---

### 7. analyze_shortcodes.py（参考用）

**目的:** ショートコード分析（既に実行済み）

**内容:**
- Markdownファイルからショートコード抽出
- 使用頻度カウント
- 用途推測
- カテゴリ別集計

**こんな人におすすめ:**
- 分析を再実行したい方
- 新しい記事を追加した方
- カスタマイズしたい方

**実行方法:**
```bash
python3 analyze_shortcodes.py
```

---

### 8. extract_examples.py（参考用）

**目的:** ショートコードの使用例抽出

**内容:**
- 主要ショートコードの実例抽出
- 属性・パラメータの確認

**こんな人におすすめ:**
- 実際の使用例を見たい方
- パラメータを確認したい方

**実行方法:**
```bash
python3 extract_examples.py
```

---

## 🎯 シーン別おすすめファイル

### シーン1：今すぐ移行を始めたい

```
1. README.md（5分）
2. CONVERSION_TABLE.md（10分）
3. swell_converter.php 実行（1-2時間）
```

---

### シーン2：慎重に理解してから移行したい

```
1. README.md（5分）
2. SHORTCODE_ANALYSIS_REPORT.md（10分）
3. SWELL_MIGRATION_GUIDE.md（20分）
4. CONVERSION_TABLE.md（10分）
5. swell_converter.php 実行（1-2時間）
```

---

### シーン3：特定のショートコードだけ変換したい

```
1. CONVERSION_TABLE.md で変換ルール確認（5分）
2. swell_converter.php の $PRIORITY_FILTER を設定（2分）
3. 実行（30分-1時間）
```

**例：st-cardとst-myboxのみ変換**
```php
$PRIORITY_FILTER = ['st-card', 'st-mybox'];
```

---

### シーン4：変換ルールをカスタマイズしたい

```
1. SWELL_MIGRATION_GUIDE.md で変換ロジック理解（20分）
2. swell_converter.php を編集（1-2時間）
3. テスト実行（30分）
```

---

### シーン5：トラブルが発生した

```
1. README.md のトラブルシューティング（5分）
2. CONVERSION_TABLE.md で正しい変換方法確認（10分）
3. バックアップから復元（必要に応じて）
```

---

## 📊 ファイルサイズ一覧

| ファイル | サイズ | 種類 |
|---------|-------|------|
| README.md | 9.0KB | Markdown（ドキュメント） |
| FILE_GUIDE.md | - | Markdown（ドキュメント） |
| CONVERSION_TABLE.md | 8.4KB | Markdown（ドキュメント） |
| SHORTCODE_ANALYSIS_REPORT.md | 7.2KB | Markdown（ドキュメント） |
| SWELL_MIGRATION_GUIDE.md | 16KB | Markdown（ドキュメント） |
| swell_converter.php | 14KB | PHP（実行スクリプト） |
| analyze_shortcodes.py | 4.9KB | Python（分析スクリプト） |
| extract_examples.py | 2.9KB | Python（抽出スクリプト） |

**合計:** 約62KB（軽量！）

---

## ✅ まとめ

### 最速で移行する方（最小限）
✅ README.md → CONVERSION_TABLE.md → swell_converter.php

### じっくり理解する方（推奨）
✅ README.md → SHORTCODE_ANALYSIS_REPORT.md → SWELL_MIGRATION_GUIDE.md → CONVERSION_TABLE.md → swell_converter.php

### 迷ったら
👉 **CONVERSION_TABLE.md** を読んでください（変換ルールが一番わかりやすい）

---

**作成日:** 2025-12-08
**バージョン:** 1.0.0
