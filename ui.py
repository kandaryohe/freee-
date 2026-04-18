# -*- coding: utf-8 -*-
"""UIコンポーネント（SVGアイコン + HTMLテンプレート）"""

from datetime import datetime
from pathlib import Path


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
    """アニメーション時計＋軌道アイコン＋パーティクル付きヒーロー"""
    return f"""
<div class="hero">
  <div class="particles">
    <div class="particle p1"></div><div class="particle p2"></div><div class="particle p3"></div>
    <div class="particle p4"></div><div class="particle p5"></div><div class="particle p6"></div>
  </div>
  <div class="hero-inner">
    <div class="hero-text">
      <div class="hero-badge">{ICON_SPARK} Kintai Intelligence</div>
      <h1>freee 勤怠レポート</h1>
      <p>freee人事労務APIと連携し、当月の勤怠データを自動取得してExcelレポートをワンクリックで生成します。</p>
    </div>

    <div class="clock-scene">
      <svg class="clock-svg" viewBox="0 0 200 200">
        <defs>
          <radialGradient id="clockFace" cx="50%" cy="40%">
            <stop offset="0%" stop-color="rgba(255,255,255,0.25)"/>
            <stop offset="100%" stop-color="rgba(255,255,255,0.05)"/>
          </radialGradient>
        </defs>
        <circle cx="100" cy="100" r="88" fill="url(#clockFace)" stroke="rgba(255,255,255,0.4)" stroke-width="2"/>
        <circle cx="100" cy="100" r="75" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>
        <g stroke="rgba(255,255,255,0.7)" stroke-width="2" stroke-linecap="round">
          <line x1="100" y1="18" x2="100" y2="28"/>
          <line x1="100" y1="172" x2="100" y2="182"/>
          <line x1="18" y1="100" x2="28" y2="100"/>
          <line x1="172" y1="100" x2="182" y2="100"/>
        </g>
        <g stroke="rgba(255,255,255,0.35)" stroke-width="1.5" stroke-linecap="round">
          <line x1="141" y1="29" x2="137" y2="36"/>
          <line x1="171" y1="59" x2="164" y2="63"/>
          <line x1="171" y1="141" x2="164" y2="137"/>
          <line x1="141" y1="171" x2="137" y2="164"/>
          <line x1="59" y1="171" x2="63" y2="164"/>
          <line x1="29" y1="141" x2="36" y2="137"/>
          <line x1="29" y1="59" x2="36" y2="63"/>
          <line x1="59" y1="29" x2="63" y2="36"/>
        </g>
        <line class="hand-hour" x1="100" y1="100" x2="100" y2="60" stroke="white" stroke-width="4" stroke-linecap="round"/>
        <line class="hand-min" x1="100" y1="100" x2="100" y2="40" stroke="white" stroke-width="3" stroke-linecap="round"/>
        <line class="hand-sec" x1="100" y1="100" x2="100" y2="32" stroke="#fbbf24" stroke-width="2" stroke-linecap="round"/>
        <circle cx="100" cy="100" r="6" fill="white"/>
        <circle cx="100" cy="100" r="2.5" fill="#6366f1"/>
      </svg>

      <div class="orbit orbit-1"><div class="orbit-item">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
        </svg>
      </div></div>
      <div class="orbit orbit-2"><div class="orbit-item">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
        </svg>
      </div></div>
      <div class="orbit orbit-3"><div class="orbit-item">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/>
        </svg>
      </div></div>
    </div>
  </div>
</div>
"""


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
    return f"""
<div class="stepper">
    <div class="step"><div class="step-num{s1}">1</div><span class="step-label{l1}">freee認証</span></div>
    <div class="step-line"></div>
    <div class="step"><div class="step-num{s2}">2</div><span class="step-label{l2}">コード入力</span></div>
    <div class="step-line"></div>
    <div class="step"><div class="step-num{s3}">3</div><span class="step-label{l3}">レポート生成</span></div>
</div>
"""


def shield_scene() -> str:
    """認証画面: 発光リング＋揺れるシールド"""
    return """
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
"""


def auth_card_header() -> str:
    return """
<div class="card-title" style="justify-content:center;">
    <span>初回認証</span>
</div>
<div class="card-sub" style="text-align:center;">freeeアカウントと安全に連携して勤怠データへのアクセス権を取得します。</div>
"""


def report_card_header() -> str:
    return f"""
<div class="card-title">
    <span class="card-title-icon">{ICON_SPARK}</span>
    <span>レポート生成</span>
</div>
<div class="card-sub">対象の会社を選択し、ワンクリックで勤怠Excelレポートを生成します。</div>
"""


def doc_scene() -> str:
    """動く書類イラスト（浮遊＋線描画＋チェックポップイン）"""
    return """
<div class="doc-scene">
  <svg class="doc-svg doc-float" viewBox="0 0 220 170">
    <defs>
      <linearGradient id="paperGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#ffffff"/>
        <stop offset="100%" stop-color="#f1f5f9"/>
      </linearGradient>
      <linearGradient id="accent" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#6366f1"/>
        <stop offset="100%" stop-color="#ec4899"/>
      </linearGradient>
    </defs>
    <rect x="50" y="20" width="130" height="140" rx="10" fill="#e0e7ff" opacity="0.6" transform="rotate(-5 115 90)"/>
    <rect x="40" y="15" width="140" height="150" rx="12" fill="url(#paperGrad)" stroke="#e5e7eb" stroke-width="1.5"/>
    <rect x="40" y="15" width="140" height="32" rx="12" fill="url(#accent)"/>
    <rect x="40" y="35" width="140" height="12" fill="url(#accent)"/>
    <rect x="54" y="26" width="50" height="6" rx="3" fill="rgba(255,255,255,0.85)"/>
    <rect x="54" y="36" width="32" height="4" rx="2" fill="rgba(255,255,255,0.6)"/>
    <line class="doc-line l1" x1="56" y1="65" x2="140" y2="65" stroke="#c7d2fe" stroke-width="4" stroke-linecap="round"/>
    <line class="doc-line l2" x1="56" y1="82" x2="160" y2="82" stroke="#c7d2fe" stroke-width="4" stroke-linecap="round"/>
    <line class="doc-line l3" x1="56" y1="99" x2="125" y2="99" stroke="#c7d2fe" stroke-width="4" stroke-linecap="round"/>
    <line class="doc-line l4" x1="56" y1="116" x2="155" y2="116" stroke="#c7d2fe" stroke-width="4" stroke-linecap="round"/>
    <line class="doc-line l5" x1="56" y1="133" x2="130" y2="133" stroke="#c7d2fe" stroke-width="4" stroke-linecap="round"/>
    <g class="doc-check" transform="translate(165, 145)">
      <circle cx="0" cy="0" r="18" fill="#10b981"/>
      <polyline points="-7,0 -2,5 7,-5" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
    </g>
  </svg>
</div>
"""


def info_row_ids(company_id, employee_id: str) -> str:
    return f"""
<div class="icon-row">
    {ICON_BUILDING}<span>Company ID: <b>{company_id}</b></span>
    <span style="margin-left:auto;">{ICON_USER}<span style="margin-left:0.4rem;">Employee ID: <b>{employee_id}</b></span></span>
</div>
"""
