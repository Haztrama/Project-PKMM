"""utils.py - Tema CSS, komponen UI, status sistem, autentikasi simulasi, dan pelaporan JSON.

Modul ini sengaja ringan (tanpa transformers/librosa) agar halaman Beranda dan Login cepat dimuat.
"""
import hmac
import html
import json
import os
import platform
import re
from datetime import datetime, timedelta, timezone

import requests
import streamlit as st

from knowledge import JOB_ROLES, QUESTION_DB

# ----------------------------------------------------------------------------
# KONFIGURASI
# ----------------------------------------------------------------------------
APP_VERSION = "1.0.0"

OLLAMA_BASE = "http://localhost:11434"
OLLAMA_URL = f"{OLLAMA_BASE}/api/generate"
OLLAMA_MODEL = "zephyr"
OLLAMA_TIMEOUT = 120  # detik

TARGET_SR = 16000  # Wav2Vec2 mewajibkan input 16 kHz mono
ASR_MODELS = {
    "Inggris": "facebook/wav2vec2-base-960h",
    # Model Wav2Vec2 XLSR hasil fine-tuning Common Voice Indonesia (lebih besar -> lebih lambat di CPU)
    "Indonesia": "indonesian-nlp/wav2vec2-large-xlsr-indonesian",
}

# Path halaman relatif terhadap file utama (app.py)
PAGE_HOME = "app.py"
PAGE_LOGIN = "pages/1_🔐_Login.py"
PAGE_DASH = "pages/2_📊_Dashboard_Penilaian.py"
PAGE_HISTORY = "pages/3_📋_Riwayat_Kandidat.py"

# Skor -> (label, nada badge, warna)
SCORE_META = {
    0: ("Tidak Ada Jawaban", "gray", "#94A3B8"),
    1: ("Kurang", "red", "#DC2626"),
    2: ("Cukup", "amber", "#D97706"),
    3: ("Baik", "green", "#10B981"),
    4: ("Sangat Baik", "green", "#059669"),
}

