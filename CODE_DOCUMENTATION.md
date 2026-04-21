# コード解説ドキュメント

## アプリの概要

**freee 勤怠レポート** は、freee 人事労務 API と連携した Streamlit 製 Web アプリです。  
従業員が自分の月次勤怠データを freee から自動取得し、Excel の作業実施報告書テンプレートにワンクリックで転記・ダウンロードできます。

- 対象: チーム全員（複数ユーザーの同時利用可）
- 動作環境: ローカル実行 または Streamlit Community Cloud

---

## ファイル構成

```
freee-/
├── app.py               # メインアプリ（認証・API・Excel生成・UI制御）
├── ui.py                # UI コンポーネント（SVG・HTML テンプレート）
├── styles.css           # スタイルシートとアニメーション
├── requirements.txt     # Python 依存ライブラリ
├── .devcontainer/
│   └── devcontainer.json  # Dev Container 設定（Python 3.11）
└── YYYY年_MM月_作業実施報告書_SMHC_苗字 名前.xlsx  # Excel テンプレート
```

---

## app.py（メインアプリケーション）

アプリの中核。OAuth 認証・API 通信・Excel 生成・Streamlit 画面制御をすべて担います。

### 設定の読み込み（19〜35行目）

```python
CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
```

次の優先順位で環境変数を読み込みます。

1. `st.secrets`（Streamlit Cloud デプロイ時）
2. `.env`（ローカル開発時）
3. `.env.sample`（フォールバック）

---

### OAuth 認証関連

freee の OAuth 2.0 認可コードフローを実装しています。

| 関数 | 役割 |
|------|------|
| `get_auth_url()` | freee の認可ページ URL を生成する（scope: hr） |
| `get_token_from_code(code)` | 認可コードをアクセストークンに交換する |
| `refresh_token(token)` | リフレッシュトークンで新しいアクセストークンを取得する |
| `get_valid_token()` | 有効なトークンを返す。期限切れなら自動更新する |
| `save_token(token_data)` | トークンをセッション（メモリ）に保存する |
| `load_token()` | セッションからトークンを取得する |

**認証フロー:**

```
① freee 認可ページへアクセス（ブラウザ）
② freee ログイン後、認可コードがリダイレクト URL に付与される
③ URL クエリ ?code= を自動検出、または手動入力
④ アクセストークン・リフレッシュトークンを取得
⑤ st.session_state に保存（ページをまたいで使い回す）
```

---

### ユーザー情報取得

| 関数 | 役割 |
|------|------|
| `get_user_info(access_token)` | freee API `/users/me` でログインユーザーの情報と所属会社一覧を取得する |
| `split_display_name(display_name)` | 表示名を空白で分割して苗字・名前を返す |

---

### 勤怠データ取得・整形

| 関数 | 役割 |
|------|------|
| `get_work_records(year, month, ...)` | 月の各日について freee API を呼び出し、勤怠データを取得する（進捗バー付き） |
| `format_work_data(records)` | 取得したデータを `{日付: {clock_in, clock_out, break}}` の辞書に整形する |
| `_parse_hhmm(s)` | ISO8601 形式や `HH:MM:SS` 形式など複数の時刻文字列を `time` オブジェクトに変換する |
| `_break_total_hours(break_records)` | 休憩レコードの配列から合計休憩時間（小数表記）を計算する |

**`_parse_hhmm` が対応する時刻形式:**
- `2026-04-01T09:00:00.000+09:00`（ISO8601）
- `2026-04-01 09:00:00`（空白区切り）
- `09:00:00`（時刻のみ）

---

### Excel 生成

**`write_to_excel(year, month, data, employee_name, last_name, first_name)`**

Excel テンプレートを開き、勤怠データを転記して BytesIO バッファとして返します。

| セル | 転記内容 |
|------|---------|
| K5 | 苗字 |
| L5 | 名前 |
| K8 | 対象月の初日（例: 2026/04/01） |
| M8〜M38 | 各日の始業時刻 |
| N8〜N38 | 各日の終業時刻 |
| O8〜O38 | 各日の休憩時間（土日かつ未出勤は空欄） |

---

### Streamlit UI 制御（260〜420行目）

画面の描画と操作フローを制御します。

**未認証時の画面:**
1. URL クエリ `?code=` を自動検出して認証を試みる
2. 「freee 認証ページを開く」ボタンを表示
3. 手動コード入力フォームを表示
4. 「認証する」ボタンでトークン取得を実行

**認証済みの画面:**
1. ユーザー情報・所属会社をメトリクス表示
2. 対象会社のセレクトボックス
3. 「データ取得 & Excel 作成」ボタン
4. `st.status` で 4 段階の進行状況を表示
5. Excel ダウンロードボタン

---

## ui.py（UI コンポーネント）

