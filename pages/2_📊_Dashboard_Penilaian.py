"""Workspace Penilaian Utama: video kandidat (kiri) dan hasil analisis AI (kanan)."""
import os
import shutil
import tempfile

import streamlit as st

from knowledge import JOB_ROLES, QUESTION_DB
from utils import (ASR_MODELS, SCORE_META, badge, build_report, esc, fmt_date, fmt_time, now_wib, render,
                   report_json, require_login, safe_filename, score_card, setup_page, topbar)

setup_page("Dashboard Penilaian")
require_login()

from pipeline import assess_answer, audio_duration, convert_video_to_audio, transcribe  # noqa: E402 (impor berat)
from storage import add_assessment, init_db  # noqa: E402

init_db()
topbar()

MAX_PHOTO_BYTES = 5 * 1024 * 1024
METHOD_TAG = {
    "llm": ("LLM · Zephyr-7B via Ollama", "blue"),
    "fallback": ("Fallback kata kunci (LLM tidak tersedia / format tidak valid)", "amber"),
    "validasi": ("Validasi masukan (jawaban terlalu pendek)", "gray"),
}

# ----------------------------------------------------------------------------
# SIDEBAR: PROFIL KANDIDAT
# ----------------------------------------------------------------------------
with st.sidebar:
    render('<div class="il-side-title">Profil Kandidat</div>'
           '<div class="il-muted">Lengkapi metadata kandidat sebelum penilaian.</div>')
    cand_name = st.text_input("Nama Lengkap", key="cand_name", placeholder="mis. Rizky Pratama")
    cand_email = st.text_input("Email", key="cand_email", placeholder="nama@email.com")
    selected_role = st.selectbox("Posisi yang Dilamar", list(JOB_ROLES.keys()), key="cand_role")
    language = st.selectbox("Bahasa Wawancara", list(ASR_MODELS.keys()), key="cand_lang")
    if language == "Indonesia":
        st.caption("Mode Indonesia bersifat eksperimental: model STT berbeda (XLSR, lebih besar dan lebih lambat di CPU), "
                   "sedangkan bank pertanyaan dan kata kunci fallback berbahasa Inggris.")
    photo = st.file_uploader("Foto Profil", type=["jpg", "jpeg", "png"], key="cand_photo")
    if photo is not None:
        if photo.size > MAX_PHOTO_BYTES:
            st.warning("Foto melebihi 5 MB dan diabaikan.")
            photo = None
        else:
            st.image(photo, width=96)
    render('<div class="il-version">● Versi Sistem: 1.0.0 (Localhost)</div>')

# ----------------------------------------------------------------------------
# PILIH PERTANYAAN
# ----------------------------------------------------------------------------
role_questions = JOB_ROLES[selected_role]
if st.session_state.get("q_select") not in role_questions:
    st.session_state["q_select"] = role_questions[0]


def _step(delta: int) -> None:
    qs = JOB_ROLES[st.session_state["cand_role"]]
    cur = st.session_state.get("q_select")
    i = qs.index(cur) if cur in qs else 0
    st.session_state["q_select"] = qs[(i + delta) % len(qs)]


q_id = st.session_state["q_select"]
result_visible = False  # True bila hasil analisis untuk video + pertanyaan saat ini sedang ditampilkan

# Header halaman
display_name = (cand_name or "").strip() or "Kandidat baru"
h1, h2 = st.columns([4, 1.2], vertical_alignment="center")
with h1:
    render(f"""
    <div class="il-crumb">Penilaian › <b>{esc(display_name)}</b></div>
    <h1 style="margin:0 0 .15rem;font-size:2.1rem">Sistem Penilaian Interview AI</h1>
    <div class="il-muted">Target posisi: <b style="color:#3F4F8F">{esc(selected_role)}</b></div>
    """)
status_slot = h2.empty()