# ----------------------------------------------------------------------------
# TEMA CSS (bersih ala SaaS profesional; tanpa font/CDN eksternal agar tetap 100% lokal)
# ----------------------------------------------------------------------------
THEME_CSS = r"""
:root{
  --il-primary:#3F4F8F; --il-primary-dark:#33417A; --il-primary-soft:#EEF1FB;
  --il-ink:#0F172A; --il-muted:#64748B; --il-line:#E6E8F0; --il-bg:#F6F7FB;
  --il-green:#10B981; --il-green-dark:#047857; --il-green-soft:#ECFDF5;
  --il-amber:#B45309; --il-amber-soft:#FFFBEB;
  --il-red:#B91C1C; --il-red-soft:#FEF2F2; --il-night:#0F172A;
}
html, body, .stApp, [class*="css"]{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  color:var(--il-ink);
}
.stApp{background:var(--il-bg);}
[data-testid="stSidebarNav"]{display:none;}
#MainMenu, footer{visibility:hidden;}
[data-testid="stHeader"]{background:transparent;}
.block-container{max-width:1180px;padding-top:1rem;padding-bottom:3rem;}
h1,h2,h3{letter-spacing:-.02em;color:var(--il-ink);}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--il-line);}

/* Kartu: container dengan key berawalan "card" */
div[class*="st-key-card"]{
  background:#fff;border:1px solid var(--il-line);border-radius:16px;padding:20px 22px;
}
.il-card-title{display:flex;align-items:center;justify-content:space-between;gap:10px;
  font-weight:700;font-size:1.02rem;margin-bottom:.75rem;}

/* Input & tombol */
[data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="textarea"]{border-radius:10px !important;}
button[data-testid="stBaseButton-primary"]{
  background:var(--il-primary);border:1px solid var(--il-primary);border-radius:10px;font-weight:600;color:#fff;}
button[data-testid="stBaseButton-primary"]:hover{background:var(--il-primary-dark);border-color:var(--il-primary-dark);color:#fff;}
button[data-testid="stBaseButton-secondary"]{
  border-radius:10px;border:1px solid var(--il-line);background:#fff;font-weight:600;color:var(--il-ink);}
button[data-testid="stBaseButton-secondary"]:hover{border-color:var(--il-primary);color:var(--il-primary);}
a[data-testid="stPageLink-NavLink"]{border-radius:10px;font-weight:600;}
[data-testid="stFileUploaderDropzone"]{border-radius:12px;border:1.5px dashed #CBD2E6;background:#FAFBFF;}

/* Brand & top bar */
.il-brand{display:flex;align-items:center;gap:10px;font-weight:750;font-size:1.08rem;letter-spacing:-.01em;}
.il-brand-mark{width:34px;height:34px;border-radius:10px;background:var(--il-primary);color:#fff;
  display:grid;place-items:center;font-size:1rem;}
.il-brand-mark--lg{width:56px;height:56px;border-radius:16px;font-size:1.5rem;margin:0 auto .6rem;}

/* Badge / chip */
.il-badge{display:inline-flex;align-items:center;gap:6px;padding:3px 10px;border-radius:999px;
  font-size:.78rem;font-weight:650;border:1px solid transparent;white-space:nowrap;}
.il-badge--green{background:var(--il-green-soft);color:var(--il-green-dark);border-color:#A7F3D0;}
.il-badge--amber{background:var(--il-amber-soft);color:var(--il-amber);border-color:#FDE68A;}
.il-badge--red{background:var(--il-red-soft);color:var(--il-red);border-color:#FECACA;}
.il-badge--blue{background:var(--il-primary-soft);color:var(--il-primary);border-color:#D6DCF3;}
.il-badge--gray{background:#F1F5F9;color:var(--il-muted);border-color:#E2E8F0;}
.il-dot{width:7px;height:7px;border-radius:50%;background:currentColor;display:inline-block;}

.il-muted{color:var(--il-muted);font-size:.88rem;}
.il-crumb{color:var(--il-muted);font-size:.85rem;margin-bottom:.2rem;}
.il-crumb b{color:var(--il-ink);font-weight:600;}
.il-side-title{font-weight:700;font-size:1.02rem;margin:.2rem 0 .1rem;}
.il-version{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.74rem;color:var(--il-muted);
  background:#F1F5F9;border-radius:8px;padding:6px 10px;margin-top:1rem;display:inline-block;}

/* Skor */
.il-score{display:flex;align-items:center;gap:20px;background:var(--il-green-soft);border:1px solid #A7F3D0;
  border-radius:14px;padding:18px 20px;}
.il-score--amber{background:var(--il-amber-soft);border-color:#FDE68A;}
.il-score--red{background:var(--il-red-soft);border-color:#FECACA;}
.il-score--gray{background:#F8FAFC;border-color:var(--il-line);}
.il-ring{--p:75;--c:#10B981;width:84px;height:84px;border-radius:50%;flex:none;display:grid;place-items:center;
  background:conic-gradient(var(--c) calc(var(--p) * 1%), #E2E8F0 0);}
.il-ring > span{width:64px;height:64px;border-radius:50%;background:#fff;display:grid;place-items:center;
  font-weight:800;font-size:1.35rem;}
.il-ring small{font-size:.75rem;color:var(--il-muted);font-weight:600;}
.il-score-main{flex:1;min-width:0;}
.il-score-kicker{font-size:.72rem;font-weight:700;letter-spacing:.04em;color:var(--il-muted);text-transform:uppercase;}
.il-score-value{font-size:1.5rem;font-weight:800;letter-spacing:-.02em;margin:.1rem 0 .5rem;}
.il-seg{display:flex;gap:6px;}
.il-seg-bar{height:6px;flex:1;border-radius:99px;}
.il-seg-labels{display:flex;gap:6px;margin-top:5px;font-size:.7rem;color:var(--il-muted);}
.il-seg-labels span{flex:1;}
.il-analysis{border:1px solid var(--il-line);border-radius:12px;padding:16px 18px;background:#fff;line-height:1.6;font-size:.95rem;}
.il-tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;}
.il-tile-info{border:1px solid var(--il-line);border-radius:12px;padding:10px 14px;background:#FAFBFF;}
.il-tile-info .k{font-size:.72rem;color:var(--il-muted);}
.il-tile-info .v{font-weight:700;font-size:.98rem;}
.il-file-chip{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.75rem;color:var(--il-muted);
  background:#F1F5F9;border-radius:8px;padding:4px 9px;}

/* Tabel riwayat */
.il-th{font-size:.72rem;font-weight:700;letter-spacing:.04em;color:var(--il-muted);text-transform:uppercase;}
.il-rowline{height:1px;background:var(--il-line);margin:.35rem 0 .55rem;}
.il-person{display:flex;align-items:center;gap:12px;min-width:0;}
.il-person b{display:block;font-size:.95rem;}
.il-person span{display:block;font-size:.8rem;color:var(--il-muted);overflow:hidden;text-overflow:ellipsis;}
.il-avatar{border-radius:50%;color:#fff;font-weight:700;display:grid;place-items:center;flex:none;}
.il-two b{display:block;font-size:.92rem;font-weight:600;}
.il-two span{display:block;font-size:.76rem;color:var(--il-muted);font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;}
.il-skor-cell{display:flex;align-items:center;gap:10px;}
.il-skor-cell .n{font-weight:800;font-size:1.05rem;}
.il-skor-cell .n small{color:var(--il-muted);font-weight:600;}
.il-skor-cell .seg{width:70px;}

/* Landing: hero, terminal, bento */
.il-hero-title{font-size:3.05rem;line-height:1.06;font-weight:800;letter-spacing:-.035em;margin:.9rem 0 1rem;}
.il-lead{font-size:1.08rem;line-height:1.6;color:#475569;max-width:34rem;}
.il-lead b{color:var(--il-ink);}
.il-facts{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:1rem;font-size:.85rem;color:var(--il-muted);}
.il-term{background:var(--il-night);color:#CBD5E1;border-radius:16px;padding:18px 20px;
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.8rem;line-height:1.75;
  box-shadow:0 18px 40px -22px rgba(15,23,42,.55);}
.il-term .bar{display:flex;justify-content:space-between;color:#94A3B8;margin-bottom:10px;}
.il-term .row{display:flex;gap:10px;padding:7px 0;border-top:1px solid #1E293B;}
.il-term .k{color:#64748B;min-width:84px;}
.il-term .ok{color:#34D399;} .il-term .warn{color:#FBBF24;} .il-term .bad{color:#F87171;}
.il-steps{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:.4rem 0 0;}
.il-step{background:#fff;border:1px solid var(--il-line);border-radius:14px;padding:14px 16px;}
.il-step i{font-style:normal;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.72rem;color:var(--il-muted);}
.il-step b{display:block;margin-top:6px;}
.il-step span{font-size:.82rem;color:var(--il-muted);}
.il-step--hl{border-color:var(--il-primary);background:var(--il-primary-soft);}
.il-section-title{font-size:1.9rem;font-weight:800;letter-spacing:-.03em;line-height:1.15;margin:2.4rem 0 1rem;max-width:36rem;}
.il-bento{display:grid;grid-template-columns:repeat(4,1fr);grid-auto-rows:minmax(150px,auto);gap:16px;}
.il-tile{background:#fff;border:1px solid var(--il-line);border-radius:18px;padding:22px 24px;}
.il-tile h3{margin:.2rem 0 .5rem;font-size:1.15rem;}
.il-tile p{color:#475569;font-size:.92rem;line-height:1.6;margin:0 0 .6rem;}
.il-tile--a{grid-column:span 2;grid-row:span 2;}
.il-tile--b{grid-column:span 2;background:var(--il-night);border-color:var(--il-night);}
.il-tile--b h3{color:#fff;} .il-tile--b p{color:#94A3B8;}
.il-stats{display:flex;gap:10px;flex-wrap:wrap;margin-top:8px;}
.il-stat{border:1px solid #334155;border-radius:12px;padding:8px 12px;color:#E2E8F0;}
.il-stat b{display:block;font-size:1.05rem;} .il-stat span{font-size:.75rem;color:#94A3B8;}
.il-flow{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:18px;
  background:var(--il-primary-soft);border:1px solid #D6DCF3;border-radius:14px;padding:18px 16px;}
.il-node{background:#fff;border:1px solid var(--il-line);border-radius:12px;padding:10px 12px;font-size:.8rem;text-align:center;min-width:92px;}
.il-node--ok{border-color:#6EE7B7;background:var(--il-green-soft);}
.il-node--no{border-color:#FCA5A5;background:var(--il-red-soft);color:var(--il-red);text-decoration:line-through;}
.il-layer{border:1px solid var(--il-line);border-radius:10px;padding:8px 12px;margin-top:8px;font-size:.84rem;background:#FAFBFF;}
.il-layer i{font-style:normal;font-family:ui-monospace,Menlo,Consolas,monospace;color:var(--il-muted);margin-right:8px;}
.il-code{background:var(--il-night);border-radius:12px;padding:12px 14px;font-family:ui-monospace,Menlo,Consolas,monospace;
  font-size:.76rem;color:#E2E8F0;line-height:1.6;margin-top:6px;}
.il-code .s{color:#FBBF24;} .il-code .n{color:#34D399;}
.il-footer{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-top:3rem;padding-top:1.2rem;
  border-top:1px solid var(--il-line);font-size:.8rem;color:var(--il-muted);}
@media (max-width: 900px){
  .il-steps{grid-template-columns:1fr 1fr;}
  .il-bento{grid-template-columns:1fr;}
  .il-tile--a,.il-tile--b{grid-column:auto;grid-row:auto;}
  .il-hero-title{font-size:2.2rem;}
}
"""

