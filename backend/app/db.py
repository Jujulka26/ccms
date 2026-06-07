import hashlib
import math
import mysql.connector

# Max concurrent open cases a counselor can hold (pending + approved, i.e. not
# yet closed). Single source of truth for the cap — ml.py imports it for matching.
MAX_CASELOAD = 5


class CounselorAtCapacity(Exception):
    """Raised when a new request would push a counselor past MAX_CASELOAD open cases."""


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
        # caseload is computed live = open cases (Pending or Approved, i.e. not
        # Closed). A new request raises it; closing lowers it. No stored counter
        # to drift. Availability is aggregated from the child table in one pass.
        cursor.execute("""
            SELECT
                c.*,
                p.about_me, p.expertise_tags, p.helpful_thought_1,
                p.helpful_thought_2, p.modality_desc, p.image,
                (
                    SELECT COUNT(*)
                    FROM tbl_request r
                    WHERE r.counselor_id = c.counselor_id
                      AND r.status IN ('Pending', 'Approved')
                ) AS caseload,
                (
                    SELECT GROUP_CONCAT(a.time_block ORDER BY a.time_block SEPARATOR ', ')
                    FROM tbl_counselor_availability a
                    WHERE a.counselor_id = c.counselor_id
                ) AS availability
            FROM tbl_counselor c
            LEFT JOIN tbl_counselor_profile p ON c.counselor_id = p.counselor_id
        """)
        return [_clean_row(r) for r in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


def counselor_exists(counselor_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM tbl_counselor WHERE counselor_id=%s LIMIT 1", (counselor_id,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()


def verify_admin_credentials(email: str, password: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT password_hash, role FROM tbl_user WHERE email=%s LIMIT 1", (email,))
        row = cursor.fetchone()
        if not row or row["role"] != "admin":
            return False
        return row["password_hash"] == hashlib.sha256(password.encode()).hexdigest()
    finally:
        cursor.close()
        conn.close()


def _set_availability(cursor, counselor_id: int, availability):
    """Replace a counselor's availability rows with the given list of time blocks."""
    cursor.execute("DELETE FROM tbl_counselor_availability WHERE counselor_id=%s", (counselor_id,))
    for block in (availability or []):
        cursor.execute(
            "INSERT INTO tbl_counselor_availability (counselor_id, time_block) VALUES (%s, %s)",
            (counselor_id, block),
        )


def add_counselor(
    *, name, age, gender, ethnicity, specialization,
    counselor_language, counselor_modality, experience_years, availability=None,
    about_me=None, expertise_tags=None, helpful_thought_1=None,
    helpful_thought_2=None, modality_desc=None, image=None,
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
        _set_availability(cursor, counselor_id, availability)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def update_counselor(
    counselor_id: int, *, name, age, gender, ethnicity, specialization,
    counselor_language, counselor_modality, experience_years, availability=None,
    about_me=None, expertise_tags=None, helpful_thought_1=None,
    helpful_thought_2=None, modality_desc=None, image=None,
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
        _set_availability(cursor, counselor_id, availability)
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
    client_name, client_email, counselor_id, compatibility_score,
    client_age=None, client_gender=None, client_ethnicity=None, client_issue=None,
    prev_exp=None, preferred_language=None, preferred_modality=None, preferred_c_gender=None,
):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Backstop: never let a counselor exceed MAX_CASELOAD open cases, even if
        # the client's view was stale or two requests race in. The front-end
        # already hides full counselors; this guarantees the rule server-side.
        cursor.execute(
            "SELECT COUNT(*) FROM tbl_request WHERE counselor_id=%s AND status IN ('Pending', 'Approved')",
            (counselor_id,),
        )
        if cursor.fetchone()[0] >= MAX_CASELOAD:
            raise CounselorAtCapacity(
                "This counselor is now fully booked. Please choose another counselor."
            )

        cursor.execute(
            """INSERT INTO tbl_request
               (client_name, client_email, counselor_id, compatibility_score, status,
                client_age, client_gender, client_ethnicity, client_issue,
                prev_exp, preferred_language, preferred_modality, preferred_c_gender)
               VALUES (%s, %s, %s, %s, 'Pending', %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                client_name, client_email, counselor_id, compatibility_score,
                client_age, client_gender, client_ethnicity, client_issue,
                prev_exp, preferred_language, preferred_modality, preferred_c_gender,
            ),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def get_all_requests() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT r.request_id, r.client_name, r.client_email, r.compatibility_score,
                      r.status, r.created_at, c.name as counselor_name,
                      r.client_age, r.client_gender, r.client_ethnicity, r.client_issue,
                      r.prev_exp, r.preferred_language, r.preferred_modality, r.preferred_c_gender
               FROM tbl_request r
               JOIN tbl_counselor c ON r.counselor_id = c.counselor_id
               ORDER BY r.request_id DESC"""
        )
        return [_clean_row(r) for r in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


def update_request_status(request_id: int, status: str):
    # Caseload is derived from request status, so approving (Pending→Approved)
    # keeps the case "open" and needs no counter bookkeeping.
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE tbl_request SET status=%s WHERE request_id=%s", (status, request_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def close_request(request_id: int):
    """Mark an approved match as Closed. This drops it out of the counselor's
    live caseload count, freeing a slot. Only an Approved match can be closed."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT status FROM tbl_request WHERE request_id=%s", (request_id,))
        row = cursor.fetchone()
        if not row or row[0] != "Approved":
            return  # only an active approved match can be closed
        cursor.execute("UPDATE tbl_request SET status='Closed' WHERE request_id=%s", (request_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def save_enquiry(name: str, email: str, subject: str, message: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO tbl_enquiry (name, email, subject, message)
               VALUES (%s, %s, %s, %s)""",
            (name, email, subject, message),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_enquiries() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT enquiry_id, name, email, subject, message, status, created_at
               FROM tbl_enquiry ORDER BY enquiry_id DESC"""
        )
        return [_clean_row(r) for r in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


def update_enquiry_status(enquiry_id: int, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE tbl_enquiry SET status=%s WHERE enquiry_id=%s", (status, enquiry_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


