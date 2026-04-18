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
    """ヒーロー: キャラクター（手振り・まばたき・バウンス）＋浮遊時計"""
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

    <div class="char-scene">
      <svg class="char-svg" width="170" height="150" viewBox="0 0 200 180" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
        <defs>
          <linearGradient id="blazerGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#475569"/>
            <stop offset="100%" stop-color="#1e293b"/>
          </linearGradient>
          <linearGradient id="pantsGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#334155"/>
            <stop offset="100%" stop-color="#0f172a"/>
          </linearGradient>
          <linearGradient id="hairGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#312e81"/>
            <stop offset="100%" stop-color="#1e1b4b"/>
          </linearGradient>
          <linearGradient id="skinGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#fde4c9"/>
            <stop offset="100%" stop-color="#fbcfa5"/>
          </linearGradient>
          <linearGradient id="accentGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#a78bfa"/>
            <stop offset="100%" stop-color="#ec4899"/>
          </linearGradient>
        </defs>

        <ellipse cx="100" cy="168" rx="46" ry="5" fill="rgba(0,0,0,0.22)"/>

        <g class="char-body">
          <rect x="88" y="128" width="10" height="32" rx="3" fill="url(#pantsGrad)"/>
          <rect x="102" y="128" width="10" height="32" rx="3" fill="url(#pantsGrad)"/>
          <ellipse cx="93" cy="161" rx="8.5" ry="3.5" fill="#0f172a"/>
          <ellipse cx="107" cy="161" rx="8.5" ry="3.5" fill="#0f172a"/>
          <rect x="85" y="158" width="16" height="3" rx="1.5" fill="#1e293b"/>
          <rect x="99" y="158" width="16" height="3" rx="1.5" fill="#1e293b"/>

          <path d="M72 86 Q72 82 76 82 L124 82 Q128 82 128 86 L128 130 Q128 134 124 134 L76 134 Q72 134 72 130 Z" fill="url(#blazerGrad)"/>
          <path d="M86 82 L100 96 L114 82 L110 82 L100 92 L90 82 Z" fill="#0f172a" opacity="0.55"/>
          <path d="M94 82 L100 93 L106 82 Z" fill="#ffffff"/>
          <path d="M98 93 L102 93 L103 108 L97 108 Z" fill="url(#accentGrad)"/>
          <rect x="116" y="100" width="7" height="5" rx="0.5" fill="#f9a8d4" opacity="0.9"/>

          <rect x="62" y="86" width="11" height="40" rx="4" fill="url(#blazerGrad)"/>
          <rect x="61" y="122" width="13" height="4" rx="1" fill="#0f172a" opacity="0.6"/>
          <circle cx="68" cy="130" r="6.5" fill="url(#skinGrad)"/>

          <g class="wave-arm">
            <rect x="125" y="70" width="11" height="40" rx="4" fill="url(#blazerGrad)"/>
            <rect x="124" y="106" width="13" height="4" rx="1" fill="#0f172a" opacity="0.6"/>
            <circle cx="131" cy="68" r="7" fill="url(#skinGrad)"/>
          </g>

          <rect x="95" y="66" width="10" height="18" rx="2" fill="url(#skinGrad)"/>

          <circle cx="100" cy="50" r="22" fill="url(#skinGrad)"/>

          <path d="M78 48 Q80 22 100 20 Q122 22 122 48 Q118 38 108 34 Q104 32 100 32 Q96 32 92 34 Q85 36 78 48 Z" fill="url(#hairGrad)"/>
          <path d="M82 30 Q92 24 102 26" stroke="#a78bfa" stroke-width="1.2" fill="none" opacity="0.7" stroke-linecap="round"/>

          <circle cx="86" cy="58" r="2.5" fill="#fb7185" opacity="0.45"/>
          <circle cx="114" cy="58" r="2.5" fill="#fb7185" opacity="0.45"/>

          <circle cx="92" cy="52" r="6.5" fill="rgba(255,255,255,0.12)" stroke="#1f2937" stroke-width="1.3"/>
          <circle cx="108" cy="52" r="6.5" fill="rgba(255,255,255,0.12)" stroke="#1f2937" stroke-width="1.3"/>
          <line x1="98.5" y1="52" x2="101.5" y2="52" stroke="#1f2937" stroke-width="1.3"/>
          <line x1="78" y1="51" x2="85.5" y2="52" stroke="#1f2937" stroke-width="1.3" stroke-linecap="round"/>
          <line x1="114.5" y1="52" x2="122" y2="51" stroke="#1f2937" stroke-width="1.3" stroke-linecap="round"/>

          <g class="char-eyes">
            <ellipse cx="92" cy="52" rx="2" ry="2.8" fill="#1f2937"/>
            <ellipse cx="108" cy="52" rx="2" ry="2.8" fill="#1f2937"/>
            <circle cx="92.6" cy="51" r="0.7" fill="white"/>
            <circle cx="108.6" cy="51" r="0.7" fill="white"/>
          </g>

          <path d="M95 63 Q100 67 105 63" stroke="#1f2937" stroke-width="1.5" fill="none" stroke-linecap="round"/>

          <circle cx="78" cy="55" r="1.6" fill="#fbbf24"/>
        </g>

        <g class="mini-clock" transform="translate(30, 40)">
          <circle r="16" fill="white" opacity="0.95"/>
          <circle r="16" fill="none" stroke="#fbbf24" stroke-width="1.5"/>
          <line class="mini-hand-h" x1="0" y1="0" x2="0" y2="-9" stroke="#6366f1" stroke-width="2" stroke-linecap="round"/>
          <line class="mini-hand-m" x1="0" y1="0" x2="7" y2="-3" stroke="#8b5cf6" stroke-width="1.5" stroke-linecap="round"/>
          <circle r="2" fill="#6366f1"/>
        </g>
      </svg>
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