SIDEBAR_HIDE_CSS = (
    "[data-testid='stSidebar'],[data-testid='stSidebarCollapsedControl'],"
    "[data-testid='collapsedControl']{display:none !important;}"
)

# ----------------------------------------------------------------------------
# HELPER UMUM
# ----------------------------------------------------------------------------
def html_block(markup: str) -> str:
    """Rapikan HTML agar tidak dianggap blok kode oleh Markdown (hapus indentasi & baris kosong)."""
    return "\n".join(line.strip() for line in markup.strip().splitlines() if line.strip())


def render(markup: str) -> None:
    st.markdown(html_block(markup), unsafe_allow_html=True)


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def setup_page(title: str, sidebar: bool = True) -> None:
    """Wajib dipanggil PERTAMA di setiap halaman (st.set_page_config + tema)."""
    st.set_page_config(
        page_title=f"{title} · InterviewLens",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded" if sidebar else "collapsed",
    )
    css = THEME_CSS + ("" if sidebar else SIDEBAR_HIDE_CSS)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# --- Waktu (WIB = UTC+7, tanpa dependensi tzdata) ---
WIB = timezone(timedelta(hours=7))
_BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


def now_wib() -> datetime:
    return datetime.now(WIB)


def fmt_date(dt: datetime) -> str:
    return f"{dt.day} {_BULAN[dt.month - 1]} {dt.year}"


