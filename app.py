"""app.py - Halaman Utama (Landing Page) InterviewLens.

Jalankan dengan:  streamlit run app.py
"""
import streamlit as st

from utils import (APP_VERSION, OLLAMA_MODEL, PAGE_DASH, PAGE_HISTORY, badge, is_authenticated,
                   ollama_status, render, setup_page, system_info, topbar)

setup_page("Beranda", sidebar=False)
topbar()

status = ollama_status()
info = system_info()

# ----------------------------------------------------------------------------
# HERO
# ----------------------------------------------------------------------------
left, right = st.columns([1.1, 1], gap="large", vertical_alignment="center")

with left:
    render(f"""
    <div style="margin-top:1.4rem">{badge("Privasi Data 100% Lokal · Selaras UU PDP · Tanpa Cloud / Tanpa GPU", "green", dot=True)}</div>
    <div class="il-hero-title">Sistem Penilaian Wawancara Otomatis yang Berjalan Mandiri di Perangkat Anda.</div>
    <div class="il-lead">Mengintegrasikan <b>Wav2Vec2</b> dan <b>Zephyr-7B LLM</b> secara luring pada CPU standar untuk
    rekrutmen yang cepat, transparan, dan aman.</div>
    """)
    b1, b2, _ = st.columns([1.5, 1, 0.8])
    with b1:
        if st.button("Buka Dashboard Penilaian", type="primary", key="cta_dashboard"):
            st.switch_page(PAGE_DASH)
    with b2:
        if is_authenticated():
            if st.button("Riwayat", key="cta_history"):
                st.switch_page(PAGE_HISTORY)
        elif st.button("Masuk", key="cta_login"):
            st.switch_page(PAGE_LOGIN)
    render("""
    <div class="il-facts">
      <span>CPU 4 inti · RAM 16 GB</span><span>Luring setelah model terpasang</span><span>Data tetap di perangkat</span>
    </div>""")

with right:
    if not status["online"]:
        ollama_line = '<span class="bad">Offline</span> <span class="k">(localhost:11434)</span>'
    elif not status["has_model"]:
        ollama_line = f'<span class="warn">Connected, model {OLLAMA_MODEL} belum diunduh</span>'
    else:
        ollama_line = '<span class="ok">Connected</span> <span class="k">(localhost:11434)</span>'
    render(f"""
    <div class="il-term">
      <div class="bar"><span>interviewlens@localhost ~ system-monitor</span><span class="ok">● LIVE</span></div>
      <div class="row"><span class="k">STATUS</span><span>Ollama REST API: {ollama_line}</span></div>
      <div class="row"><span class="k">HARDWARE</span><span>Prosesor: {info["cores"]} inti ({info["machine"]}, CPU-only mode)</span></div>
      <div class="row"><span class="k">PRIVASI</span><span>Inferensi hanya memanggil <span class="ok">localhost</span></span></div>
      <div class="row"><span class="k">BENCHMARK</span><span>WER: 34,2% | Fallback uptime: 100%<br>
        <span class="k">hasil uji internal (Laporan Akhir PKMM)</span></span></div>
    </div>""")

# ----------------------------------------------------------------------------
# ARSITEKTUR CPU (urutan nyata -> penomoran sesuai)
# ----------------------------------------------------------------------------
render("""
<div class="il-section-title">Satu pipeline, nol koneksi keluar.</div>
<div class="il-steps">
  <div class="il-step"><i>01</i><b>Video .mp4</b><span>FFmpeg · 16 kHz mono</span></div>
  <div class="il-step"><i>02</i><b>Wav2Vec2</b><span>Speech-to-text lokal (CPU)</span></div>
  <div class="il-step il-step--hl"><i>03</i><b>Zephyr-7B</b><span>via Ollama, kuantisasi 4-bit</span></div>
  <div class="il-step"><i>04</i><b>Rubrik + JSON</b><span>Skor 0–4 dengan alasan tertulis</span></div>
</div>
""")

# ----------------------------------------------------------------------------
# BENTO GRID FITUR UTAMA
# ----------------------------------------------------------------------------
render("""
<div class="il-section-title">Dirancang untuk HR yang tidak mau berkompromi soal privasi.</div>
<div class="il-bento">
  <div class="il-tile il-tile--a">
    <h3>Kedaulatan Data Penuh</h3>
    <p>Rekaman suara dan video pelamar diproses di mesin lokal. Tidak ada API pihak ketiga dan tidak ada
    server asing saat inferensi: transkripsi dan penalaran LLM berjalan di perangkat Anda.</p>
    <div class="il-flow">
      <div class="il-node">audio.wav</div>
      <div class="il-node il-node--ok"><b>127.0.0.1</b><br>mesin lokal</div>
      <div class="il-node">report.json</div>
      <div class="il-node il-node--no">cloud</div>
    </div>
  </div>
  <div class="il-tile il-tile--b">
    <h3>Optimasi Perangkat Keras CPU</h3>
    <p>Zephyr-7B berjalan lewat Ollama pada kuantisasi 4-bit, dan Wav2Vec2-base hanya sekitar 95 juta parameter,
    sehingga pipeline cukup CPU standar tanpa GPU NVIDIA.</p>
    <div class="il-stats">
      <div class="il-stat"><b>≈ 4,1 GB</b><span>unduhan model LLM</span></div>
      <div class="il-stat"><b>≈ 95 jt</b><span>parameter STT (base)</span></div>
      <div class="il-stat"><b>0</b><span>GPU dibutuhkan</span></div>
    </div>
  </div>
  <div class="il-tile">
    <h3>Fallback Berlapis</h3>
    <p>Sistem tetap berjalan meski transkripsi keliru karena logat lokal.</p>
    <div class="il-layer"><i>L1</i>Validasi masukan</div>
    <div class="il-layer"><i>L2</i>Penilaian LLM</div>
    <div class="il-layer"><i>L3</i>Rubrik kata kunci</div>
  </div>
  <div class="il-tile">
    <h3>Rubrik Audit &amp; Ekspor JSON</h3>
    <p>Skor 0–4 dengan alasan tertulis yang dapat diaudit manusia.</p>
    <div class="il-code">
      <div>{</div>
      <div style="padding-left:14px">"score": <span class="n">3</span>,</div>
      <div style="padding-left:14px">"reason": <span class="s">"Struktur jelas…"</span></div>
      <div>}</div>
    </div>
  </div>
</div>
""")

render(f"""
<div class="il-footer">
  <span>© 2025 Tim InterviewLens · v{APP_VERSION}</span>
  <span>Dikembangkan untuk PKMM AST-PTMA 2025 · Penilaian bersifat alat bantu, keputusan akhir tetap pada HR</span>
</div>
""")
