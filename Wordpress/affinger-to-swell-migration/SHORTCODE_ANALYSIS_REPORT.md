# Affinger4 ショートコード分析レポート

## 📊 分析サマリー

- **分析ファイル数**: 86ファイル
- **ショートコード総使用回数**: 541回
- **ユニークなショートコード種類**: 35種類

---

## 🏆 使用頻度ランキング TOP 15

| 順位 | ショートコード | 使用回数 | 推測用途・見た目 |
|------|---------------|----------|-----------------|
| 1 | `st-card` | 190回 | **カード** - 他記事へのリンクカード表示 |
| 2 | `st-mybox` | 116回 | **マイボックス** - カラフルな装飾ボックス（注意・ポイント等） |
| 3 | `st-midasibox` | 70回 | **見出しボックス** - 見出し付きコンテンツボックス |
| 4 | `st-mybutton` | 28回 | **マイボタン** - アフィリエイトリンク等のボタン |
| 5 | `caption` | 24回 | **画像キャプション** - WordPress標準の画像説明 |
| 6 | `star` | 24回 | **星評価** - おそらく評価表示（要確認） |
| 7 | `st-minihukidashi` | 15回 | **ミニ吹き出し** - 小さな見出し吹き出し |
| 8 | `st-kaiwa1` | 11回 | **吹き出し1** - キャラクター会話吹き出し（右側） |
| 9 | `st-kaiwa5` | 9回 | **吹き出し5** - キャラクター会話吹き出し（右側） |
| 10 | `With` | 8回 | マッチングアプリ名（誤検出の可能性） |
| 11 | `Omiai` | 7回 | マッチングアプリ名（誤検出の可能性） |
| 12 | `Google` | 6回 | サービス名（誤検出の可能性） |
| 13 | `table` | 4回 | テーブル要素 |
| 14 | `Rooters` | 4回 | サービス名（誤検出の可能性） |
| 15 | `st-mcbutton` | 3回 | **マルチカラーボタン** - 複数ボタン配置 |

---

## 📁 カテゴリ別使用状況

| カテゴリ | 使用回数 | 割合 |
|----------|----------|------|
| カード（内部リンク） | 190回 | 35.1% |
| マイボックス（装飾ボックス） | 116回 | 21.4% |
| 見出しボックス | 70回 | 12.9% |
| ボタン類 | 31回 | 5.7% |
| 吹き出し・会話 | 23回 | 4.3% |
| 画像キャプション | 24回 | 4.4% |
| その他 | 87回 | 16.1% |

---

## 🔍 主要ショートコード詳細

### 1. st-card（190回使用）
**用途**: 内部記事へのリンクカード
**見た目**: カード型のリンク表示、アイキャッチ画像・タイトル・抜粋を表示

```
[st-card myclass="" id=529 label="" pc_height="" name="" bgcolor="" color="" fontawesome="" readmore="on"]
```

**属性**:
- `id`: 記事ID
- `readmore`: 続きを読むボタンの表示/非表示
- `bgcolor`, `color`: 背景色・文字色
- `fontawesome`: アイコン指定

---

### 2. st-mybox（116回使用）
**用途**: 注意・ポイント等の装飾ボックス
**見た目**: タイトル付き、枠線・背景色・アイコン付きボックス

```
[st-mybox title="注意ポイント" fontawesome="fa-exclamation-circle" color="#ef5350" bordercolor="#ef9a9a" bgcolor="#ffebee" borderwidth="2" borderradius="5" titleweight="bold"]
コンテンツ
[/st-mybox]
```

**属性**:
- `title`: ボックスのタイトル
- `fontawesome`: Font Awesomeアイコン
- `color`, `bordercolor`, `bgcolor`: 配色
- `borderwidth`, `borderradius`: 枠線の太さ・角丸

**バリエーション**:
- 注意ポイント（赤系）
- ポイント（黄色系）
- その他カスタム配色

---