def fmt_time(dt: datetime) -> str:
    return f"{dt:%H:%M} WIB"


# ----------------------------------------------------------------------------
# KOMPONEN UI (HTML)
# ----------------------------------------------------------------------------
def badge(text: str, tone: str = "gray", dot: bool = False) -> str:
    d = '<span class="il-dot"></span>' if dot else ""
    return f'<span class="il-badge il-badge--{tone}">{d}{esc(text)}</span>'


def segments(score: int, labels: bool = False) -> str:
    color = SCORE_META[score][2]
    bars = "".join(
        f'<span class="il-seg-bar" style="background:{color if i < score else "#E2E8F0"}"></span>'
        for i in range(4)
    )
    out = f'<div class="il-seg">{bars}</div>'
    if labels:
        out += ('<div class="il-seg-labels"><span>1 · Kurang</span><span>2 · Cukup</span>'
                '<span>3 · Baik</span><span>4 · Sangat Baik</span></div>')
    return out


def ring(score: int) -> str:
    color = SCORE_META[score][2]
    return (f'<div class="il-ring" style="--p:{score / 4 * 100:.0f};--c:{color}">'
            f'<span>{score}<small>/4</small></span></div>')


def avatar(name: str, size: int = 38) -> str:
    parts = [p for p in str(name).split() if p]
    initials = "".join(p[0] for p in parts[:2]).upper() or "?"
    palette = ["#3F4F8F", "#0E7490", "#7C3AED", "#B45309", "#047857", "#BE185D"]
    color = palette[sum(ord(c) for c in str(name)) % len(palette)]
    return (f'<div class="il-avatar" style="width:{size}px;height:{size}px;background:{color};'
            f'font-size:{size * 0.38:.0f}px">{esc(initials)}</div>')


