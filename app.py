# -*- coding: utf-8 -*-
"""
freee人事労務API × Streamlit
勤怠データを取得してExcelに転記するWEBアプリ
"""

import os
import requests
import calendar
from io import BytesIO
from datetime import datetime, date, time, timedelta
from urllib.parse import urlencode
from dotenv import load_dotenv
import streamlit as st
from openpyxl import load_workbook

import ui

# 設定読込: ローカルは .env / .env.sample、Streamlit Cloud は st.secrets を使用
load_dotenv()
load_dotenv(".env.sample", override=True)


def _cfg(key: str) -> str | None:
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key)


CLIENT_ID = _cfg("CLIENT_ID")
CLIENT_SECRET = _cfg("CLIENT_SECRET")
REDIRECT_URI = _cfg("REDIRECT_URI")

TEMPLATE_FILE = "2026_2月_作業実施報告書_SMHC_神田涼平 .xlsx"


# =========================
# OAuth関連処理
# =========================

def get_auth_url():
    params = urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "hr",
    })
    return f"https://accounts.secure.freee.co.jp/public_api/authorize?{params}"


def save_token(token_data):
    st.session_state["token"] = token_data


def load_token():
    return st.session_state.get("token")


def get_token_from_code(code):
    url = "https://accounts.secure.freee.co.jp/public_api/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    res = requests.post(url, data=data)
    token = res.json()
    token["expires_at"] = (datetime.now() + timedelta(seconds=token["expires_in"])).timestamp()
    save_token(token)
    return token


def refresh_token(token):
    url = "https://accounts.secure.freee.co.jp/public_api/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": token["refresh_token"],
    }
    res = requests.post(url, data=data)
    new_token = res.json()
    new_token["expires_at"] = (datetime.now() + timedelta(seconds=new_token["expires_in"])).timestamp()
    save_token(new_token)
    return new_token


def get_valid_token():
    token = load_token()
    if not token:
        return None
    if datetime.now().timestamp() > token["expires_at"]:
        token = refresh_token(token)
    return token["access_token"]


# =========================
# ユーザー情報取得
# =========================

def get_user_info(access_token):
    url = "https://api.freee.co.jp/hr/api/v1/users/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        st.error(f"ユーザー情報取得エラー: {res.text}")
        return None
    return res.json()


def get_employee_name(access_token, company_id, employee_id):
    """従業員の表示名を取得"""
    url = f"https://api.freee.co.jp/hr/api/v1/employees/{employee_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"company_id": company_id}
    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        st.warning(f"従業員名API失敗 (status={res.status_code}): {res.text[:300]}")
        return None
    body = res.json()
    # freee HR APIは {"employee": {...}} でラップされることがある
    emp = body.get("employee", body)
    last = (emp.get("last_name") or "").strip()
    first = (emp.get("first_name") or "").strip()
    full = f"{last}{first}".strip()
    return emp.get("display_name") or emp.get("name") or (full or None)


# =========================
# API処理
# =========================

def _parse_hhmm(s):
    """freeeの '2026-04-01 09:00:00' や '09:00:00' から time オブジェクトを返す"""
    if not s:
        return None
    s = str(s).strip()
    time_part = s.split(" ", 1)[-1] if " " in s else s
    try:
        parts = time_part.split(":")
        return time(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return None


def _break_total_hours(break_records):
    """break_records 配列から合計休憩時間(時間, 小数)を計算"""
    total_minutes = 0
    for b in break_records or []:
        t1 = _parse_hhmm(b.get("clock_in_at"))
        t2 = _parse_hhmm(b.get("clock_out_at"))
        if t1 and t2:
            total_minutes += max(0, (t2.hour * 60 + t2.minute) - (t1.hour * 60 + t1.minute))
    return round(total_minutes / 60, 2) if total_minutes else 0


def get_work_records(year, month, access_token, company_id, employee_id):
    """各日ごとに勤怠データを取得 (GET /employees/{id}/work_records/{date})"""
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"company_id": company_id}
    days = calendar.monthrange(year, month)[1]

    records = []
    errors = []
    progress = st.progress(0.0, text="勤怠データ取得中...")
    for i in range(days):
        day = i + 1
        date_str = f"{year}-{month:02d}-{day:02d}"
        url = (
            "https://api.freee.co.jp/hr/api/v1"
            f"/employees/{employee_id}/work_records/{date_str}"
        )
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            rec = res.json()
            if not rec.get("date"):
                rec["date"] = date_str
            records.append(rec)
        elif res.status_code != 404:
            errors.append(f"{date_str}: status={res.status_code} {res.text[:120]}")
        progress.progress((i + 1) / days, text=f"{date_str} 取得中...")
    progress.empty()

    if errors:
        st.warning("一部の日付でエラーが発生しました:\n" + "\n".join(errors[:5]))

    # デバッグ用: 先頭レコードの構造を確認できるようにする
    if records:
        with st.expander("🔍 先頭日のレスポンス構造 (デバッグ)"):
            st.json(records[0])

    return records


def format_work_data(records):
    data = {}
    for r in records:
        d = r.get("date")
        if not d:
            continue
        data[d] = {
            "clock_in": _parse_hhmm(r.get("clock_in_at")),
            "clock_out": _parse_hhmm(r.get("clock_out_at")),
            "break": _break_total_hours(r.get("break_records")),
        }
    return data


