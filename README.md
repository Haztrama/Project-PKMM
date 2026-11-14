# InterviewLens: Sistem Penilaian Wawancara Kerja Otomatis Berbasis Speech Recognition Wav2Vec2 dan Large Language Model Lokal

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red)
![AI Model](https://img.shields.io/badge/Model-Wav2Vec2%20%7C%20Zephyr--7B%20(Ollama)-green)
![Architecture](https://img.shields.io/badge/Architecture-CPU%20Only%20%7C%20100%25%20Local-orange)

**InterviewLens** adalah purwarupa sistem penilaian wawancara kerja otomatis berbasis kecerdasan buatan (*Artificial Intelligence*) yang dirancang khusus untuk berjalan secara mandiri (*luring/offline*) pada perangkat CPU standar tanpa memerlukan GPU diskrit ataupun layanan *cloud* pihak ketiga[cite: 1, 17]. Sistem ini mengintegrasikan ekstraksi audio FFmpeg, transkripsi **Wav2Vec2**, penskoran berbasis rubrik 0–4 serta alasan tertulis oleh **Zephyr-7B** melalui **Ollama** pada *localhost*, mekanisme *fallback* kata kunci berlapis, serta antarmuka web interaktif berbasis **Streamlit**[cite: 1, 21].

> **Program Kreativitas Mahasiswa Karsa Cipta (PKM-KC) AST-PTMA 2025**[cite: 1]

---

## 👥 Tim Penyusun

* **Ketua Tim:** Fahri Rasyidin (Teknik Informatika)[cite: 28, 31]
* **Anggota 1:** Hafiz Putra Mahesta (Teknik Informatika)[cite: 29, 31]
* **Anggota 2:** Muhammad Rizqy Zufarrel (Sistem dan Teknologi Informasi)[cite: 30, 31]
* **Dosen Pendamping:** Dr. Ir. Mohammad Givi Efgivia, M.Kom[cite: 32]
* **Perguruan Tinggi:** Universitas Muhammadiyah Prof. DR. HAMKA (UHAMKA)[cite: 32]

---

## 🌟 Fitur Utama

* **Kedaulatan & Privasi Data 100% (Zero Cloud Export):** Seluruh proses inferensi berjalan secara luring di perangkat lokal, memastikan data suara dan wajah pelamar terlindungi sesuai Undang-Undang Pelindungan Data Pribadi (UU PDP)[cite: 1, 17, 20].
* **Efisiensi Perangkat Keras (CPU-Only):** Tidak memerlukan GPU server yang mahal. Dioptimalkan untuk berjalan pada prosesor x86-64 dengan RAM minimum 16 GB menggunakan model terkuantisasi[cite: 20, 21].
* **Dukungan Multi-Bahasa STT:** Mendukung model Wav2Vec2 untuk bahasa Inggris (`facebook/wav2vec2-base-960h`) dan bahasa Indonesia (`cahya/wav2vec2-base-indonesian`)[cite: 1, 19].
* **Mekanisme Fallback Berlapis (100% Uptime):** Dilengkapi pencocokan kata kunci otomatis untuk menjaga kesinambungan sistem apabila layanan LLM mengalami kendala atau format respons tidak valid.
* **Antarmuka Multi-Page SaaS & Ekspor JSON:** Dibangun dengan Streamlit mencakup *Landing Page* (Bento-Grid), simulasi login lokal, *workspace* penilaian split-screen, dan tabel riwayat kandidat yang dapat mengunduh laporan format JSON[cite: 1, 21].

---

## 🛠️ Tech Stack & Arsitektur

* **Interface Framework:** Streamlit
* **Speech-to-Text (STT):** Facebook / Cahya Wav2Vec2 via Hugging Face Transformers[cite: 1, 19]
* **LLM (Reasoning & Judging):** Zephyr-7B (`zephyr`) melalui REST API Ollama lokal (`http://localhost:11434`)[cite: 1, 19]
* **Video & Audio Processing:** FFmpeg (via `imageio-ffmpeg`, konversi ke WAV 16 kHz mono)
* **Evaluasi & Metrik:** Word Error Rate (WER) menggunakan pustaka `jiwer`[cite: 1, 21]

---

## 📋 Spesifikasi Sistem Minimum

| Komponen | Spesifikasi Minimum / Acuan |
| :--- | :--- |
| **Sistem Operasi** | Windows 10/11, Linux (Ubuntu), atau macOS |
| **Memori (RAM)** | Minimal 16 GB (Direkomendasikan untuk model 7B)[cite: 20, 21] |
| **Prosesor (CPU)** | Intel Core i5 / AMD Ryzen 5 (minimal 4 inti, tanpa GPU)[cite: 21] |
| **Penyimpanan** | Kosong minimal 20 GB (untuk cache model dan dependensi)[cite: 21] |
| **Periferal** | Webcam dan Mikrofon USB[cite: 21] |

---

## 🚀 Panduan Instalasi & Menjalankan

Ikuti langkah-langkah berikut untuk mengatur dan menjalankan proyek di komputer lokal Anda:

### 1. Prasyarat
* Pastikan **Python 3.10+** sudah terinstal[cite: 1].
* Pastikan aplikasi **Ollama** sudah terpasang dan model Zephyr telah diunduh (`ollama pull zephyr`)[cite: 1, 19].

### 2. Clone Repository
```bash
git clone [https://github.com/Haztrama/Project-PKMM.git](https://github.com/Haztrama/Project-PKMM.git)
cd Project-PKMM
```

### 3. Buat dan Aktifkan Virtual Environment
```bash
# Windows
python -m venv env
env\Scripts\activate

# macOS / Linux
python3 -m venv env
source env/bin/activate
```

### 4. Instal Dependensi Pustaka
```bash
pip install -r requirements.txt
```

### 5. Jalankan Aplikasi Streamlit
Pastikan layanan Ollama aktif di latar belakang, lalu jalankan perintah:
```bash
streamlit run app.py
```
Akses aplikasi melalui peramban di alamat: http://localhost:8501

## 📁 Struktur Direktori Proyek
```
Project-PKMM/
├── app.py                      # Landing Page utama (Bento-Grid)
├── requirements.txt            # Daftar pustaka Python
├── pipeline.py                 # Modul logika AI (FFmpeg, Wav2Vec2, Ollama API)
├── knowledge.py                # Database pertanyaan, posisi pekerjaan, dan keyword
├── storage.py                  # Manajemen penyimpanan lokal dan laporan JSON
├── utils.py                    # Fungsi utilitas dan styling antarmuka
└── pages/
    ├── 1_🔐_Login.py          # Halaman autentikasi / login HR
    ├── 2_📊_Dashboard_Penilaian.py # Workspace split-screen penilaian video & AI
    └── 3_📋_Riwayat_Kandidat.py   # Tabel log rekapitulasi riwayat penilaian
```

## ⚙️ Logika Penilaian & Cara Kerja Sistem
* **Ekstraksi & Transkripsi Audio**: Video wawancara diunggah melalui antarmuka Streamlit, kemudian dikonversi menjadi audio WAV 16 kHz mono menggunakan FFmpeg sebelum ditranskripsi oleh modul Wav2Vec2.
* **Evaluasi LLM dengan Guardrail Ketat**: Transkrip teks dikirim ke Zephyr-7B melalui Ollama dengan prompt peran perekrut teknis, menghasilkan format keluaran terstruktur Score | Reason (skor 0–4 beserta alasan).
* **Mekanisme Fallback Kata Kunci**: Jika layanan LLM mengalami gangguan, timeout, atau format respons tidak valid, sistem secara otomatis mengalihkan proses ke modul fallback berbasis jumlah kecocokan kata kunci teknis guna mempertahankan uptime sistem hingga 100%.

## 📄 Lisensi & Pernyataan
Proyek pengembangan purwarupa ini disusun guna memenuhi luaran Program Kreativitas Mahasiswa Karsa Cipta (PKM-KC) AST-PTMA Tahun 2026. Seluruh data dan implementasi dikembangkan secara mandiri dengan menjunjung tinggi prinsip integritas akademik.