def doc_scene() -> str:
    """動く書類イラスト（浮遊＋線描画＋チェックポップイン）"""
    return _flat("""
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
""")


def dancing_mascot() -> str:
    """踊るオフィスワーカーマスコット（手振り・脚振り・まばたき・ジャンプ・きらめき）"""
    return _flat("""
<div class="mascot-scene">
  <svg class="mascot-svg" viewBox="0 0 220 170" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="mBodyGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#f472b6"/>
        <stop offset="100%" stop-color="#ec4899"/>
      </linearGradient>
      <linearGradient id="mPantsGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#6366f1"/>
        <stop offset="100%" stop-color="#4338ca"/>
      </linearGradient>
      <radialGradient id="mStage" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="rgba(250,204,21,0.25)"/>
        <stop offset="100%" stop-color="rgba(250,204,21,0)"/>
      </radialGradient>
    </defs>

    <ellipse cx="110" cy="160" rx="70" ry="9" fill="url(#mStage)"/>
    <ellipse cx="110" cy="158" rx="40" ry="4" fill="rgba(0,0,0,0.18)"/>

    <g class="mascot-body">
      <g class="leg-kick-l" transform-origin="96 128">
        <rect x="92" y="125" width="12" height="30" rx="4" fill="url(#mPantsGrad)"/>
        <ellipse cx="98" cy="156" rx="9" ry="4" fill="#1f2937"/>
      </g>
      <g class="leg-kick-r" transform-origin="118 128">
        <rect x="112" y="125" width="12" height="30" rx="4" fill="url(#mPantsGrad)"/>
        <ellipse cx="118" cy="156" rx="9" ry="4" fill="#1f2937"/>
      </g>

      <rect x="82" y="78" width="56" height="54" rx="14" fill="url(#mBodyGrad)"/>
      <path d="M100 78 L110 94 L120 78" stroke="white" stroke-width="2.2" fill="none" opacity="0.7"/>
      <circle cx="110" cy="108" r="2.6" fill="white" opacity="0.7"/>
      <circle cx="110" cy="118" r="2.6" fill="white" opacity="0.7"/>

      <g class="arm-dance-l">
        <rect x="68" y="76" width="12" height="40" rx="5" fill="url(#mBodyGrad)"/>
        <circle cx="74" cy="118" r="8" fill="#fde68a"/>
      </g>
      <g class="arm-dance-r">
        <rect x="140" y="58" width="12" height="40" rx="5" fill="url(#mBodyGrad)"/>
        <circle cx="146" cy="58" r="8" fill="#fde68a"/>
        <g class="mascot-thumb" transform="translate(146, 50)">
          <rect x="-2" y="-8" width="4" height="8" rx="2" fill="#fde68a"/>
        </g>
      </g>

      <rect x="103" y="60" width="14" height="22" rx="3" fill="#fde68a"/>

      <circle cx="110" cy="46" r="26" fill="#fde68a"/>
      <path d="M84 44 Q88 16 110 14 Q132 16 136 44 Q130 30 110 28 Q90 30 84 44 Z" fill="#312e81"/>

      <circle cx="98" cy="58" r="3.2" fill="#fca5a5" opacity="0.75"/>
      <circle cx="122" cy="58" r="3.2" fill="#fca5a5" opacity="0.75"/>

      <g class="mascot-eyes">
        <ellipse cx="101" cy="48" rx="2.6" ry="3.6" fill="#1f2937"/>
        <ellipse cx="119" cy="48" rx="2.6" ry="3.6" fill="#1f2937"/>
        <circle cx="102" cy="47" r="0.9" fill="white"/>
        <circle cx="120" cy="47" r="0.9" fill="white"/>
      </g>

      <path d="M101 60 Q110 68 119 60" stroke="#1f2937" stroke-width="2" fill="none" stroke-linecap="round"/>

      <g class="mascot-note" transform="translate(64, 58)">
        <path d="M0 0 L0 -14 L10 -18 L10 -4" stroke="#6366f1" stroke-width="2.2" fill="none" stroke-linecap="round"/>
        <ellipse cx="-2.5" cy="0" rx="3" ry="2.2" fill="#6366f1"/>
        <ellipse cx="7.5" cy="-4" rx="3" ry="2.2" fill="#6366f1"/>
      </g>
    </g>

    <g class="spark spark-1"><polygon points="30,30 32,38 40,40 32,42 30,50 28,42 20,40 28,38" fill="#fbbf24"/></g>
    <g class="spark spark-2"><polygon points="190,40 192,46 198,48 192,50 190,56 188,50 182,48 188,46" fill="#a78bfa"/></g>
    <g class="spark spark-3"><polygon points="200,110 202,116 208,118 202,120 200,126 198,120 192,118 198,116" fill="#f472b6"/></g>
    <g class="spark spark-4"><polygon points="20,110 22,116 28,118 22,120 20,126 18,120 12,118 18,116" fill="#34d399"/></g>
  </svg>
</div>
""")


def info_row_ids(company_id, employee_id: str) -> str:
    return _flat(f"""
<div class="icon-row">
    {ICON_BUILDING}<span>Company ID: <b>{company_id}</b></span>
    <span style="margin-left:auto;">{ICON_USER}<span style="margin-left:0.4rem;">Employee ID: <b>{employee_id}</b></span></span>
</div>
""")
