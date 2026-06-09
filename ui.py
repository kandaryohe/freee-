# -*- coding: utf-8 -*-
"""UIコンポーネント（SVGアイコン + HTMLテンプレート）"""

from datetime import datetime
from pathlib import Path


def _flat(s: str) -> str:
    """st.markdown が 4スペース以上の行頭インデントをコードブロックとして扱うのを防ぐため、
    各行の行頭空白を除去して単一行として連結する。"""
    return "".join(line.lstrip() for line in s.splitlines())


# =========================
# SVGアイコン
# =========================
ICON_CALENDAR = (
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="3" y="4" width="18" height="18" rx="2"/>'
    '<line x1="16" y1="2" x2="16" y2="6"/>'
    '<line x1="8" y1="2" x2="8" y2="6"/>'
    '<line x1="3" y1="10" x2="21" y2="10"/></svg>'
)

ICON_USER = (
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>'
    '<circle cx="12" cy="7" r="4"/></svg>'
)

ICON_BUILDING = (
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="4" y="2" width="16" height="20" rx="2"/>'
    '<path d="M9 22v-4h6v4"/>'
    '<path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M12 6h.01"/>'
    '<path d="M12 10h.01"/><path d="M12 14h.01"/>'
    '<path d="M16 10h.01"/><path d="M16 14h.01"/>'
    '<path d="M8 10h.01"/><path d="M8 14h.01"/></svg>'
)

ICON_SHIELD = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
)

ICON_SPARK = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M12 2l2.4 7.4H22l-6 4.6 2.3 7.4L12 17l-6.3 4.4L8 14 2 9.4h7.6L12 2z"/></svg>'
)


# =========================
# スタイル読込
# =========================

def load_styles(now: datetime) -> str:
    """styles.css を読込み、時計用のディレイ(CSS変数)を注入したstyleブロックを返す"""
    sec_delay = -now.second
    min_delay = -(now.minute * 60 + now.second)
    hour_delay = -((now.hour % 12) * 3600 + now.minute * 60 + now.second)

    css_path = Path(__file__).parent / "styles.css"
    css = css_path.read_text(encoding="utf-8")

    time_vars = (
        ":root {"
        f" --sec-delay: {sec_delay}s;"
        f" --min-delay: {min_delay}s;"
        f" --hour-delay: {hour_delay}s;"
        " }"
    )

    return f"<style>{css}\n{time_vars}</style>"


# =========================
# HTMLテンプレート
# =========================

def ambient_blobs() -> str:
    return (
        '<div class="ambient-blob blob-a"></div>'
        '<div class="ambient-blob blob-b"></div>'
        '<div class="ambient-blob blob-c"></div>'
    )


def hero() -> str:
    """ヒーロー: タイトル＋説明テキスト"""
    return _flat("""
<div class="hero">
  <div class="particles">
    <div class="particle p1"></div><div class="particle p2"></div><div class="particle p3"></div>
    <div class="particle p4"></div><div class="particle p5"></div><div class="particle p6"></div>
  </div>
  <div class="hero-inner">
    <div class="hero-text">
      <h1>freee 勤怠レポート</h1>
      <p>freee人事労務APIと連携し、当月の勤怠データを自動取得してExcelレポートをワンクリックで生成します。</p>
    </div>
  </div>
</div>
""")


def status_pill(authenticated: bool) -> str:
    if authenticated:
        return '<span class="status-pill ok"><span class="status-dot"></span>Authenticated</span>'
    return '<span class="status-pill warn"><span class="status-dot"></span>Unauthenticated</span>'


def icon_row_period(year: int, month: int) -> str:
    return f'<div class="icon-row">{ICON_CALENDAR}<span><b>{year}年 {month:02d}月</b></span></div>'


def icon_row_security() -> str:
    return f'<div class="icon-row">{ICON_SHIELD}<span>OAuth 2.0 / freee公式</span></div>'


def footer_note(text: str = "Powered by <b>freee HR API</b>") -> str:
    return f'<div class="footer-note">{text}</div>'


def stepper(active_step: int = 1) -> str:
    def cls(n: int) -> tuple[str, str]:
        muted = " muted" if n != active_step else ""
        return muted, muted

    s1, l1 = cls(1)
    s2, l2 = cls(2)
    s3, l3 = cls(3)
    return _flat(f"""
<div class="stepper">
    <div class="step"><div class="step-num{s1}">1</div><span class="step-label{l1}">freee認証</span></div>
    <div class="step-line"></div>
    <div class="step"><div class="step-num{s2}">2</div><span class="step-label{l2}">コード入力</span></div>
    <div class="step-line"></div>
    <div class="step"><div class="step-num{s3}">3</div><span class="step-label{l3}">レポート生成</span></div>
</div>
""")


def shield_scene() -> str:
    """認証画面: 発光リング＋揺れるシールド"""
    return _flat("""
<div class="shield-scene">
    <div class="shield-ring"></div>
    <div class="shield-ring"></div>
    <div class="shield-ring"></div>
    <div class="shield-core">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <polyline points="9 12 11 14 15 10"/>
        </svg>
    </div>
</div>
""")


def auth_card_header() -> str:
    return _flat("""
<div class="card-title" style="justify-content:center;">
    <span>初回認証</span>
</div>
<div class="card-sub" style="text-align:center;">freeeアカウントと安全に連携して勤怠データへのアクセス権を取得します。</div>
""")


def report_card_header() -> str:
    return _flat(f"""
<div class="card-title">
    <span class="card-title-icon">{ICON_SPARK}</span>
    <span>レポート生成</span>
</div>
<div class="card-sub">対象の会社を選択し、ワンクリックで勤怠Excelレポートを生成します。</div>
""")


def upload_card_header() -> str:
    return _flat(f"""
<div class="card-title">
    <span class="card-title-icon">{ICON_SPARK}</span>
    <span>Excel → freee 書き込み</span>
</div>
<div class="card-sub">作業実施報告書のExcelをアップロードすると、勤怠データをfreeeに自動で書き込みます。</div>
""")


def info_row_ids(company_id, employee_id: str) -> str:
    return _flat(f"""
<div class="icon-row">
    {ICON_BUILDING}<span>Company ID: <b>{company_id}</b></span>
    <span style="margin-left:auto;">{ICON_USER}<span style="margin-left:0.4rem;">Employee ID: <b>{employee_id}</b></span></span>
</div>
""")