def eligibility(score: int):
    """Status kelayakan awal (saran bagi HR, bukan keputusan akhir)."""
    return ("Lolos Tahap Awal", "green") if score >= 3 else ("Perlu Review", "amber")


def score_tone(score: int) -> str:
    return {0: "gray", 1: "red", 2: "amber", 3: "", 4: ""}[score]


def score_card(score: int) -> str:
    label, _, _ = SCORE_META[score]
    tone = score_tone(score)
    cls = f"il-score il-score--{tone}" if tone else "il-score"
    return html_block(f"""
    <div class="{cls}">
      {ring(score)}
      <div class="il-score-main">
        <div class="il-score-kicker">Skor Jawaban</div>
        <div class="il-score-value">Score: {score}/4 – {esc(label)}</div>
        {segments(score, labels=True)}
      </div>
    </div>""")


# ----------------------------------------------------------------------------
# STATUS SISTEM
# ----------------------------------------------------------------------------
@st.cache_data(ttl=10, show_spinner=False)
def ollama_status() -> dict:
    """Cek nyata apakah Ollama menyala di localhost dan model sudah diunduh."""
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=1.5)
        r.raise_for_status()
        names = [m.get("name", "") for m in r.json().get("models", [])]
        return {"online": True, "has_model": any(n.startswith(OLLAMA_MODEL) for n in names)}
    except Exception:
        return {"online": False, "has_model": False}


def system_info() -> dict:
    return {"cores": os.cpu_count() or 0, "os": platform.system(), "machine": platform.machine()}


def status_chip() -> str:
    s = ollama_status()
    if not s["online"]:
        return badge("Ollama Offline", "red", dot=True)
    if not s["has_model"]:
        return badge(f"Ollama aktif · model {OLLAMA_MODEL} belum diunduh", "amber", dot=True)
    return badge("Ollama Localhost Active", "green", dot=True)


# ----------------------------------------------------------------------------
# AUTENTIKASI SIMULASI (lokal; BUKAN pengganti autentikasi produksi)
# ----------------------------------------------------------------------------
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def authenticate(email: str, password: str):
    """Validasi sederhana. Jika env INTERVIEWLENS_PASSWORD diset, kata sandi harus sama persis."""
    if not _EMAIL_RE.match(email or ""):
        return False, "Format email tidak valid."
    expected = os.getenv("INTERVIEWLENS_PASSWORD")
    if expected is not None:
        if hmac.compare_digest(password or "", expected):
            return True, ""
        return False, "Email atau kata sandi salah."
    if len(password or "") < 6:
        return False, "Kata sandi minimal 6 karakter."
    return True, ""


def is_authenticated() -> bool:
    return bool(st.session_state.get("authenticated"))


def login(email: str) -> None:
    st.session_state["authenticated"] = True
    st.session_state["user_email"] = email


