# freee 勤怠レポート

freee人事労務APIと連携し、**当月の勤怠データを自動取得して Excel レポートをワンクリックで生成**する Streamlit 製 Web アプリです。

---

## 概要

- 従業員が自分の freee アカウントで OAuth 認証
- 所属会社を選択し、任意で**契約名**を入力すると、当月分の勤怠データ（始業・終業・休憩・有給/半休）を自動取得
- 所定のテンプレート（作業実施報告書）に転記し、氏名入りの Excel ファイルとしてダウンロード

60 名規模のチームでの同時利用を想定した設計です（セッションごとに独立したトークン管理・メモリ上でのファイル生成）。

### Excelテンプレートへの転記仕様

| セル | 内容 |
| --- | --- |
| K3 | 契約名（任意入力。空欄可） |
| K5 | 作業者の苗字（freee登録の姓） |
| L5 | 作業者の名前（freee登録の名） |
| K8 | 対象月の初日（例: 2026/04/01） |
| L8〜 | 曜日（テンプレートの `=K8` 数式＋`ddd` 書式で自動表示） |
| M8〜 | 各日の始業時刻 |
| N8〜 | 各日の終業時刻 |
| O8〜 | 各日の休憩時間（時間・小数） ※未出勤日は空欄 |
| H8〜 | 備考欄（有給/半休時に自動記載 / 通常日はテンプレートの祝日VLOOKUP数式が動作） |

### 有給・半休の自動判定

freee API の `paid_holiday` / `half_holiday_type` / `half_paid_holiday_mins` を判定し、Excel の備考欄(H列)と勤怠時刻欄(M/N/O列)に以下を出力します。

| freee 上の状態 | 備考(H列) | 始業(M)/終業(N) | 休憩(O列) |
| --- | --- | --- | --- |
| 全日有給 | 「有給取得」 | 空欄 | 空欄 |
| 午前休 | 「午前休取得」 | freee の打刻時刻 | 休憩時間（無ければ 0.0） |
| 午後休 | 「午後休取得」 | freee の打刻時刻 | 休憩時間（無ければ 0.0） |
| 通常勤務日 | 既存の祝日数式 | freee の打刻時刻 | 合計休憩時間 |
| 未出勤日 | 既存の祝日数式 | 空欄 | 空欄 |

> ⚠️ 有給/半休は **freee 側で「申請 → 承認」フローが完了している** 必要があります。承認待ちのデータは API で取得できません。

---

## 必要環境

- Python 3.10 以上
- freee 人事労務の API 利用権限（freee アプリ登録済み）

---

## 構成の全体像

このアプリは以下の 2 通りの実行形態があります。

| 形態 | 用途 | 設定ソース | 利用URL |
| --- | --- | --- | --- |
| **ローカル実行** | 開発・個人動作確認 | `.env` | `http://localhost:8501` |
| **Streamlit Cloud** | チーム全員で共有利用 | Streamlit Secrets | `https://<your-app>.streamlit.app` |

---

## A. ローカル実行

### 1. リポジトリを取得

```bash
git clone https://github.com/kandaryohe/freee-.git
cd freee-
```

### 2. 依存ライブラリをインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数を設定

プロジェクト直下に **`.env`** ファイルを作成し、以下の値を設定します。
（`.env` は `.gitignore` 対象のため Git にはコミットされません）

```env
CLIENT_ID=<freeeアプリのClient ID>
CLIENT_SECRET=<freeeアプリのClient Secret>
REDIRECT_URI=<freeeアプリ管理画面に登録した「コールバックURL」と同一の値>
```

> - `CLIENT_ID` / `CLIENT_SECRET` は freee アプリ管理画面（開発者向け）で取得できます
> - `REDIRECT_URI` は freee 側で設定した「コールバックURL」と**完全に一字一句一致**させる必要があります
>   - 例1: ローカルで受け取る場合 → `http://localhost:8501`
>   - 例2: freee の developers ページで認可コードを表示させる場合 → `https://app.secure.freee.co.jp/developers/start_guides/applications/<app_id>/token?company_id=<company_id>`
>   - 例3: OOB（画面に認可コードを表示する方式） → `urn:ietf:wg:oauth:2.0:oob`

### 4. 起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が開きます。

---

## B. チームでURL共有して使うには（Streamlit Cloud デプロイ）

無料の **Streamlit Community Cloud** にデプロイすると、発行された URL を共有するだけで、チーム全員が自分の freee アカウントで認証してレポートを生成できます。

### 事前準備

- GitHub アカウント（このリポジトリへのアクセス権）
- freee 開発者アプリ（本番用の `CLIENT_ID` / `CLIENT_SECRET`）

