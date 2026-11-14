"""Halaman Autentikasi (simulasi lokal)."""
import streamlit as st

from utils import (PAGE_DASH, PAGE_HOME, authenticate, badge, is_authenticated, login, ollama_status, render,
                   setup_page)

setup_page("Login", sidebar=False)

if is_authenticated():
    st.switch_page(PAGE_DASH)

render('<div class="il-file-chip">interviewlens@localhost ~ /auth</div>')

_, mid, _ = st.columns([1, 1.25, 1])
with mid:
    st.write("")
    with st.container(key="card_login"):
        render("""
        <div style="text-align:center">
          <div class="il-brand-mark il-brand-mark--lg">⚡</div>
          <div style="font-size:1.5rem;font-weight:800;letter-spacing:-.02em">InterviewLens</div>
        </div>""")
        render(f'<div style="text-align:center;margin:.3rem 0 1rem">{badge("Secure localhost authentication", "green", dot=True)}</div>')

        notice = st.session_state.pop("login_notice", None)
        if notice:
            st.info(notice)

        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email Perusahaan / HR", placeholder="nama@perusahaan.co.id")
            password = st.text_input("Kata Sandi (Password)", type="password")
            submitted = st.form_submit_button("Masuk ke Dashboard", type="primary")

        if submitted:
            ok, message = authenticate(email.strip(), password)
            if ok:
                login(email.strip())
                st.switch_page(PAGE_DASH)
            else:
                st.error(message)

        render("""
        <div style="border:1px solid #A7F3D0;background:#ECFDF5;border-radius:12px;padding:12px 14px;font-size:.86rem;color:#065F46;margin-top:.6rem">
          Seluruh pemrosesan berjalan lokal di perangkat Anda. <b>Autentikasi ini simulasi untuk demo lokal</b>
          dan bukan pengganti sistem login produksi.
        </div>""")
        render('<div style="text-align:center;margin-top:1rem" class="il-muted">Belum punya akun instansi? '
               '<b style="color:#3F4F8F">Hubungi Administrator IT lokal.</b></div>')

    s = ollama_status()
    tone = "green" if s["online"] and s["has_model"] else ("amber" if s["online"] else "red")
    text = ("Ollama Local Node: Online" if s["online"] and s["has_model"]
            else "Ollama Local Node: model belum diunduh" if s["online"] else "Ollama Local Node: Offline")
    render(f'<div style="text-align:center;margin-top:1rem">{badge(text + " · localhost:11434", tone, dot=True)}</div>')

st.page_link(PAGE_HOME, label="← Kembali ke Beranda")
