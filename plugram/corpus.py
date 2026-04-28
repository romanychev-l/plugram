import sqlite3
import time
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS corpus (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    text TEXT NOT NULL,
    ts INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS corpus_ts ON corpus(ts);
"""


class Corpus:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def add(self, text: str, source: str = "live") -> None:
        self._conn.execute(
            "INSERT INTO corpus (source, text, ts) VALUES (?, ?, ?)",
            (source, text, int(time.time())),
        )
        self._conn.commit()

    def add_many(self, texts: list[str], source: str) -> int:
        rows = [(source, t, int(time.time())) for t in texts]
        cur = self._conn.executemany(
            "INSERT INTO corpus (source, text, ts) VALUES (?, ?, ?)", rows
        )
        self._conn.commit()
        return cur.rowcount

    def sample(self, n: int = 30, min_len: int = 30, max_len: int = 400) -> list[str]:
        cur = self._conn.execute(
            "SELECT text FROM corpus "
            "WHERE length(text) BETWEEN ? AND ? "
            "ORDER BY RANDOM() LIMIT ?",
            (min_len, max_len, n),
        )
        return [row[0] for row in cur.fetchall()]

    def stats(self) -> dict:
        cur = self._conn.execute(
            "SELECT source, COUNT(*) FROM corpus GROUP BY source"
        )
        by_source = {row[0]: row[1] for row in cur.fetchall()}
        total = sum(by_source.values())
        return {"total": total, "by_source": by_source}

    def close(self) -> None:
        self._conn.close()
