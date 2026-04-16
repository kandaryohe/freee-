# -*- coding: utf-8 -*-
"""
============================================================
freee人事労務API × Streamlit
勤怠データ自動取得・Excel転記WEBアプリ
============================================================
【処理の流れ】
  1. 起動時に実行月を自動判定
  2. 初回のみ：「freeeにログイン」ボタンを押すとブラウザが開く
             → freee側で許可するとこのアプリに自動でリダイレクトされ、
               URLに含まれる認可コードを自動検知してトークンを保存
  3. ボタン押下で勤怠データをAPIから取得してExcelに転記
"""

# ===== 必要なライブラリのインポート =====
import os
import json
import webbrowser                # ブラウザを自動で開くために使用
import requests
import calendar
from datetime import datetime, timedelta, date
from io import BytesIO
from dotenv import load_dotenv
import streamlit as st
from openpyxl import load_workbook

# ===== .envファイルの読み込み =====
load_dotenv()

# ===== 環境変数の取得 =====
CLIENT_ID     = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI  = os.getenv("REDIRECT_URI")   # 例: http://localhost:8501
EMPLOYEE_ID   = os.getenv("EMPLOYEE_ID")
COMPANY_ID    = os.getenv("COMPANY_ID")

# ===== 定数 =====
TOKEN_FILE    = "token.json"
TEMPLATE_FILE = "作業実施報告書_テンプレート.xlsx"

FREEE_AUTH_URL  = "https://accounts.secure.freee.co.jp/public_api/authorize"
FREEE_TOKEN_URL = "https://accounts.secure.freee.co.jp/public_api/token"
FREEE_API_BASE  = "https://api.freee.co.jp/hr/api/v1"

# ===== 実行月を自動判定（年月選択UIは不要） =====
TODAY         = datetime.now()
TARGET_YEAR   = TODAY.year
TARGET_MONTH  = TODAY.month


# ============================================================
# セクション1: OAuth認証 関連の関数
# ============================================================

def get_auth_url() -> str:
    """
    【認証URL生成】
    freeeのログイン・許可画面へ誘導するURLを作成する。
    許可後は REDIRECT_URI（= このアプリのURL）に ?code=XXXXX 付きでリダイレクトされる。
    """
    return (
        f"{FREEE_AUTH_URL}"
        f"?client_id={CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
    )


def get_token_from_code(code: str) -> dict:
    """
    【認可コード → トークン取得】
    freeeから返ってきた認可コードをアクセストークン・リフレッシュトークンに交換する。
    """
    res = requests.post(FREEE_TOKEN_URL, data={
        "grant_type":    "authorization_code",
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code":          code,
        "redirect_uri":  REDIRECT_URI,
    })
    res.raise_for_status()
    token = res.json()
    token["expires_at"] = (
        datetime.now() + timedelta(seconds=token.get("expires_in", 21600))
    ).timestamp()
    save_token(token)
    return token


def refresh_access_token(token: dict) -> dict:
    """
    【アクセストークン自動更新】
    有効期限（6時間）切れ時に、リフレッシュトークンで新しいトークンを取得する。
    """
    res = requests.post(FREEE_TOKEN_URL, data={
        "grant_type":    "refresh_token",
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": token["refresh_token"],
    })
    res.raise_for_status()
    new_token = res.json()
    new_token["expires_at"] = (
        datetime.now() + timedelta(seconds=new_token.get("expires_in", 21600))
    ).timestamp()
    save_token(new_token)
    return new_token


def save_token(token: dict):
    """トークンをJSONファイルに保存する"""
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(token, f, ensure_ascii=False, indent=2)


def load_token() -> dict | None:
    """保存済みトークンを読み込む。ファイルがなければNoneを返す"""
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_valid_access_token() -> str | None:
    """
    【有効なアクセストークンを返す】
    期限切れなら自動でリフレッシュしてから返す（有効期限60秒前に更新）。
    """
    token = load_token()
    if token is None:
        return None
    if datetime.now().timestamp() > token.get("expires_at", 0) - 60:
        token = refresh_access_token(token)
    return token["access_token"]


# ============================================================
# セクション2: freee API呼び出し 関連の関数
# ============================================================

