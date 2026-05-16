import hashlib
import math
import pandas as pd
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ccms_db",
    )


def _clean(val):
    if val is None:
        return None
    if isinstance(val, float) and math.isnan(val):
        return None
    return val


def _clean_row(row: dict) -> dict:
    return {k: _clean(v) for k, v in row.items()}


def load_counselors() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT c.*, p.about_me, p.expertise_tags, p.helpful_thought_1, p.helpful_thought_2,
               p.modality_desc, p.image
        FROM tbl_counselor c
        LEFT JOIN tbl_counselor_profile p ON c.counselor_id = p.counselor_id
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return [_clean_row(r) for r in rows]
    finally:
        cursor.close()
        conn.close()


def verify_admin_credentials(email: str, password: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT password_hash, role FROM tbl_user WHERE email=%s LIMIT 1"
    try:
        cursor.execute(query, (email,))
        row = cursor.fetchone()
        if not row or row["role"] != "admin":
            return False
        hashed = hashlib.sha256(password.encode()).hexdigest()
        return row["password_hash"] == hashed
    finally:
        cursor.close()
        conn.close()


def add_counselor(
    name, age, gender, ethnicity, specialization,
    counselor_language, counselor_modality, experience_years,
    about_me, expertise_tags, helpful_thought_1, helpful_thought_2,
    modality_desc=None, image=None,
):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO tbl_counselor
               (name, age, gender, ethnicity, specialization, counselor_language, counselor_modality, experience_years)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (name, age, gender, ethnicity, specialization, counselor_language, counselor_modality, experience_years),
        )
        counselor_id = cursor.lastrowid
        cursor.execute(
            """INSERT INTO tbl_counselor_profile
               (counselor_id, about_me, expertise_tags, helpful_thought_1, helpful_thought_2, modality_desc, image)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (counselor_id, about_me, expertise_tags, helpful_thought_1, helpful_thought_2, modality_desc, image),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def get_counselor_by_name(name: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT counselor_id FROM tbl_counselor WHERE name=%s LIMIT 1", (name,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def update_counselor(
    counselor_id, name, age, gender, ethnicity, specialization,
    counselor_language, counselor_modality, experience_years,
    about_me, expertise_tags, helpful_thought_1, helpful_thought_2,
    modality_desc=None, image=None,
):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """UPDATE tbl_counselor
               SET name=%s, age=%s, gender=%s, ethnicity=%s, specialization=%s,
                   counselor_language=%s, counselor_modality=%s, experience_years=%s
               WHERE counselor_id=%s""",
            (name, age, gender, ethnicity, specialization, counselor_language, counselor_modality, experience_years, counselor_id),
        )
        cursor.execute("SELECT profile_id FROM tbl_counselor_profile WHERE counselor_id=%s", (counselor_id,))
        if cursor.fetchone():
            cursor.execute(
                """UPDATE tbl_counselor_profile
                   SET about_me=%s, expertise_tags=%s, helpful_thought_1=%s, helpful_thought_2=%s,
                       modality_desc=%s, image=%s
                   WHERE counselor_id=%s""",
                (about_me, expertise_tags, helpful_thought_1, helpful_thought_2, modality_desc, image, counselor_id),
            )
        else:
            cursor.execute(
                """INSERT INTO tbl_counselor_profile
                   (counselor_id, about_me, expertise_tags, helpful_thought_1, helpful_thought_2, modality_desc, image)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (counselor_id, about_me, expertise_tags, helpful_thought_1, helpful_thought_2, modality_desc, image),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def delete_counselor(counselor_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tbl_counselor WHERE counselor_id=%s", (counselor_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def has_pending_request(email: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT 1 FROM tbl_request WHERE client_email=%s AND status='Pending' LIMIT 1",
            (email,),
        )
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()


def save_intro_request(
    client_name, client_email, counselor_id, compatibility_score, outcome_consent=False,
    client_age=None, client_gender=None, client_ethnicity=None, client_issue=None,
    prev_exp=None, preferred_language=None, preferred_modality=None, preferred_c_gender=None,
):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO tbl_request
               (client_name, client_email, counselor_id, compatibility_score, status, outcome_consent,
                client_age, client_gender, client_ethnicity, client_issue,
                prev_exp, preferred_language, preferred_modality, preferred_c_gender)
               VALUES (%s, %s, %s, %s, 'Pending', %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                client_name, client_email, counselor_id, compatibility_score, int(outcome_consent),
                client_age, client_gender, client_ethnicity, client_issue,
                prev_exp, preferred_language, preferred_modality, preferred_c_gender,
            ),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_all_requests() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT r.request_id, r.client_name, r.client_email, r.compatibility_score,
                      r.status, r.created_at, r.match_outcome, r.outcome_consent, c.name as counselor_name
               FROM tbl_request r
               JOIN tbl_counselor c ON r.counselor_id = c.counselor_id
               ORDER BY r.request_id DESC"""
        )
        rows = cursor.fetchall()
        return [_clean_row(r) for r in rows]
    finally:
        cursor.close()
        conn.close()


def update_match_outcome(request_id: int, outcome: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE tbl_request SET match_outcome=%s WHERE request_id=%s", (outcome, request_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def update_request_status(request_id: int, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE tbl_request SET status=%s WHERE request_id=%s", (status, request_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_outcome_stats() -> dict:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
                COUNT(*) AS total_consented,
                SUM(match_outcome = 'Successful') AS successful,
                SUM(match_outcome = 'Unsuccessful') AS unsuccessful,
                SUM(match_outcome = 'Ongoing') AS ongoing,
                SUM(match_outcome IS NULL) AS not_recorded
            FROM tbl_request
            WHERE outcome_consent = 1
        """)
        row = cursor.fetchone()
        return {k: int(v) if v is not None else 0 for k, v in row.items()}
    finally:
        cursor.close()
        conn.close()


def get_consented_outcomes() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
                r.client_age, r.client_gender, r.client_ethnicity, r.client_issue,
                r.prev_exp, r.preferred_language, r.preferred_modality, r.preferred_c_gender,
                c.age AS counselor_age, c.gender AS counselor_gender,
                c.ethnicity AS counselor_ethnicity, c.specialization,
                c.counselor_language, c.counselor_modality, c.experience_years,
                r.compatibility_score, r.match_outcome
            FROM tbl_request r
            JOIN tbl_counselor c ON r.counselor_id = c.counselor_id
            WHERE r.outcome_consent = 1 AND r.match_outcome IN ('Successful', 'Unsuccessful')
            ORDER BY r.request_id DESC
        """)
        rows = cursor.fetchall()
        return [_clean_row(r) for r in rows]
    finally:
        cursor.close()
        conn.close()
