import hashlib

import pandas as pd
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ccms_db",
    )


def load_counselors():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM tbl_counselors")
        return pd.DataFrame(cursor.fetchall())
    finally:
        cursor.close()
        conn.close()


def verify_admin_credentials(email, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT password FROM tbl_admin WHERE email=%s LIMIT 1"
    try:
        cursor.execute(query, (email,))
        admin_row = cursor.fetchone()
        if not admin_row:
            return False

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return admin_row["password"] == hashed_password
    finally:
        cursor.close()
        conn.close()


def add_counselor(name, age, gender, ethnicity, specialization, counselor_language, counselor_modality, experience_years):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO tbl_counselors
    (name, age, gender, ethnicity, specialization, counselor_language, counselor_modality, experience_years)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (name, age, gender, ethnicity, specialization, counselor_language, counselor_modality, experience_years)

    try:
        cursor.execute(query, values)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def update_counselor(counselor_id, name, age, gender, ethnicity, specialization, counselor_language, counselor_modality, experience_years):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    UPDATE tbl_counselors
    SET name=%s, age=%s, gender=%s, ethnicity=%s, specialization=%s, counselor_language=%s, counselor_modality=%s, experience_years=%s
    WHERE counselor_id=%s
    """

    values = (name, age, gender, ethnicity, specialization, counselor_language, counselor_modality, experience_years, counselor_id)

    try:
        cursor.execute(query, values)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def delete_counselor(counselor_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = "DELETE FROM tbl_counselors WHERE counselor_id=%s"
    try:
        cursor.execute(query, (counselor_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