with st.container(key="card_question"):
    qa, qb, qc, qd = st.columns([6, 1.1, 1.1, 1.3], vertical_alignment="center")
    with qa:
        st.selectbox("Pilih Pertanyaan Interview", role_questions, key="q_select",
                     format_func=lambda x: f"Q{x}: {QUESTION_DB[x]}")
    q_pos = role_questions.index(st.session_state["q_select"]) + 1
    with qb:
        render(f'<div class="il-th">Pertanyaan</div><div style="font-weight:700">{q_pos} <span class="il-muted">/ {len(role_questions)}</span></div>')
    duration_slot = qc.empty()
    with qd:
        p, n = st.columns(2)
        p.button("‹", key="q_prev", on_click=_step, args=(-1,))
        n.button("›", key="q_next", on_click=_step, args=(1,))

q_id = st.session_state["q_select"]
st.write("")

col_vid, col_res = st.columns(2, gap="large")

# ----------------------------------------------------------------------------
# KOLOM KIRI: REKAMAN KANDIDAT
# ----------------------------------------------------------------------------
with col_vid:
    with st.container(key="card_video"):
        header_slot = st.empty()
        uploaded_video = st.file_uploader("Unggah video jawaban", type=["mp4", "mov", "avi", "webm"],
                                          key="video_upload", label_visibility="collapsed")
        if uploaded_video is not None:
            header_slot.markdown(
                f'<div class="il-card-title"><span>Rekaman Kandidat</span><span class="il-file-chip">{esc(uploaded_video.name)}</span></div>',
                unsafe_allow_html=True)
            st.video(uploaded_video)
            size_mb = uploaded_video.size / (1024 * 1024)
            ext = os.path.splitext(uploaded_video.name)[1].lstrip(".").upper() or "-"
            t1, t2, t3 = st.columns(3)
            for col, key, val in ((t1, "Bahasa", language), (t2, "Ukuran", f"{size_mb:.1f} MB"), (t3, "Format", ext)):
                col.markdown(f'<div class="il-tile-info"><div class="k">{key}</div><div class="v">{esc(val)}</div></div>',
                             unsafe_allow_html=True)
        else:
            header_slot.markdown('<div class="il-card-title"><span>Rekaman Kandidat</span></div>', unsafe_allow_html=True)
            st.caption("Unggah video jawaban (.mp4, .mov, .avi, .webm) untuk mulai penilaian.")


# ----------------------------------------------------------------------------
# PIPELINE ANALISIS
# ----------------------------------------------------------------------------
def run_analysis(video, question_id: int, lang: str):
    """Ekstraksi audio -> Wav2Vec2 (CPU) -> penilaian LLM/fallback. Berkas sementara dihapus setelah selesai."""
    workdir = tempfile.mkdtemp(prefix="interviewlens_")
    try:
        video_path = os.path.join(workdir, os.path.basename(video.name))
        audio_path = os.path.splitext(video_path)[0] + ".wav"
        with open(video_path, "wb") as f:
            f.write(video.getbuffer())

        with st.status("Sedang memproses...", expanded=True) as status:
            st.write("Mengekstrak audio (FFmpeg, 16 kHz mono)...")
            if not convert_video_to_audio(video_path, audio_path):
                status.update(label="Gagal memproses video", state="error")
                st.error("Gagal memproses file video. Cek formatnya.")
                return None

            st.write(f"Transkripsi suara (Wav2Vec2, CPU, bahasa: {lang})... pemuatan pertama dapat memakan waktu.")
            transcript = transcribe(audio_path, lang)
            duration = audio_duration(audio_path)

            st.write("Melakukan penilaian teknis (Zephyr-7B via Ollama / fallback)...")
            score, reason, method = assess_answer(transcript, question_id, lang)
            status.update(label="Analisis selesai", state="complete", expanded=False)
    except Exception as exc:  # model gagal dimuat, dsb.
        st.error(f"Terjadi kesalahan saat analisis: {exc}")
        return None
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    name = (st.session_state.get("cand_name") or "").strip() or "Kandidat Tanpa Nama"
    email = (st.session_state.get("cand_email") or "").strip()
    photo_name = photo.name if photo is not None else ""
    processed_at = now_wib()
    report = build_report(name, email, photo_name, question_id, score, reason, processed_at)
    add_assessment(name, email, selected_role, question_id, score, reason, method, lang, report)
    return {
        "key": (video.name, video.size, question_id, lang),
        "score": score, "reason": reason, "method": method, "transcript": transcript,
        "duration": duration, "processed_at": processed_at, "name": name,
        "report_json": report_json(report), "question_id": question_id,
    }


