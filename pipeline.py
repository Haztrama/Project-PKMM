"""pipeline.py - Logika AI: ekstraksi audio (FFmpeg), STT Wav2Vec2 (CPU), penilaian LLM via Ollama + fallback kata kunci.

Modul ini memuat pustaka berat (transformers, librosa), jadi hanya diimpor oleh halaman Dashboard.
"""
import os
import re
import shutil
import subprocess

import imageio_ffmpeg
import librosa
import requests
import streamlit as st
from transformers import pipeline

from knowledge import QUESTION_DB, TOPIC_KEYWORDS
from utils import ASR_MODELS, OLLAMA_MODEL, OLLAMA_TIMEOUT, OLLAMA_URL, TARGET_SR

# --- KONFIGURASI SISTEM ---
try:
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    # Fallback jika terjadi kendala, arahkan ke string default sistem
    ffmpeg_path = "ffmpeg"


@st.cache_resource(show_spinner=False)
def load_stt(language: str = "Inggris"):
    """Muat model Wav2Vec2 pada CPU (device=-1). Di-cache per bahasa agar tidak dimuat ulang."""
    return pipeline("automatic-speech-recognition", model=ASR_MODELS[language], device=-1)


# --- FUNGSI UTILITAS ---
def convert_video_to_audio(video_path, audio_path):
    """
    Ekstraksi audio dari video menggunakan subprocess FFmpeg.
    """
    try:
        ffmpeg_cmd = "ffmpeg.exe" if os.path.exists("ffmpeg.exe") else "ffmpeg"
        command = [
            ffmpeg_cmd, "-i", video_path, "-vn",
            "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            audio_path, "-y"
        ]

        # Sembunyikan window terminal di Windows
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
        return True
    except Exception:
        return False


def audio_duration(audio_path) -> float:
    """Durasi audio dalam detik (0.0 jika gagal dibaca)."""
    try:
        return float(librosa.get_duration(path=audio_path))
    except Exception:
        return 0.0


def transcribe(audio_path, language="Inggris"):
    """
    Transkripsi audio ke teks dengan Wav2Vec2 (CPU).
    Audio dimuat & di-resample ke 16 kHz mono dengan librosa.
    """
    model_stt = load_stt(language)
    speech, _ = librosa.load(audio_path, sr=TARGET_SR, mono=True)
    result = model_stt(
        {"raw": speech, "sampling_rate": TARGET_SR},
        chunk_length_s=30,   # potong audio panjang agar tidak OOM
        stride_length_s=5    # overlap antar potongan
    )
    # Output Wav2Vec2 berupa HURUF KAPITAL tanpa tanda baca -> lowercase
    return result["text"].lower().strip()


def keyword_assessment(text, question_id):
    """
    Penilaian berbasis keyword. Dipakai sebagai fallback
    jika LLM tidak tersedia atau outputnya tidak bisa di-parse.
    - 1: 0 keyword | 2: 1-2 keyword | 3: 3-5 keyword | 4: >5 keyword
    """
    target_keywords = TOPIC_KEYWORDS.get(question_id, [])
    text_lower = text.lower()

    found_keywords = [k for k in target_keywords if k in text_lower]
    hit_count = len(set(found_keywords))

    if hit_count == 0:
        return 1, "The answer does not contain relevant technical keywords for this topic."
    elif hit_count <= 2:
        return 2, f"Basic understanding. Mentioned keywords: {', '.join(found_keywords)}."
    elif hit_count <= 5:
        return 3, f"Solid technical explanation. Key concepts covered: {', '.join(found_keywords)}."
    else:
        return 4, f"Comprehensive and detailed response. Extensive vocabulary used: {', '.join(found_keywords)}."


def assess_answer(text, question_id, language="Inggris"):
    """
    Skor dan alasan dihasilkan LLM Zephyr via REST API Ollama (localhost), format "Score | Reason".
    Mengembalikan (skor, alasan, metode) dengan metode: "validasi" | "llm" | "fallback".
    - 0: teks < 10 karakter
    - 1-4: dinilai LLM; jika Ollama mati / error / format tidak valid -> keyword_assessment
    """
    if len(text) < 10:
        return 0, "No audible response detected or response too short.", "validasi"

    question_text = QUESTION_DB.get(question_id, "General interview question")
    lang_note = ""
    if language == "Indonesia":
        lang_note = "\nNote: The candidate answer is an automatic transcript in Indonesian and may contain errors. Write the Reason in English.\n"

    prompt_text = f"""You are a Senior Technical Recruiter. Evaluate this interview answer.

Question: "{question_text}"
Candidate Answer: "{text}"
{lang_note}
Task:
1. Give a Score (1-4) based on depth, clarity, and technical correctness.
2. Write a short Reason (max 1 sentence).

Rubric:
1: Poor/Irrelevant.
2: Basic/General.
3: Good/Specific.
4: Excellent/Detailed.

Output Format: Score | Reason
Example: 3 | The candidate gave a relevant answer with some specific details.
Respond with exactly one line in this format and nothing else."""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt_text,
        "stream": False,
        "options": {"temperature": 0, "num_predict": 80}
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
        response.raise_for_status()
        output = response.json()["response"].strip()

        match = re.search(r"(?:score\s*[:=]?\s*)?\b([1-4])\b(?:\s*/\s*4)?\s*\|\s*(.+)", output, re.IGNORECASE | re.DOTALL)
        if match:
            score = int(match.group(1))
            reason = match.group(2).strip().split("\n")[0].strip()
            if reason:
                return score, reason, "llm"
    except Exception as e:
        print(f"[Ollama] Gagal memanggil API, memakai fallback keyword: {e}")

    score, reason = keyword_assessment(text, question_id)
    return score, reason, "fallback"
