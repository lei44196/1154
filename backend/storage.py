import sqlite3
from pathlib import Path

# 数据文件固定在 backend 下，不受启动命令所在目录影响。
DB_FILE = Path(__file__).with_name("history.db")


def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    try:
        conn.execute("BEGIN")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                text TEXT,
                score REAL,
                label TEXT,
                pinyin TEXT,
                created_at TEXT
            )
        """)
        # IF NOT EXISTS 不会修改旧表；保留已有记录，旧记录保持未分配状态。
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(history)")}
        if "session_id" not in columns:
            conn.execute("ALTER TABLE history ADD COLUMN session_id TEXT")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_history_session_created "
            "ON history(session_id, created_at)"
        )
        conn.execute("DROP INDEX IF EXISTS idx_history_created")
        conn.commit()
    finally:
        conn.close()


def save_record(session_id, record):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO history (session_id, text, score, label, pinyin, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [session_id, record["text"], record["score"], record["label"],
             record["pinyin"], record["created_at"]],
        )
        conn.commit()
    finally:
        conn.close()


def get_history(session_id, limit):
    conn = get_conn()
    try:
        # 秒级时间戳可能相同；同秒时用自增 id 保证最新插入的记录在前。
        rows = conn.execute(
            # 会话编号用于筛选，不放进浏览器能读到的 JSON 响应。
            "SELECT id, text, score, label, pinyin, created_at FROM history "
            "WHERE session_id = ? ORDER BY created_at DESC, id DESC LIMIT ?",
            [session_id, limit],
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