# ----------------------------------------------------------------------------
# KOLOM KANAN: HASIL PENILAIAN AI
# ----------------------------------------------------------------------------
with col_res:
    with st.container(key="card_result"):
        result_head = st.empty()
        current_key = (uploaded_video.name, uploaded_video.size, q_id, language) if uploaded_video is not None else None

        if uploaded_video is None:
            result_head.markdown('<div class="il-card-title"><span>Hasil Penilaian AI</span></div>', unsafe_allow_html=True)
            st.caption("Hasil analisis akan tampil di sini setelah video diunggah dan dianalisis.")
        else:
            if st.button("Analisis Jawaban", type="primary", key="btn_analyze"):
                outcome = run_analysis(uploaded_video, q_id, language)
                if outcome is not None:
                    st.session_state["result"] = outcome

            res = st.session_state.get("result")
            if res and res["key"] == current_key:
                result_head.markdown(
                    f'<div class="il-card-title"><span>Hasil Penilaian AI</span>'
                    f'<span class="il-muted">Diproses {fmt_date(res["processed_at"])}, {fmt_time(res["processed_at"])}</span></div>',
                    unsafe_allow_html=True)
                render(score_card(res["score"]))
                tag_text, tag_tone = METHOD_TAG[res["method"]]
                render(f"""
                <div class="il-th" style="margin:1rem 0 .4rem">Analisis AI</div>
                <div class="il-analysis">{esc(res["reason"])}
                  <div class="il-tags">{badge(tag_text, tag_tone)}{badge(f"Skala 0–4 · {SCORE_META[res['score']][0]}", "gray")}</div>
                </div>""")
                with st.expander("Lihat Transkripsi Lengkap"):
                    st.write(res["transcript"] or "(transkrip kosong)")
                    st.caption("Wav2Vec2 menghasilkan teks huruf kecil tanpa tanda baca; galat dapat terjadi pada logat lokal dan istilah teknis.")
                st.download_button("Unduh Laporan JSON", data=res["report_json"],
                                   file_name=f"Assessment_{safe_filename(res['name'])}.json",
                                   mime="application/json", type="primary", key="dl_report")
                st.caption("Laporan mencakup skor, analisis, dan metadata. Hasil juga tersimpan di Riwayat Penilaian (SQLite lokal).")
                result_visible = True
                status_slot.markdown(badge("Analisis selesai", "green", dot=True), unsafe_allow_html=True)
                duration_slot.markdown(
                    f'<div class="il-th">Durasi</div><div style="font-weight:700">{int(res["duration"] // 60):02d}:{int(res["duration"] % 60):02d}</div>',
                    unsafe_allow_html=True)
            else:
                result_head.markdown('<div class="il-card-title"><span>Hasil Penilaian AI</span></div>', unsafe_allow_html=True)
                st.caption("Klik **Analisis Jawaban** untuk memproses video dan pertanyaan yang dipilih.")

if not result_visible:
    status_slot.markdown(badge("Menunggu analisis", "gray", dot=True), unsafe_allow_html=True)
    duration_slot.markdown('<div class="il-th">Durasi</div><div style="font-weight:700">—</div>', unsafe_allow_html=True)
