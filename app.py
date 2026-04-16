# -*- coding: utf-8 -*-
"""
freee人事労務API × Streamlit
勤怠データを取得してExcelに転記するWEBアプリ
"""

import os
import json
import requests
import calendar
from datetime import datetime, timedelta
from dotenv import load_dotenv
import streamlit as st
from openpyxl import load_workbook

# .env読み込み
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
EMPLOYEE_ID = os.getenv("EMPLOYEE_ID")
COMPANY_ID = os.getenv("COMPANY_ID")

TOKEN_FILE = "token.json"


# =========================
# OAuth関連処理
# =========================

def get_auth_url():
    """認証URL生成"""
    return (
        "https://accounts.secure.freee.co.jp/public_api/authorize"
        f"?client_id={CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
    )


def save_token(token_data):
    """トークン保存（ローカル）"""
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f)


def load_token():
    """トークン読み込み"""
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        return json.load(f)


def get_token_from_code(code):
    """認可コードからトークン取得"""
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

    # 有効期限を保存
    token["expires_at"] = (datetime.now() + timedelta(seconds=token["expires_in"])).timestamp()

    save_token(token)
    return token


def refresh_token(token):
    """アクセストークン更新"""
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
    """有効なアクセストークン取得"""
    token = load_token()

    if not token:
        return None

    # 有効期限チェック
    if datetime.now().timestamp() > token["expires_at"]:
        token = refresh_token(token)

    return token["access_token"]


# =========================
# API処理（月次取得）
# =========================

def get_work_records(year, month, access_token):
    """1ヶ月分の勤怠データ取得"""
    url = "https://api.freee.co.jp/hr/api/v1/work_records"

    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "company_id": COMPANY_ID,
        "employee_id": EMPLOYEE_ID,
        "start_date": start_date,
        "end_date": end_date
    }

    res = requests.get(url, headers=headers, params=params)

    if res.status_code != 200:
        st.error(f"APIエラー: {res.text}")
        return []

    return res.json().get("work_records", [])


# =========================
# データ整形
# =========================

def format_work_data(records):
    """日付ごとに整理"""
    data = {}

    for r in records:
        date = r.get("date")
        data[date] = {
            "clock_in": r.get("clock_in_at"),
            "clock_out": r.get("clock_out_at"),
            "break": r.get("break_minutes", 0)
        }

    return data


# =========================
# Excel書き込み
# =========================

def write_to_excel(year, month, data):
    """テンプレートに転記"""
    template = "作業実施報告書_テンプレート.xlsx"
    wb = load_workbook(template)
    ws = wb.active

    # K8に月初
    ws["K8"] = f"{year}/{month:02d}/01"

    # 日数分ループ
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

st.title("freee 勤怠データ取得アプリ")

# 年月選択
year = st.number_input("年", value=2026)
month = st.number_input("月", min_value=1, max_value=12, value=2)

st.markdown("---")

# 初回認証
st.subheader("初回認証")

auth_url = get_auth_url()
st.write("① 下記URLへアクセスして認可コード取得")
st.write(auth_url)

code = st.text_input("認可コード入力")

if st.button("トークン取得"):
    token = get_token_from_code(code)
    st.success("トークン取得完了")

st.markdown("---")

# メイン処理
if st.button("データ取得＆Excel作成"):
    access_token = get_valid_token()

    if not access_token:
        st.error("先に認証してください")
    else:
        records = get_work_records(year, month, access_token)
        data = format_work_data(records)

        file_path = write_to_excel(year, month, data)

        with open(file_path, "rb") as f:
            st.download_button(
                label="Excelダウンロード",
                data=f,
                file_name=file_path
            )