def fetch_daily_work_record(target_date: date, access_token: str) -> dict | None:
    """
    【1日分の勤怠データ取得】
    エンドポイント: GET /hr/api/v1/employees/{id}/work_records/{date}
    """
    url = f"{FREEE_API_BASE}/employees/{EMPLOYEE_ID}/work_records/{target_date.strftime('%Y-%m-%d')}"
    res = requests.get(url, headers={
        "Authorization": f"Bearer {access_token}",
        "FREEE-VERSION": "2022-02-01",
    }, params={"company_id": COMPANY_ID})

    if res.status_code == 404:
        return None  # 休日などデータなしは正常
    if res.status_code == 401:
        raise PermissionError("認証エラー: トークンが無効です。再認証してください。")
    if res.status_code != 200:
        raise RuntimeError(f"APIエラー ({res.status_code}): {res.text}")
    return res.json()


def fetch_month_work_records(year: int, month: int, access_token: str) -> dict:
    """
    【1ヶ月分の勤怠データ取得】
    対象月の全日をループしてAPIで取得し、日付→勤怠データの辞書として返す。
    """
    days_in_month = calendar.monthrange(year, month)[1]
    records = {}
    bar = st.progress(0, text="APIからデータを取得中...")

    for day in range(1, days_in_month + 1):
        d = date(year, month, day)
        record = fetch_daily_work_record(d, access_token)
        if record:
            records[d.strftime("%Y-%m-%d")] = record
        bar.progress(day / days_in_month, text=f"取得中: {d} ({day}/{days_in_month}日)")

    bar.empty()
    return records


# ============================================================
# セクション3: データ整形 関連の関数
# ============================================================

def parse_time_to_hhmm(iso_str: str | None) -> str | None:
    """ISO8601の日時文字列を "HH:MM" 形式に変換する"""
    if not iso_str:
        return None
    try:
        return datetime.fromisoformat(iso_str).strftime("%H:%M")
    except (ValueError, TypeError):
        return None


def calc_break_minutes(record: dict) -> int:
    """
    【休憩時間の合計分数を計算】
    break_records（複数休憩）がある場合はそこから合計を計算、
    なければ break_minutes フィールドをそのまま使用する。
    """
    break_records = record.get("break_records", [])
    if break_records:
        total = 0
        for br in break_records:
            s, e = br.get("clock_in_at"), br.get("clock_out_at")
            if s and e:
                total += int((datetime.fromisoformat(e) - datetime.fromisoformat(s)).total_seconds() / 60)
        return total
    return record.get("break_minutes", record.get("total_break_minutes", 0))


def extract_attendance_data(raw_records: dict) -> dict:
    """APIの生データを { 日付: {clock_in, clock_out, break_min} } の形式に整形する"""
    return {
        date_str: {
            "clock_in":  parse_time_to_hhmm(r.get("clock_in_at")),
            "clock_out": parse_time_to_hhmm(r.get("clock_out_at")),
            "break_min": calc_break_minutes(r),
        }
        for date_str, r in raw_records.items()
    }


# ============================================================
# セクション4: Excel書き込み 関連の関数
# ============================================================

def write_to_excel(year: int, month: int, attendance: dict) -> BytesIO:
    """
    【Excelテンプレートへの転記】
    K8=月初日付、M列=出勤、N列=退勤、O列=休憩（分）を書き込み、
    メモリ上のバイトデータとして返す。
    """
    if not os.path.exists(TEMPLATE_FILE):
        raise FileNotFoundError(
            f"テンプレートが見つかりません: {TEMPLATE_FILE}\n"
            "app.py と同じフォルダに配置してください。"
        )

    wb = load_workbook(TEMPLATE_FILE, keep_vba=False, data_only=False)
    ws = wb.active

    ws["K8"] = date(year, month, 1)  # 月初日付（Excelの日付型で入力）

    for day in range(1, calendar.monthrange(year, month)[1] + 1):
        row = 7 + day                                # 8行目スタート
        key = f"{year}-{month:02d}-{day:02d}"
        rec = attendance.get(key)
        if rec:
            if rec["clock_in"]:
                ws[f"M{row}"] = rec["clock_in"]
            if rec["clock_out"]:
                ws[f"N{row}"] = rec["clock_out"]
            if rec["break_min"] is not None:
                ws[f"O{row}"] = rec["break_min"]

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output


