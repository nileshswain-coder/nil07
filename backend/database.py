import sqlite3
from typing import Any, Dict, List, Optional

DB_NAME = "database.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS projects(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT UNIQUE,
            wave_type TEXT,
            sample_size INTEGER,
            survey_file TEXT,
            quota_file TEXT,
            created_date TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS question_mapping(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT UNIQUE,
            respondent_id TEXT,
            duration TEXT,
            awareness_question TEXT,
            consideration_question TEXT,
            purchase_question TEXT,
            usage_question TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS uploads(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT,
            upload_name TEXT,
            upload_date TEXT
        )
        """
    )

    cursor.execute("PRAGMA table_info(question_mapping)")
    existing_columns = [row["name"] for row in cursor.fetchall()]
    if "respondent_id" not in existing_columns:
        cursor.execute("ALTER TABLE question_mapping ADD COLUMN respondent_id TEXT DEFAULT ''")
    if "duration" not in existing_columns:
        cursor.execute("ALTER TABLE question_mapping ADD COLUMN duration TEXT DEFAULT ''")
    if "usage_question" not in existing_columns:
        cursor.execute("ALTER TABLE question_mapping ADD COLUMN usage_question TEXT DEFAULT ''")

    conn.commit()
    conn.close()


def project_exists(project_name: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM projects WHERE project_name = ? LIMIT 1",
        (project_name.strip(),),
    )
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def add_project(
    project_name: str,
    wave_type: str,
    sample_size: int,
    survey_file: str,
    quota_file: str,
    created_date: str,
) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO projects(
            project_name,
            wave_type,
            sample_size,
            survey_file,
            quota_file,
            created_date
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (project_name.strip(), wave_type, sample_size, survey_file, quota_file, created_date),
    )
    conn.commit()
    conn.close()


def update_project_files(
    project_name: str,
    survey_file: Optional[str] = None,
    quota_file: Optional[str] = None,
) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    if survey_file is not None:
        cursor.execute(
            "UPDATE projects SET survey_file = ? WHERE project_name = ?",
            (survey_file, project_name.strip()),
        )
    if quota_file is not None:
        cursor.execute(
            "UPDATE projects SET quota_file = ? WHERE project_name = ?",
            (quota_file, project_name.strip()),
        )
    conn.commit()
    conn.close()


def get_projects() -> List[str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT project_name FROM projects ORDER BY project_name")
    projects = [row["project_name"] for row in cursor.fetchall()]
    conn.close()
    return projects


def save_question_mapping(
    project_name: str,
    respondent_id: str,
    duration: str,
    awareness: str,
    consideration: str,
    purchase: str,
    usage: str,
) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM question_mapping WHERE project_name = ?",
        (project_name.strip(),),
    )
    cursor.execute(
        """
        INSERT INTO question_mapping(
            project_name,
            respondent_id,
            duration,
            awareness_question,
            consideration_question,
            purchase_question,
            usage_question
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project_name.strip(),
            respondent_id,
            duration,
            awareness,
            consideration,
            purchase,
            usage,
        ),
    )
    conn.commit()
    conn.close()


def get_question_mapping(project_name: str) -> Optional[Dict[str, str]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM question_mapping WHERE project_name = ?",
        (project_name.strip(),),
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "respondent_id": row["respondent_id"],
        "duration": row["duration"],
        "awareness": row["awareness_question"],
        "consideration": row["consideration_question"],
        "purchase": row["purchase_question"],
        "usage": row["usage_question"],
    }


def get_project(project_name: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM projects WHERE project_name = ?",
        (project_name.strip(),),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def save_upload_log(project_name: str, upload_name: str, upload_date: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO uploads(project_name, upload_name, upload_date) VALUES (?, ?, ?)",
        (project_name.strip(), upload_name, upload_date),
    )
    conn.commit()
    conn.close()
