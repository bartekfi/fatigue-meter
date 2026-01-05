"""
SQLite storage for historical scores and trend tracking.
"""

import os
import sqlite3
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class StoredScore:
    """A score record from the database."""
    prompt_hash: str
    score: float
    category: str
    timestamp: datetime
    project: str
    text_preview: str


DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'scores.db')


def get_connection():
    """Get database connection, creating tables if needed."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            prompt_hash TEXT PRIMARY KEY,
            score REAL,
            category TEXT,
            timestamp INTEGER,
            project TEXT,
            text_preview TEXT,
            created_at INTEGER DEFAULT (strftime('%s', 'now'))
        )
    ''')

    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp ON scores(timestamp)
    ''')

    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_project ON scores(project)
    ''')

    conn.commit()
    return conn


def hash_prompt(text: str, timestamp: datetime) -> str:
    """Create unique hash for a prompt."""
    content = f"{text}:{timestamp.isoformat()}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def store_score(text: str, score: float, category: str,
                timestamp: datetime, project: str):
    """Store a score in the database."""
    conn = get_connection()
    prompt_hash = hash_prompt(text, timestamp)
    preview = text[:100] + '...' if len(text) > 100 else text

    conn.execute('''
        INSERT OR REPLACE INTO scores
        (prompt_hash, score, category, timestamp, project, text_preview)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (prompt_hash, score, category, int(timestamp.timestamp()),
          project, preview))

    conn.commit()
    conn.close()


def store_scores_batch(scores: list):
    """
    Store multiple scores efficiently.

    Args:
        scores: List of (text, score, category, timestamp, project) tuples
    """
    conn = get_connection()

    records = []
    for text, score, category, timestamp, project in scores:
        prompt_hash = hash_prompt(text, timestamp)
        preview = text[:100] + '...' if len(text) > 100 else text
        records.append((prompt_hash, score, category,
                       int(timestamp.timestamp()), project, preview))

    conn.executemany('''
        INSERT OR REPLACE INTO scores
        (prompt_hash, score, category, timestamp, project, text_preview)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', records)

    conn.commit()
    conn.close()


def get_scores(days: int = None, project: str = None,
               limit: int = None) -> list[StoredScore]:
    """Get scores from database with optional filters."""
    conn = get_connection()

    query = "SELECT * FROM scores WHERE 1=1"
    params = []

    if days:
        cutoff = int((datetime.now() - timedelta(days=days)).timestamp())
        query += " AND timestamp >= ?"
        params.append(cutoff)

    if project:
        query += " AND project LIKE ?"
        params.append(f"%{project}%")

    query += " ORDER BY timestamp DESC"

    if limit:
        query += " LIMIT ?"
        params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [StoredScore(
        prompt_hash=row['prompt_hash'],
        score=row['score'],
        category=row['category'],
        timestamp=datetime.fromtimestamp(row['timestamp']),
        project=row['project'],
        text_preview=row['text_preview']
    ) for row in rows]


def get_weekly_averages(weeks: int = 8) -> list[dict]:
    """Get average scores by week for trend analysis."""
    conn = get_connection()

    cutoff = int((datetime.now() - timedelta(weeks=weeks)).timestamp())

    rows = conn.execute('''
        SELECT
            strftime('%Y-%W', timestamp, 'unixepoch') as week,
            AVG(score) as avg_score,
            COUNT(*) as count
        FROM scores
        WHERE timestamp >= ?
        GROUP BY week
        ORDER BY week
    ''', (cutoff,)).fetchall()

    conn.close()

    return [{'week': row['week'], 'avg_score': row['avg_score'],
             'count': row['count']} for row in rows]


def get_hourly_stats() -> dict:
    """Get average scores by hour of day."""
    conn = get_connection()

    rows = conn.execute('''
        SELECT
            CAST(strftime('%H', timestamp, 'unixepoch', 'localtime') AS INTEGER) as hour,
            AVG(score) as avg_score,
            COUNT(*) as count
        FROM scores
        GROUP BY hour
        ORDER BY hour
    ''').fetchall()

    conn.close()

    return {row['hour']: {'avg_score': row['avg_score'], 'count': row['count']}
            for row in rows}


def get_day_of_week_stats() -> dict:
    """Get average scores by day of week (0=Monday, 6=Sunday)."""
    conn = get_connection()

    rows = conn.execute('''
        SELECT
            CAST(strftime('%w', timestamp, 'unixepoch', 'localtime') AS INTEGER) as dow,
            AVG(score) as avg_score,
            COUNT(*) as count
        FROM scores
        GROUP BY dow
        ORDER BY dow
    ''').fetchall()

    conn.close()

    # Convert Sunday=0 to Monday=0 format
    result = {}
    for row in rows:
        dow = (row['dow'] - 1) % 7  # Shift so Monday=0
        result[dow] = {'avg_score': row['avg_score'], 'count': row['count']}

    return result


def get_score_count() -> int:
    """Get total number of stored scores."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM scores").fetchone()[0]
    conn.close()
    return count


def clear_old_scores(days: int = 365):
    """Remove scores older than N days."""
    conn = get_connection()
    cutoff = int((datetime.now() - timedelta(days=days)).timestamp())
    conn.execute("DELETE FROM scores WHERE timestamp < ?", (cutoff,))
    conn.commit()
    conn.close()
