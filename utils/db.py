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
        # We use a LEFT JOIN so we pull the basic info AND the profile text together
        query = """
        SELECT c.*, p.about_me, p.expertise_tags, p.helpful_thought_1, p.helpful_thought_2
        FROM tbl_counselor c
        LEFT JOIN tbl_counselor_profile p ON c.counselor_id = p.counselor_id
        """
        cursor.execute(query)
        return pd.DataFrame(cursor.fetchall())
    finally:
        cursor.close()
        conn.close()

def verify_admin_credentials(email, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT password_hash, role FROM tbl_user WHERE email=%s LIMIT 1"
    try:
        cursor.execute(query, (email,))
        admin_row = cursor.fetchone()
        if not admin_row:
            return False
            
        if admin_row["role"] != "admin":
            return False

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return admin_row["password_hash"] == hashed_password
    finally:
        cursor.close()
        conn.close()

def add_counselor(name, age, gender, ethnicity, specialization, counselor_language, counselor_modality, experience_years, about_me, expertise_tags, helpful_thought_1, helpful_thought_2):
    conn = get_connection()
    cursor = conn.cursor()

    query_counselor = """
    INSERT INTO tbl_counselor
    (name, age, gender, ethnicity, specialization, counselor_language, counselor_modality, experience_years)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    values_counselor = (name, age, gender, ethnicity, specialization, counselor_language, counselor_modality, experience_years)

    try:
        # 1. Insert into main table
        cursor.execute(query_counselor, values_counselor)
        counselor_id = cursor.lastrowid # Get the ID that was just created

        # 2. Insert into profile table using the new ID
        query_profile = """
        INSERT INTO tbl_counselor_profile
        (counselor_id, about_me, expertise_tags, helpful_thought_1, helpful_thought_2)
        VALUES (%s, %s, %s, %s, %s)
        """
        values_profile = (counselor_id, about_me, expertise_tags, helpful_thought_1, helpful_thought_2)
        cursor.execute(query_profile, values_profile)
        
        conn.commit()
    except Exception as e:
        conn.rollback() # If something fails, cancel both inserts to protect database
        raise e
    finally:
        cursor.close()
        conn.close()

def update_counselor(counselor_id, name, age, gender, ethnicity, specialization, counselor_language, counselor_modality, experience_years, about_me, expertise_tags, helpful_thought_1, helpful_thought_2):
    conn = get_connection()
    cursor = conn.cursor()

    query_counselor = """
    UPDATE tbl_counselor
    SET name=%s, age=%s, gender=%s, ethnicity=%s, specialization=%s, counselor_language=%s, counselor_modality=%s, experience_years=%s
    WHERE counselor_id=%s
    """
    values_counselor = (name, age, gender, ethnicity, specialization, counselor_language, counselor_modality, experience_years, counselor_id)

    try:
        # 1. Update main table
        cursor.execute(query_counselor, values_counselor)

        # 2. Check if a profile already exists for this counselor
        cursor.execute("SELECT profile_id FROM tbl_counselor_profile WHERE counselor_id = %s", (counselor_id,))
        profile_exists = cursor.fetchone()

        if profile_exists:
            # Update existing profile
            query_profile = """
            UPDATE tbl_counselor_profile
            SET about_me=%s, expertise_tags=%s, helpful_thought_1=%s, helpful_thought_2=%s
            WHERE counselor_id=%s
            """
            cursor.execute(query_profile, (about_me, expertise_tags, helpful_thought_1, helpful_thought_2, counselor_id))
        else:
            # Insert new profile if it didn't exist before
            query_profile = """
            INSERT INTO tbl_counselor_profile
            (counselor_id, about_me, expertise_tags, helpful_thought_1, helpful_thought_2)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query_profile, (counselor_id, about_me, expertise_tags, helpful_thought_1, helpful_thought_2))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def delete_counselor(counselor_id):
    conn = get_connection()
    cursor = conn.cursor()

    # The ON DELETE CASCADE in your database schema will automatically delete the profile too!
    query = "DELETE FROM tbl_counselor WHERE counselor_id=%s"
    try:
        cursor.execute(query, (counselor_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()