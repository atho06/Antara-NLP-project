import sqlite3
import hashlib
import secrets
import hmac
import json

from pathlib import Path
from datetime import datetime


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_FILE = BASE_DIR / "antara.db"


def get_connection():

    connection = sqlite3.connect(DATABASE_FILE)

    connection.row_factory = sqlite3.Row

    return connection


# ==========================================
# INITIALIZE DATABASE
# ==========================================

def init_db():

    connection = get_connection()

    cursor = connection.cursor()

    # PATIENTS TABLE

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (

            patient_id TEXT PRIMARY KEY,

            full_name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            password_salt TEXT NOT NULL,

            created_at TEXT NOT NULL

        )
    """)

    # PATIENT SESSIONS TABLE

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_sessions (

            session_id TEXT PRIMARY KEY,

            patient_id TEXT NOT NULL,

            session_data TEXT NOT NULL,

            status TEXT NOT NULL,

            created_at TEXT NOT NULL,

            updated_at TEXT NOT NULL,

            FOREIGN KEY (patient_id)
            REFERENCES patients(patient_id)

        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_patient_sessions_patient
        ON patient_sessions(patient_id)
    """)

    connection.commit()

    connection.close()


# ==========================================
# PASSWORD HASHING
# ==========================================

def hash_password(password, salt=None):

    if salt is None:
        salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        600000
    )

    return password_hash.hex(), salt.hex()


# ==========================================
# PATIENT REGISTRATION
# ==========================================

def register_patient(full_name, email, password):

    full_name = full_name.strip()
    email = email.strip().lower()

    if not full_name or not email or not password:
        return False, "All fields are required."

    if "@" not in email or "." not in email:
        return False, "Please enter a valid email address."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    password_hash, password_salt = hash_password(password)

    patient_id = secrets.token_hex(16)

    created_at = datetime.now().isoformat()

    connection = get_connection()

    try:

        connection.execute("""
            INSERT INTO patients (
                patient_id,
                full_name,
                email,
                password_hash,
                password_salt,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            patient_id,
            full_name,
            email,
            password_hash,
            password_salt,
            created_at
        ))

        connection.commit()

        return True, "Account created successfully."

    except sqlite3.IntegrityError:

        return False, "An account with this email already exists."

    finally:

        connection.close()


# ==========================================
# PATIENT LOGIN
# ==========================================

def authenticate_patient(email, password):

    email = email.strip().lower()

    connection = get_connection()

    try:

        patient = connection.execute("""
            SELECT *
            FROM patients
            WHERE email = ?
        """, (email,)).fetchone()

        if patient is None:
            return None

        stored_salt = bytes.fromhex(
            patient["password_salt"]
        )

        calculated_hash, _ = hash_password(
            password,
            stored_salt
        )

        if hmac.compare_digest(
            calculated_hash,
            patient["password_hash"]
        ):

            return {
                "patient_id": patient["patient_id"],
                "full_name": patient["full_name"],
                "email": patient["email"]
            }

        return None

    finally:

        connection.close()


# ==========================================
# SAVE PATIENT SESSION
# ==========================================

def save_patient_session(
    patient_id,
    session_id,
    session_data,
    status="in_progress"
):

    connection = get_connection()

    now = datetime.now().isoformat()

    data = json.dumps(
        session_data,
        ensure_ascii=False
    )

    connection.execute("""
        INSERT INTO patient_sessions (
            session_id,
            patient_id,
            session_data,
            status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?)

        ON CONFLICT(session_id)
        DO UPDATE SET

            session_data = excluded.session_data,
            status = excluded.status,
            updated_at = excluded.updated_at

        WHERE patient_sessions.patient_id = excluded.patient_id

    """, (
        session_id,
        patient_id,
        data,
        status,
        now,
        now
    ))

    connection.commit()

    connection.close()


# ==========================================
# GET PATIENT SESSION
# ==========================================

def get_patient_session(patient_id, session_id):

    connection = get_connection()

    try:

        result = connection.execute("""
            SELECT session_data
            FROM patient_sessions
            WHERE patient_id = ?
            AND session_id = ?
        """, (
            patient_id,
            session_id
        )).fetchone()

        if result:

            return json.loads(result["session_data"])

        return None

    finally:

        connection.close()


# ==========================================
# GET ALL PATIENT SESSIONS
# ==========================================

def get_patient_sessions(patient_id):

    connection = get_connection()

    try:

        results = connection.execute("""
            SELECT session_id, status, created_at, updated_at
            FROM patient_sessions
            WHERE patient_id = ?
            ORDER BY updated_at DESC
        """, (patient_id,)).fetchall()

        return [dict(row) for row in results]

    finally:

        connection.close()


# ==========================================
# DELETE PATIENT SESSION
# ==========================================

def delete_patient_session(patient_id, session_id):

    connection = get_connection()

    connection.execute("""
        DELETE FROM patient_sessions
        WHERE patient_id = ?
        AND session_id = ?
    """, (
        patient_id,
        session_id
    ))

    connection.commit()

    connection.close()


# ==========================================
# INITIALIZE DATABASE AUTOMATICALLY
# ==========================================

init_db()