Streamlit の `st.markdown` に渡す HTML 文字列を生成する関数群です。  
SVG アイコン・キャラクターアニメーション・カードレイアウトなどを担います。

| 関数 | 役割 |
|------|------|
| `load_styles(now)` | CSS ファイルと時計アニメーション用 CSS 変数を `<style>` タグで注入する |
| `ambient_blobs()` | 背景に浮かぶ紫・青・ピンクのブロブ（装飾用 SVG）を返す |
| `hero()` | トップのキャラクター（手振り・まばたき・バウンス）と浮遊時計の SVG を返す |
| `status_pill(authenticated)` | 認証状態を示すバッジ（緑「Authenticated」/ 黄「Unauthenticated」）を返す |
| `stepper(active_step)` | 「freee認証 → コード入力 → レポート生成」の 3 ステップ進捗表示を返す |
| `shield_scene()` | 認証画面の発光リングとシールドアニメーションを返す |
| `auth_card_header()` | 「初回認証」カードのヘッダー HTML を返す |
| `report_card_header()` | 「レポート生成」カードのヘッダー HTML を返す |
| `dancing_mascot()` | ダンスするマスコット（腕振り・脚振り・まばたき・ジャンプ）の SVG を返す |
| `icon_row_period(year, month)` | 月度表示のアイコン行を返す |
| `icon_row_security()` | OAuth 2.0 / freee 公式のセキュリティマークを返す |
| `info_row_ids(company_id, employee_id)` | Company ID / Employee ID の表示行を返す |
| `footer_note(text)` | フッターテキストを返す |
| `_flat(s)` | 多行文字列の行頭インデントを除去するユーティリティ関数 |

### SVG アイコン定数

`ICON_CALENDAR`、`ICON_USER`、`ICON_BUILDING`、`ICON_SHIELD`、`ICON_SPARK` の 5 種類を定義しています。

---

## styles.css（スタイルシート）

アプリ全体のビジュアルを定義します。

| セクション | 内容 |
|----------|------|
| 基本 | フォント・背景グラデーション・ブロブ浮遊アニメーション |
| ヒーロー | キャラクター出現アニメーション・パーティクル上昇 |
| メトリクス | カード風ホバーエフェクト・テキストグラデーション |
| ボタン | プライマリ（紫→ピンク）・ダウンロード（緑）・リンクボタン |
| カード | 背景ぼかし・ボーダー・シャドウ |
| ステータスピル | OK / 警告の色分けとパルスアニメーション |
| ステッパー | 3 段階進捗のグラデーションとライン |
| シールド | 発光リングのパルスとシールド揺れアニメーション |
| マスコット | ジャンプ・腕振り・脚振り・まばたき・音符浮遊・きらめき |

主な `@keyframes` アニメーション一覧:

| アニメーション名 | 効果 |
|----------------|------|
| `floatBlob` | 背景ブロブの浮遊 |
| `gradientShift` | ヒーロー背景グラデーションの変化 |
| `wave` | キャラクターの手振り |
| `blink` | 目のまばたき |
| `ringPulse` | シールドの発光リング |
| `mascotJump` | マスコットのジャンプ |
| `armDanceL/R` | 両腕のダンス |
| `legKickL/R` | 両脚のキック |
| `sparkPop` | きらめきの出現 |

---

## データフロー

```
① ユーザーが freee にログイン（OAuth 認証）
        ↓
② アクセストークンを取得・セッションに保存
        ↓
③ /users/me でユーザー情報・所属会社を取得
        ↓
④ 月と会社を選択して「データ取得 & Excel作成」ボタン
        ↓
⑤ 月の各日に freee API /work_records/{date} を呼び出し
        ↓
⑥ 取得データを日付キーの辞書に整形
        ↓
⑦ Excel テンプレートに氏名・勤怠時刻を転記
        ↓
⑧ Excel ファイルをダウンロード
```

---

## セキュリティ設計

- **トークンの保存場所**: `st.session_state`（メモリのみ、ファイルに永続化しない）
- **セッション分離**: Streamlit はユーザーごとにセッションが独立しており、他ユーザーのトークンと混ざらない
- **CLIENT_SECRET の管理**: 環境変数または Streamlit Secrets のみで管理し、コードに埋め込まない
- **トークン自動更新**: アクセストークン期限切れ時はリフレッシュトークンで自動更新

---

## 技術スタック

| 用途 | 技術 |
|------|------|
| Web フレームワーク | Streamlit |
| HTTP 通信 | requests |
| Excel 操作 | openpyxl |
| 環境変数 | python-dotenv |
| 認証方式 | OAuth 2.0 認可コードフロー |
| API | freee 人事労務 API v1 |
| デプロイ | Streamlit Community Cloud（無料） |