### デプロイ手順

#### 1. Streamlit Cloud にサインイン

[https://share.streamlit.io/](https://share.streamlit.io/) にアクセスし、**GitHub アカウントでログイン**します。

#### 2. 新規アプリを作成

「**New app**」をクリックし、以下を指定：

- **Repository**: `kandaryohe/freee-`
- **Branch**: `main`
- **Main file path**: `app.py`

#### 3. Secrets を設定

「**Advanced settings → Secrets**」に以下を TOML 形式で貼り付け：

```toml
CLIENT_ID = "<freeeアプリのClient ID>"
CLIENT_SECRET = "<freeeアプリのClient Secret>"
REDIRECT_URI = ""   # 次のステップでURL発行後に埋めるため一旦空欄でOK
```

> 💡 本番運用時は `.env` は使用されず、上記の Streamlit Secrets が優先されます。

#### 4. Deploy 実行

「**Deploy**」をクリック。数分で `https://<your-app>.streamlit.app` のような URL が発行されます。

#### 5. REDIRECT_URI を更新

1. 発行された URL（例: `https://freee-kintai.streamlit.app`）をコピー
2. Secrets の `REDIRECT_URI` を上記 URL に書き換えて保存
3. アプリが自動で再起動される

#### 6. freee 側のコールバックURLを追加

**freee アプリ管理画面（開発者ページ）** にログインし、対象アプリの設定で：

- 「コールバックURL」欄に **発行されたStreamlit URL を追加**
   - 例: `https://freee-kintai.streamlit.app`
- 既存のローカル用URL（`http://localhost:8501` 等）と**併記可能**

#### 7. チームに URL を共有

`https://<your-app>.streamlit.app` を Slack / メール等でチーム全員に共有。各自が自分の freee アカウントで認証すれば、それぞれの勤怠レポートを生成できます。

### 重要な注意点

- freee 側「コールバックURL」と Streamlit Secrets の `REDIRECT_URI` は**完全一致必須**（末尾スラッシュ、`https` / `http` の違いも含め一字一句同一）
- `CLIENT_SECRET` は **Streamlit Secrets UI にのみ入力**し、GitHub にはコミットしない
- セッション（トークン）はブラウザ単位で独立。他人のデータが混ざることはありません

---

## 使い方

1. 起動後の画面で **「freee 認証ページを開く」** をクリック
2. freee でログイン＆認可 → `REDIRECT_URI` のページに遷移
   - **Streamlit Cloud / localhost の場合**: ブラウザのURLに `?code=xxxx` が付き、**自動で認証完了**します
   - **OOB 方式の場合**: 画面に認可コードが表示されるので、アプリの「認可コード」欄に貼り付けて「認証する」をクリック
3. 対象会社を選択
4. 必要に応じて **契約名** を入力（任意 / 空欄可）
5. **「データ取得 & Excel 作成」** をクリック
6. 生成された Excel を **「Excel をダウンロード」** で取得

---

## テスト手順

デプロイ後、または機能変更後に以下を実施してください。

### ✅ 事前準備

- [ ] freee 人事労務で自分のアカウントに当月の勤怠データがあることを確認
- [ ] `.env`（または Streamlit Cloud の Secrets）の `CLIENT_ID` / `CLIENT_SECRET` / `REDIRECT_URI` が正しく設定されているか
- [ ] freee アプリ管理画面のコールバックURLが `REDIRECT_URI` と完全一致しているか

### ✅ T1. 起動確認

1. `streamlit run app.py`（または Streamlit Cloud URL へアクセス）
2. トップ画面が表示される
3. サイドバー Status が **「Unauthenticated」** になっている

**合格条件**: エラー表示なく画面が表示される

### ✅ T2. OAuth 認証フロー

1. 「freee 認証ページを開く」をクリック → freee 認証画面に遷移
2. freee でログインし、認可を実行
3. リダイレクト先に表示された認可コード（`code=xxxxx` の `xxxxx` 部分）をコピー
4. アプリに戻り、「認可コード」欄に貼り付け
5. 「認証する」をクリック

**合格条件**: 「認証完了」が表示され、画面が再描画されて Status が **「Authenticated」** になる

### ✅ T3. ユーザー情報取得

1. 認証後、画面上部の 3 つのメトリクス（User / 対象月 / 所属会社）が表示される
2. 対象会社のプルダウンが表示される

**合格条件**: 自分のメール・当月・所属社数が正しく表示される

### ✅ T4. 勤怠データ取得＆Excel 生成

1. 対象会社を選択
2. **契約名** を入力（任意 / 空欄でもOK）
3. 「データ取得 & Excel 作成」をクリック
4. ステータス表示で ①〜④ が順番に完了する
5. 「Excel をダウンロード」ボタンが表示される

**合格条件**:
- エラーなく ①〜④ が完了する
- 取得件数が表示される（例: `→ 30 件のレコードを取得`）
- ダウンロードした Excel を開き、以下がすべて満たされること：
  - **K3** に契約名（入力した場合）
  - **K5** に苗字、**L5** に名前
  - **K8** に対象月初日（例: `2026/04/01`）
  - **L8〜** に曜日（テンプレートの数式で自動表示）
  - **M列（始業）/ N列（終業）/ O列（休憩時間）** に各日の値
  - **未出勤日（平日含む）の O 列は空欄**（`0.0` ではなく空）
- ファイル名が `2026_4月_作業実施報告書_SMHC_<氏名>.xlsx` の形式

### ✅ T4-2. 有給/半休の備考欄記載

freee で当月に **承認済みの有給/半休** がある場合に確認します（無ければスキップ可）。

**合格条件**: 該当日の H 列(備考)に以下が出力されている
- 全日有給 → 「**有給取得**」、M/N/O 列は空欄
- 午前休 → 「**午前休取得**」、M/N に打刻時刻、O に休憩時間（無ければ 0.0）
- 午後休 → 「**午後休取得**」、M/N に打刻時刻、O に休憩時間（無ければ 0.0）

> 画面下部に表示される「🔍 有給/半休レコード」expander で freee の生データと判定結果(`paid_full`/`am_half`/`pm_half`)を確認できます。

### ✅ T5. ログアウト

1. サイドバーの「ログアウト」をクリック
2. 画面が未認証状態に戻る

**合格条件**: Status が「Unauthenticated」に戻り、再び認証画面が表示される

### ✅ T6. 複数人同時利用（本番デプロイ後）

1. 2 人以上が同時にアプリ URL へアクセス
2. それぞれが別々の freee アカウントで認証
3. それぞれが自分の勤怠レポートを生成

**合格条件**: 他人のデータが混ざらず、全員が自分のデータを正しく取得できる

### ✅ T7. トークン自動更新

1. 認証後、1 時間以上放置
2. 再度「データ取得 & Excel 作成」を実行

**合格条件**: エラーなくデータ取得が成功する（内部で `refresh_token` が動作）

---

## トラブルシューティング

| 症状 | 原因の候補 | 対処 |
| --- | --- | --- |
| 「認可コードを入力してください」 | コード未入力 | freee 認証後に表示される `code=xxxx` を貼り付け |
| 「ユーザー情報取得エラー」 | トークン不正・スコープ不足 | freee アプリの権限設定とスコープ（`hr`）を確認 |
| `redirect_uri_mismatch` | freee 側の設定と `REDIRECT_URI` が不一致 | 末尾スラッシュ・`https`/`http` を含め完全一致させる |
| Excel の M/N 列が空 | 勤怠データが 0 件 / 時刻フィールドが null | freee 側に当月データがあるか確認 |
| Excel の O 列に `0.0` が大量表示 | 旧テンプレートを使っている | 最新の `YYYY年_MM月_作業実施報告書_SMHC_苗字 名前.xlsx` を使用 |
| K5 に苗字だけ、L5 が空 | freee の `display_name` に空白がない | freee 側の表示名を「姓 名」形式に登録 |
| Streamlit Cloud で 401 が出続ける | Secrets の `REDIRECT_URI` と freee 側 URL 不一致 | 両者を完全一致させて再デプロイ |
| 有給/半休が備考欄に出ない | freee 側で「申請中」「承認待ち」のまま | 上長に承認依頼。承認後に再取得 |
| 有給/半休判定が `(該当なし)` | freee 側のフィールド形式が想定と異なる | デバッグ expander の JSON を確認し `detect_leave_type()` の条件を調整 |
| スマホで Excel の数式が消えて見える | スマホアプリ側で関数が再計算されない | PC版 Excel で開くか、関数ベースのテンプレートではなく値貼付け版が必要 |
| `必須パラメータが不足...` (認証時) | `REDIRECT_URI` が freee 側未登録 | freee アプリ管理画面のコールバックURLに使用URLを追加 |

---

## セキュリティ上の注意

- `.env` は `.gitignore` で除外済。**絶対にコミットしないこと**
- `CLIENT_SECRET` が漏洩した場合は freee アプリ管理画面で即時再発行
- アクセストークンは `st.session_state`（ブラウザセッションごと）に保管。ファイルには保存しません
- Streamlit Cloud の Secrets はアプリ管理者のみ閲覧可能。チームメンバーには見えません