def write_to_excel(year, month, data, employee_name):
    wb = load_workbook(TEMPLATE_FILE)
    ws = wb.active
    ws["K8"] = date(year, month, 1)  # date型で書き込み → L列の weekday書式(ddd)が機能する

    days = calendar.monthrange(year, month)[1]
    for i in range(days):
        row = 8 + i
        date_str = f"{year}-{month:02d}-{i+1:02d}"
        record = data.get(date_str, {})
        ws[f"M{row}"] = record.get("clock_in")
        ws[f"N{row}"] = record.get("clock_out")
        ws[f"O{row}"] = record.get("break")

    safe_name = (employee_name or "未設定").strip()
    file_name = f"{year}_{month}月_作業実施報告書_SMHC_{safe_name}.xlsx"

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return file_name, buffer


# =========================
# Streamlit UI
# =========================

st.set_page_config(
    page_title="freee 勤怠レポート",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 現在時刻（時計アニメ初期位置に使用）
now = datetime.now()
year = now.year
month = now.month

# スタイル読込（styles.css + 時計ディレイの CSS 変数）
st.markdown(ui.load_styles(now), unsafe_allow_html=True)

# 背景ブロブ + ヒーロー
st.markdown(ui.ambient_blobs(), unsafe_allow_html=True)
st.markdown(ui.hero(), unsafe_allow_html=True)

# トークン
access_token = get_valid_token()

# サイドバー
with st.sidebar:
    st.markdown("### Status")
    st.markdown(ui.status_pill(access_token is not None), unsafe_allow_html=True)

    st.markdown("### Period")
    st.markdown(ui.icon_row_period(year, month), unsafe_allow_html=True)
    st.caption(f"自動判定: {now.strftime('%Y-%m-%d')}")

    st.markdown("### Security")
    st.markdown(ui.icon_row_security(), unsafe_allow_html=True)

    st.markdown("---")

    if access_token:
        if st.button("ログアウト", use_container_width=True):
            st.session_state.pop("token", None)
            st.rerun()

    st.markdown(ui.footer_note(), unsafe_allow_html=True)


# メイン
if not access_token:
    st.markdown(ui.stepper(active_step=1), unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2.2, 1])
    with col_c:
        with st.container(border=True):
            st.markdown(ui.shield_scene(), unsafe_allow_html=True)
            st.markdown(ui.auth_card_header(), unsafe_allow_html=True)

            auth_url = get_auth_url()

            st.markdown("**Step 1.** freee認証ページを開いて認可コードを取得")
            st.link_button("freee認証ページを開く", auth_url, use_container_width=True)

            st.markdown("**Step 2.** 表示された認可コードを貼り付け")
            code = st.text_input(
                "認可コード",
                placeholder="ここに認可コードを入力",
                label_visibility="collapsed",
            )

            if st.button("認証する", type="primary", use_container_width=True):
                if not code:
                    st.warning("認可コードを入力してください")
                else:
                    with st.spinner("認証中..."):
                        get_token_from_code(code)
                    st.success("認証完了")
                    st.rerun()

else:
    user_info = get_user_info(access_token)
    if not user_info:
        st.stop()

    companies = user_info.get("companies", [])
    if not companies:
        st.error("所属会社が見つかりません")
        st.stop()

    # freee HR API の仕様:
    #   companies[].name         = 会社名
    #   companies[].display_name = ユーザー本人の従業員表示名（氏名）
    options = {
        (c.get("name") or f"会社ID:{c['id']}"): c
        for c in companies
    }

    m1, m2, m3 = st.columns(3)
    user_label = user_info.get("email") or f"User #{user_info.get('id', '-')}"
    m1.metric("User", user_label)
    m2.metric("対象月", f"{year}年{month:02d}月")
    m3.metric("所属会社", f"{len(companies)} 社")

    with st.container(border=True):
        st.markdown(ui.report_card_header(), unsafe_allow_html=True)
        st.markdown(ui.dancing_mascot(), unsafe_allow_html=True)

        label = st.selectbox("対象会社", list(options.keys()))
        selected = options[label]
        company_id = selected["id"]
        employee_id = selected.get("employee_id")

        if not employee_id:
            st.error("この会社には従業員IDが紐付いていません")
        else:
            st.markdown(ui.info_row_ids(company_id, employee_id), unsafe_allow_html=True)

            if st.button("データ取得 & Excel作成", type="primary", use_container_width=True):
                with st.status("レポートを生成しています...", expanded=True) as status:
                    st.write("① 従業員情報を取得中...")
                    # /users/me の companies[].display_name に氏名が入っているため優先
                    employee_name = (
                        selected.get("display_name")
                        or get_employee_name(access_token, company_id, employee_id)
                    )
                    st.write(f"　→ {employee_name or '(取得失敗)'}")

                    st.write("② 勤怠データを取得中...")
                    records = get_work_records(year, month, access_token, company_id, employee_id)
                    st.write(f"　→ {len(records)} 件のレコードを取得")

                    st.write("③ データを整形中...")
                    data = format_work_data(records)

                    st.write("④ Excelファイルを生成中...")
                    file_name, file_buffer = write_to_excel(year, month, data, employee_name)
                    st.write(f"　→ {file_name}")

                    status.update(label="レポート生成完了", state="complete", expanded=False)

                st.download_button(
                    label="Excelをダウンロード",
                    data=file_buffer,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

st.markdown(ui.footer_note("© <b>freee Kintai Report</b> · Streamlit で構築"), unsafe_allow_html=True)