def logout() -> None:
    for key in ("authenticated", "user_email", "result"):
        st.session_state.pop(key, None)
    st.switch_page(PAGE_HOME)


def require_login() -> None:
    pass 
   # """Alihkan ke halaman Login jika belum masuk."""
   # if not is_authenticated():
   #     st.session_state["login_notice"] = "Silakan masuk terlebih dahulu untuk membuka halaman tersebut."
   #     st.switch_page(PAGE_LOGIN)


def topbar() -> None:
    pass
   # """Bilah navigasi atas (menggantikan navigasi sidebar bawaan Streamlit)."""
   # c = st.columns([2.4, 1.0, 1.1, 1.1, 2.1, 1.1], vertical_alignment="center")
   # with c[0]:
    #    render('<div class="il-brand"><div class="il-brand-mark">⚡</div>InterviewLens</div>')
   # with c[1]:
   #     st.page_link(PAGE_HOME, label="Beranda")
   # with c[2]:
  #      st.page_link(PAGE_DASH, label="Penilaian")
   # with c[3]:
   #     st.page_link(PAGE_HISTORY, label="Riwayat")
   # with c[4]:
   #     render(f'<div style="text-align:right">{status_chip()}</div>')
 #   with c[5]:
    #    if is_authenticated():
    #        if st.button("Keluar", key="topbar_logout"):
    #            logout()
    #    else:
     #       st.page_link(PAGE_LOGIN, label="Masuk")


# ----------------------------------------------------------------------------
# PELAPORAN JSON (struktur sama dengan app.py sebelumnya)
# ----------------------------------------------------------------------------
def safe_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", (name or "Kandidat").strip()).strip("_") or "Kandidat"


def build_report(name, email, photo_name, question_id, score, reason, evaluated_at=None) -> dict:
    """Bangun laporan JSON akhir (kerangka identik dengan versi app.py sebelumnya)."""
    ts = (evaluated_at or now_wib()).strftime("%Y-%m-%d %H:%M:%S")
    interview_percentage = (score / 4) * 100
    total_final_score = (100 + interview_percentage) / 2  # Asumsi Project Score 100
    return {
        "success": True,
        "data": {
            "id": 131,  # ID Mockup
            "candidate": {"name": name, "email": email, "photoUrl": photo_name or "default.png"},
            "certification": {
                "abbreviatedType": "DCML",
                "normalType": "DEV_CERTIFICATION_MACHINE_LEARNING",
                "submittedAt": ts,
                "status": "FINISHED",
                "projectType": "dcml_package_1",
                "interviewQuestionSets": 1,
                "examScore": total_final_score,
                "autoGraderProjectScore": 100,
                "downloadProjectUrl": "https://github.com/hayeee14/project-ML-ASAH-FT",
                "isReviewedByMe": False,
                "isAlreadyReviewedByMe": False,
                "assess": {"project": False, "interviews": True},
            },
            "reviewChecklists": {
                "project": [],
                "interviews": [{
                    "positionId": question_id,
                    "question": QUESTION_DB[question_id],
                    "isVideoExist": True,
                    "recordedVideoUrl": "https://drive.google.com/file/d/mock-url-video/view",  # link dummy
                }],
            },
            "pastReviews": [{
                "assessorProfile": {"id": 47, "name": "AI Assessor System", "photoUrl": "xxx"},
                "decision": "PASSED" if score >= 3 else "REVIEW NEEDED",
                "reviewedAt": ts,
                "scoresOverview": {
                    "project": 100,
                    "interview": round(interview_percentage, 1),
                    "total": round(total_final_score, 1),
                },
                "reviewChecklistResult": {
                    "project": [],
                    "interviews": {
                        "minScore": 0,
                        "maxScore": 4,
                        "scores": [{"id": question_id, "score": score, "reason": reason}],
                    },
                },
                "notes": "Automated assessment utilizing Facebook Wav2Vec2 (CPU) for transcription and Ollama REST API (Zephyr) for local reasoning.",
            }],
        },
    }


def report_json(report: dict) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False)
