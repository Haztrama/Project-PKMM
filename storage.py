"""storage.py - Penyimpanan riwayat penilaian di SQLite lokal (tanpa server, tanpa cloud)."""
import sqlite3
from datetime import datetime
from pathlib import Path

import streamlit as st

from knowledge import QUESTION_DB
from utils import WIB, build_report, now_wib, report_json

DB_PATH = Path(__file__).with_name("interviewlens.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS assessments (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    email         TEXT,
    position      TEXT NOT NULL,
    evaluated_at  TEXT NOT NULL,
    question_id   INTEGER NOT NULL,
    score         INTEGER NOT NULL,
    reason        TEXT,
    method        TEXT,
    language      TEXT,
    is_sample     INTEGER NOT NULL DEFAULT 0,
    report_json   TEXT NOT NULL
)
"""

# Contoh data (fiktif) agar halaman Riwayat tidak kosong saat pertama kali dibuka.
_SAMPLES = [
    ("Rizky Pratama", "rizky.pratama@example.com", "Machine Learning Engineer", "2026-06-12 14:32:00", 1, 3,
     "The candidate described a recommendation model and its trade-offs clearly but did not mention quantitative evaluation metrics."),
    ("Sarah Anindya", "sarah.anindya@example.com", "Data Scientist", "2026-06-11 10:15:00", 5, 2,
     "The answer covers data cleaning in general terms without concrete techniques or tools."),
    ("Budi Santoso", "budi.santoso@example.com", "NLP Engineer", "2026-06-10 16:50:00", 13, 4,
     "The candidate explained tokenization and embeddings in detail with concrete examples such as Word2Vec and cosine similarity."),
]


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _insert(conn, name, email, position, evaluated_at: datetime, question_id, score, reason, method, language, is_sample):
    report = build_report(name, email, "", question_id, score, reason, evaluated_at)
    conn.execute(
        "INSERT INTO assessments (name,email,position,evaluated_at,question_id,score,reason,method,language,is_sample,report_json)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (name, email, position, evaluated_at.strftime("%Y-%m-%d %H:%M:%S"), question_id, score, reason,
         method, language, int(is_sample), report_json(report)),
    )


@st.cache_resource(show_spinner=False)
def init_db() -> bool:
    """Buat tabel dan isi contoh data jika kosong (dijalankan sekali per proses)."""
    with _conn() as conn:
        conn.execute(_SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM assessments").fetchone()[0] == 0:
            for name, email, pos, ts, qid, score, reason in _SAMPLES:
                _insert(conn, name, email, pos, datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").replace(tzinfo=WIB),
                        qid, score, reason, "contoh", "Inggris", True)
    return True


def add_assessment(name, email, position, question_id, score, reason, method, language, report: dict) -> int:
    init_db()
    ts = now_wib()
    with _conn() as conn:
        cur = conn.execute(
            "INSERT INTO assessments (name,email,position,evaluated_at,question_id,score,reason,method,language,is_sample,report_json)"
            " VALUES (?,?,?,?,?,?,?,?,?,0,?)",
            (name, email, position, ts.strftime("%Y-%m-%d %H:%M:%S"), question_id, score, reason, method,
             language, report_json(report)),
        )
        return cur.lastrowid


def list_assessments() -> list:
    init_db()
    with _conn() as conn:
        rows = conn.execute("SELECT * FROM assessments ORDER BY evaluated_at DESC, id DESC").fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["evaluated_dt"] = datetime.strptime(d["evaluated_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=WIB)
        d["question"] = QUESTION_DB.get(d["question_id"], "-")
        out.append(d)
    return out
