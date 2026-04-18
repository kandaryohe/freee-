# -*- coding: utf-8 -*-
"""
freee人事労務API × Streamlit
勤怠データを取得してExcelに転記するWEBアプリ
"""

import os
import requests
import calendar
from datetime import datetime, timedelta
from dotenv import load_dotenv
import streamlit as st
from openpyxl import load_workbook

import ui

# .env読み込み
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")


# =========================
# OAuth関連処理
# =========================

def get_auth_url():
    return (
        "https://accounts.secure.freee.co.jp/public_api/authorize"
        f"?client_id={CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
    )


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


# =========================
# API処理
# =========================

def get_work_records(year, month, access_token, company_id, employee_id):
    url = "https://api.freee.co.jp/hr/api/v1/work_records"
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "company_id": company_id,
        "employee_id": employee_id,
        "start_date": start_date,
        "end_date": end_date
    }
    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        st.error(f"APIエラー: {res.text}")
        return []
    return res.json().get("work_records", [])


def format_work_data(records):
    data = {}
    for r in records:
        date = r.get("date")
        data[date] = {
            "clock_in": r.get("clock_in_at"),
            "clock_out": r.get("clock_out_at"),
            "break": r.get("break_minutes", 0)
        }
    return data


def write_to_excel(year, month, data):
    template = "作業実施報告書_テンプレート.xlsx"
    wb = load_workbook(template)
    ws = wb.active
    ws["K8"] = f"{year}/{month:02d}/01"
    days = calendar.monthrange(year, month)[1]
    for i in range(days):
        row = 8 + i
        date_str = f"{year}-{month:02d}-{i+1:02d}"
        record = data.get(date_str)
        if record:
            ws[f"M{row}"] = record["clock_in"]
            ws[f"N{row}"] = record["clock_out"]
            ws[f"O{row}"] = record["break"]
    output_file = f"勤怠_{year}_{month:02d}.xlsx"
    wb.save(output_file)
    return output_file


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
st.html(ui.load_styles(now))

# 背景ブロブ + ヒーロー
st.html(ui.ambient_blobs())
st.html(ui.hero())

# トークン
access_token = get_valid_token()

# サイドバー
with st.sidebar:
    st.markdown("### Status")
    st.html(ui.status_pill(access_token is not None))

    st.markdown("### Period")
    st.html(ui.icon_row_period(year, month))
    st.caption(f"自動判定: {now.strftime('%Y-%m-%d')}")

    st.markdown("### Security")
    st.html(ui.icon_row_security())

    st.markdown("---")

    if access_token:
        if st.button("ログアウト", use_container_width=True):
            st.session_state.pop("token", None)
            st.rerun()

    st.html(ui.footer_note())


# メイン
if not access_token:
    st.html(ui.stepper(active_step=1))

    col_l, col_c, col_r = st.columns([1, 2.2, 1])
    with col_c:
        with st.container(border=True):
            st.html(ui.shield_scene())
            st.html(ui.auth_card_header())

            auth_url = get_auth_url()

            st.markdown("**Step 1.** freee認証ページを開いて認可コードを取得")
            st.link_button("freee認証ページを開く", auth_url, use_container_width=True)

            st.markdown("")
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

    options = {
        (c.get("display_name") or c.get("name") or f"会社ID:{c['id']}"): c
        for c in companies
    }

    m1, m2, m3 = st.columns(3)
    user_label = user_info.get("email") or f"User #{user_info.get('id', '-')}"
    m1.metric("User", user_label)
    m2.metric("対象月", f"{year}年{month:02d}月")
    m3.metric("所属会社", f"{len(companies)} 社")

    st.markdown("")

    with st.container(border=True):
        st.html(ui.report_card_header())
        st.html(ui.doc_scene())

        label = st.selectbox("対象会社", list(options.keys()))
        selected = options[label]
        company_id = selected["id"]
        employee_id = selected.get("employee_id")

        if not employee_id:
            st.error("この会社には従業員IDが紐付いていません")
        else:
            st.html(ui.info_row_ids(company_id, employee_id))
            st.markdown("")

            if st.button("データ取得 & Excel作成", type="primary", use_container_width=True):
                with st.status("レポートを生成しています...", expanded=True) as status:
                    st.write("① 勤怠データを取得中...")
                    records = get_work_records(year, month, access_token, company_id, employee_id)
                    st.write(f"　→ {len(records)} 件のレコードを取得")

                    st.write("② データを整形中...")
                    data = format_work_data(records)

                    st.write("③ Excelファイルを生成中...")
                    file_path = write_to_excel(year, month, data)
                    st.write(f"　→ {file_path}")

                    status.update(label="レポート生成完了", state="complete", expanded=False)

                with open(file_path, "rb") as f:
                    st.download_button(
                        label="Excelをダウンロード",
                        data=f,
                        file_name=file_path,
                        use_container_width=True,
                    )

st.html(ui.footer_note("© <b>freee Kintai Report</b> · built with Streamlit"))