### 3. st-midasibox（70回使用）
**用途**: シンプルな見出しボックス
**見た目**: タイトル付きのシンプルなコンテンツボックス

```
[st-midasibox title="ポイント" fontawesome="" bordercolor="" color="" bgcolor="" borderwidth="" borderradius="" titleweight="bold"]
コンテンツ
[/st-midasibox]
```

---

### 4. st-mybutton（28回使用）
**用途**: アフィリエイトリンク等のボタン
**見た目**: グラデーション背景のボタン

```
[st-mybutton url="https://..." title="マッチングアプリwithを無料でダウンロードしてみる" color="#fff" bgcolor="#F48FB1" bgcolor_top="#..." bordercolor="#..." borderwidth="1" borderradius="5" fontsize="" fontweight="bold" target="_blank"]
```

**属性**:
- `url`: リンク先URL
- `title`: ボタンテキスト
- `bgcolor`, `bgcolor_top`: グラデーション背景色
- `target`: リンクターゲット（`_blank`で別タブ）

---

### 5. caption（24回使用）
**用途**: WordPress標準の画像キャプション
**見た目**: 画像の下に説明文を表示

```
[caption id="attachment_584" align="aligncenter" width="512"]
<img>タグ キャプション文
[/caption]
```

---

### 6. st-minihukidashi（15回使用）
**用途**: ミニ吹き出し（セクション見出し等）
**見た目**: 小さな吹き出し型の強調見出し

```
[st-minihukidashi fontawesome="fa-exclamation-circle" fontsize="90" fontweight="bold" bgcolor="#ef5350" color="#fff" margin="0 0 0 0"]
ここに注意！
[/st-minihukidashi]
```

---

### 7. st-kaiwa1 / st-kaiwa5（計20回使用）
**用途**: キャラクター会話吹き出し
**見た目**: アバター画像付き吹き出し（会話形式）

```
[st-kaiwa1 r]
キャラクターのセリフ
[/st-kaiwa1]
```

**属性**:
- `r`: 右寄せ（省略時は左寄せ）
- `st-kaiwa1`, `st-kaiwa5`: 異なるキャラクターを表示

---

## ⚠️ 注意事項（誤検出の可能性）

以下は本来のショートコードではなく、記事内の文字列が誤検出された可能性があります：

- `With`, `Omiai`, `Google`, `Rooters`, `Tinder`, `Tantan` - マッチングアプリ名・サービス名
- `April`, `November`, `June`, `Maya` - 日付・人名
- `table`, `aside` - HTML要素

これらは記事内で `[サービス名]` のように角括弧付きで記載されていると推測されます。

---

## 🎯 移行時の優先度

### 高優先度（80%以上の使用量）
1. ✅ **st-card** (190回) - 内部リンクカード → Gutenbergブロック化
2. ✅ **st-mybox** (116回) - 装飾ボックス → カスタムブロック化
3. ✅ **st-midasibox** (70回) - 見出しボックス → カスタムブロック化

### 中優先度
4. ✅ **st-mybutton** (28回) - ボタン → Gutenbergボタンブロック化
5. ✅ **st-minihukidashi** (15回) - ミニ吹き出し → カスタムCSS化
6. ✅ **st-kaiwa1/st-kaiwa5** (20回) - 会話吹き出し → カスタムブロック化

### 低優先度
7. **st-mcbutton** (3回) - 使用頻度低、手動変換でも可

---

## 📝 次のステップ

1. **Gutenbergブロック作成**
   - st-card → 内部リンクカードブロック
   - st-mybox → 装飾ボックスブロック（複数プリセット）
   - st-midasibox → 見出しボックスブロック

2. **ショートコード変換スクリプト作成**
   - 既存記事の一括変換
   - バックアップ推奨

3. **スタイリング**
   - CSS移植（色・余白・アイコン等）

4. **テスト**
   - サンプル記事で変換テスト
   - 表示確認

---

**生成日**: 2025-12-08
**分析対象**: `/mnt/c/Users/yoona/99.Project/Wordpress/Wordpress記事`