# ============================================================
# セクション5: Streamlit WEB画面
# ============================================================

st.set_page_config(page_title="freee 勤怠データ取得アプリ", page_icon="📋", layout="centered")
st.title("📋 freee 勤怠データ取得アプリ")

# ===== 実行月を自動表示（選択不要） =====
st.info(f"対象月: **{TARGET_YEAR}年 {TARGET_MONTH}月**（実行月を自動判定）")
st.divider()

# ============================================================
# 自動認証処理：URLに ?code= が含まれていたらトークンに自動交換
# ============================================================
# freeeが許可後に http://localhost:8501?code=XXXXX へリダイレクトしてくる。
# Streamlit の st.query_params でそのコードを自動検知して処理する。
query_params = st.query_params

if "code" in query_params and load_token() is None:
    # URLに認可コードが含まれていれば自動でトークンに交換する
    with st.spinner("認証中... トークンを取得しています"):
        try:
            get_token_from_code(query_params["code"])
            st.query_params.clear()   # URLから ?code= を取り除く
            st.rerun()                # 画面を再読み込みして認証済み状態にする
        except Exception as e:
            st.error(f"❌ 認証に失敗しました: {e}")
            st.query_params.clear()
            st.stop()

# ============================================================
# UI① : 認証ステータスと初回ログインボタン
# ============================================================
st.subheader("① freee認証")

token = load_token()

if token:
    # ===== 認証済み =====
    st.success("✅ 認証済み — トークンが保存されています")
else:
    # ===== 未認証：ボタン1つでブラウザを自動で開く =====
    st.warning("⚠️ 未認証です。下のボタンを押してfreeeにログインしてください。")
    st.caption("ボタンを押すとブラウザが開きます。freeeで「許可する」をクリックすると自動で認証が完了します。")

    if st.button("🔑 freeeにログイン（ブラウザが開きます）", type="primary", use_container_width=True):
        # サーバー側（ローカルPC）でブラウザを自動で開く
        webbrowser.open(get_auth_url())
        st.info("ブラウザが開きました。freeeにログインして「許可する」を押してください。\nページが自動で更新され、認証が完了します。")
        st.stop()

st.divider()

# ============================================================
# UI② : データ取得 & Excel作成
# ============================================================
st.subheader("② データ取得 & Excel作成")

if st.button("🚀 データ取得＆Excelファイル作成", type="primary", use_container_width=True, disabled=(token is None)):

    # ===== 有効なアクセストークンを取得（期限切れなら自動リフレッシュ） =====
    try:
        access_token = get_valid_access_token()
    except Exception as e:
        st.error(f"❌ トークンの更新に失敗しました: {e}")
        st.stop()

    if not access_token:
        st.error("❌ 未認証です。先にfreeeにログインしてください。")
        st.stop()

    # ===== API取得・Excel転記 =====
    try:
        with st.status(f"📡 {TARGET_YEAR}年{TARGET_MONTH}月の勤怠データを取得中...", expanded=True) as status:
            st.write("freee APIにリクエスト送信中...")
            raw_records = fetch_month_work_records(TARGET_YEAR, TARGET_MONTH, access_token)

            st.write(f"✅ {len(raw_records)} 日分のデータを取得しました")
            st.write("Excelファイルを作成中...")
            attendance = extract_attendance_data(raw_records)
            excel_data = write_to_excel(TARGET_YEAR, TARGET_MONTH, attendance)
            status.update(label="✅ 完了！", state="complete", expanded=False)

    except FileNotFoundError as e:
        st.error(f"❌ {e}")
        st.stop()
    except PermissionError as e:
        st.error(f"❌ {e}")
        st.stop()
    except Exception as e:
        st.error(f"❌ 処理中にエラーが発生しました: {e}")
        st.stop()

    # ===== 結果表示 & ダウンロードボタン =====
    if not raw_records:
        st.warning("⚠️ 取得できたデータが0件でした。従業員IDや事業所IDを確認してください。")
    else:
        st.success(f"✅ {TARGET_YEAR}年{TARGET_MONTH}月の勤怠データ {len(raw_records)}日分をExcelに転記しました")
        st.download_button(
            label="📥 Excelファイルをダウンロード",
            data=excel_data,
            file_name=f"勤怠_{TARGET_YEAR}_{TARGET_MONTH:02d}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
