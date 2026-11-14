"""Log Riwayat Penilaian: tabel kandidat dengan filter, ekspor CSV, unduh JSON, dan detail."""
import pandas as pd
import streamlit as st

from knowledge import JOB_ROLES
from storage import list_assessments
from utils import (SCORE_META, avatar, badge, eligibility, esc, fmt_date, fmt_time, ollama_status, render,
                   require_login, safe_filename, score_card, segments, setup_page, topbar)

setup_page("Riwayat Kandidat", sidebar=False)
require_login()
topbar()

PAGE_SIZE = 10
COLS = [2.9, 2.0, 1.6, 1.7, 1.8, 1.05, 1.05]

rows = list_assessments()
s = ollama_status()

render(f"""
<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:12px;flex-wrap:wrap;margin:.6rem 0 1rem">
  <div>
    <div class="il-crumb">Assessment log</div>
    <h1 style="margin:0;font-size:2rem">Riwayat Penilaian</h1>
    <div class="il-muted">Seluruh hasil evaluasi wawancara yang diproses secara lokal oleh InterviewLens.</div>
  </div>
  <div>{badge("Ollama · localhost:11434" if s["online"] else "Ollama offline", "green" if s["online"] else "red", dot=True)}</div>
</div>
""")


@st.dialog("Detail Penilaian", width="large")
def show_detail(r: dict) -> None:
    label, tone = eligibility(r["score"])
    render(f"""
    <div class="il-person" style="margin-bottom:.8rem">{avatar(r["name"], 46)}
      <div><b>{esc(r["name"])}</b><span>{esc(r["email"] or "-")} · {esc(r["position"])}</span></div>
    </div>
    <div class="il-muted" style="margin-bottom:.8rem">Dievaluasi {fmt_date(r["evaluated_dt"])}, {fmt_time(r["evaluated_dt"])}</div>
    """)
    render(score_card(r["score"]))
    render(f"""
    <div class="il-th" style="margin:1rem 0 .4rem">Pertanyaan Q{r["question_id"]}</div>
    <div class="il-analysis">{esc(r["question"])}</div>
    <div class="il-th" style="margin:1rem 0 .4rem">Analisis AI</div>
    <div class="il-analysis">{esc(r["reason"])}
      <div class="il-tags">{badge(label, tone)}{badge("Contoh data" if r["is_sample"] else "Metode: " + str(r["method"]), "gray")}</div>
    </div>""")
    st.download_button("Unduh Laporan JSON", data=r["report_json"], file_name=f"Assessment_{safe_filename(r['name'])}.json",
                       mime="application/json", type="primary", key=f"dlg_{r['id']}")


# ----------------------------------------------------------------------------
# FILTER
# ----------------------------------------------------------------------------
with st.container(key="card_table"):
    f1, f2, f3, f4 = st.columns([3.2, 2, 2, 1.7], vertical_alignment="center")
    query = f1.text_input("Cari", placeholder="Cari berdasarkan nama kandidat atau email...",
                          label_visibility="collapsed", key="hist_q")
    role_filter = f2.selectbox("Posisi", ["Semua Posisi"] + list(JOB_ROLES.keys()),
                               label_visibility="collapsed", key="hist_role")
    score_range = f3.slider("Rentang skor", 0, 4, (0, 4), label_visibility="collapsed", key="hist_score")

    filtered = [
        r for r in rows
        if (not query or query.lower() in r["name"].lower() or query.lower() in (r["email"] or "").lower())
        and (role_filter == "Semua Posisi" or r["position"] == role_filter)
        and score_range[0] <= r["score"] <= score_range[1]
    ]

    df = pd.DataFrame([{
        "Nama Kandidat": r["name"], "Email": r["email"], "Posisi Dilamar": r["position"],
        "Tanggal Evaluasi": f"{fmt_date(r['evaluated_dt'])} {fmt_time(r['evaluated_dt'])}",
        "Skor Akhir": f"{r['score']}/4", "Status Kelayakan": eligibility(r["score"])[0],
    } for r in filtered])
    f4.download_button("Ekspor Rekap CSV", data=df.to_csv(index=False).encode("utf-8-sig"),
                       file_name="rekap_penilaian.csv", mime="text/csv", key="export_csv")

    # --- Pagination sederhana ---
    total_pages = max(1, -(-len(filtered) // PAGE_SIZE))
    page = 1
    if total_pages > 1:
        page = st.number_input("Halaman", 1, total_pages, 1, key="hist_page")
    page_rows = filtered[(page - 1) * PAGE_SIZE: page * PAGE_SIZE]

    st.markdown('<div class="il-rowline" style="margin-top:.9rem"></div>', unsafe_allow_html=True)
    header = st.columns(COLS, vertical_alignment="center")
    for col, title in zip(header, ["Nama Kandidat", "Posisi Dilamar", "Tanggal Evaluasi", "Skor Akhir", "Status Kelayakan", "", "Aksi"]):
        col.markdown(f'<div class="il-th">{title}</div>', unsafe_allow_html=True)
    st.markdown('<div class="il-rowline"></div>', unsafe_allow_html=True)

    if not page_rows:
        st.info("Tidak ada data yang cocok dengan filter.")

    for r in page_rows:
        label, tone = eligibility(r["score"])
        sample_badge = badge("Contoh", "gray") if r["is_sample"] else ""
        c = st.columns(COLS, vertical_alignment="center")
        c[0].markdown(f'<div class="il-person">{avatar(r["name"])}<div><b>{esc(r["name"])} {sample_badge}</b>'
                      f'<span>{esc(r["email"] or "-")}</span></div></div>', unsafe_allow_html=True)
        c[1].markdown(f'<div style="font-size:.92rem;font-weight:600">{esc(r["position"])}</div>', unsafe_allow_html=True)
        c[2].markdown(f'<div class="il-two"><b>{fmt_date(r["evaluated_dt"])}</b><span>{fmt_time(r["evaluated_dt"])}</span></div>',
                      unsafe_allow_html=True)
        c[3].markdown(f'<div class="il-skor-cell"><div class="n">{r["score"]}<small>/4</small></div>'
                      f'<div><div class="seg">{segments(r["score"])}</div>'
                      f'<div class="il-muted" style="font-size:.74rem">{SCORE_META[r["score"]][0]}</div></div></div>',
                      unsafe_allow_html=True)
        c[4].markdown(badge(label, tone, dot=True), unsafe_allow_html=True)
        c[5].download_button("Unduh JSON", data=r["report_json"], file_name=f"Assessment_{safe_filename(r['name'])}.json",
                             mime="application/json", key=f"dl_{r['id']}")
        if c[6].button("Lihat Detail", key=f"det_{r['id']}"):
            show_detail(r)
        st.markdown('<div class="il-rowline"></div>', unsafe_allow_html=True)

    render(f"""
    <div class="il-muted">Menampilkan <b>{len(page_rows)}</b> dari <b>{len(filtered)}</b> data kandidat tersimpan di database
    lokal (SQLite). Status kelayakan adalah saran awal; keputusan akhir tetap pada HR.</div>""")

render('<div class="il-footer"><span>© 2025 InterviewLens · v1.0.0</span>'
       '<span>Data riwayat hanya tersimpan di perangkat ini (interviewlens.db)</span></div>')
