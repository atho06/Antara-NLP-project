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
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ==========================================
# INITIALIZE DATABASE
# ==========================================

def init_db():

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS patient_sessions (
                session_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                session_data TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                FOREIGN KEY (patient_id)
                REFERENCES patients(patient_id)
                ON DELETE CASCADE
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_patient_sessions_patient
            ON patient_sessions(patient_id)
        """)

        # ==========================================
        # THERAPISTS TABLE & SEED ACCOUNTS
        # ==========================================
        connection.execute("""
            CREATE TABLE IF NOT EXISTS therapists (
                therapist_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                license_number TEXT,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # Seed default attending therapist if not present
        existing_therapist = connection.execute(
            "SELECT therapist_id FROM therapists WHERE email = ?",
            ("therapist@antara.health",)
        ).fetchone()

        if not existing_therapist:
            pw_hash, pw_salt = hash_password("Therapist@123")
            connection.execute("""
                INSERT INTO therapists (
                    therapist_id,
                    full_name,
                    email,
                    license_number,
                    password_hash,
                    password_salt,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                "therapist_default_01",
                "Dr. Ananya Sharma (Clinical Psychologist)",
                "therapist@antara.health",
                "RCI-PSY-48921",
                pw_hash,
                pw_salt,
                datetime.now().isoformat()
            ))

        # Seed anonymous patient so open intakes can store sessions with valid foreign key
        existing_anon = connection.execute(
            "SELECT patient_id FROM patients WHERE patient_id = 'anonymous_patient'"
        ).fetchone()

        if not existing_anon:
            p_hash, p_salt = hash_password("anonymous_secret")
            connection.execute("""
                INSERT INTO patients (
                    patient_id,
                    full_name,
                    email,
                    password_hash,
                    password_salt,
                    created_at
                )
                VALUES ('anonymous_patient', 'Anonymous Patient', 'anonymous@patient.local', ?, ?, ?)
            """, (p_hash, p_salt, datetime.now().isoformat()))


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

    try:

        with get_connection() as connection:

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

        return True, "Account created successfully."

    except sqlite3.IntegrityError:

        return False, "An account with this email already exists."


# ==========================================
# PATIENT LOGIN
# ==========================================

def authenticate_patient(email, password):

    email = email.strip().lower()

    with get_connection() as connection:

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


# ==========================================
# THERAPIST REGISTRATION & AUTHENTICATION
# ==========================================

def register_therapist(full_name, email, password, license_number=""):
    full_name = full_name.strip()
    email = email.strip().lower()

    if not full_name or not email or not password:
        return False, "All fields are required."

    if "@" not in email or "." not in email:
        return False, "Please enter a valid professional email address."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    password_hash, password_salt = hash_password(password)
    therapist_id = secrets.token_hex(16)
    created_at = datetime.now().isoformat()

    try:
        with get_connection() as connection:
            connection.execute("""
                INSERT INTO therapists (
                    therapist_id,
                    full_name,
                    email,
                    license_number,
                    password_hash,
                    password_salt,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                therapist_id,
                full_name,
                email,
                license_number.strip(),
                password_hash,
                password_salt,
                created_at
            ))
        return True, "Therapist account registered successfully."
    except sqlite3.IntegrityError:
        return False, "A therapist with this email is already registered."


def authenticate_therapist(email, password):
    email = email.strip().lower()

    with get_connection() as connection:
        therapist = connection.execute("""
            SELECT *
            FROM therapists
            WHERE email = ?
        """, (email,)).fetchone()

        if therapist is None:
            return None

        stored_salt = bytes.fromhex(therapist["password_salt"])
        calculated_hash, _ = hash_password(password, stored_salt)

        if hmac.compare_digest(calculated_hash, therapist["password_hash"]):
            return {
                "therapist_id": therapist["therapist_id"],
                "full_name": therapist["full_name"],
                "email": therapist["email"],
                "license_number": therapist["license_number"] or ""
            }

        return None


def get_all_therapist_sessions():
    """Retrieves all sessions across patients for therapist portal review."""
    with get_connection() as connection:
        results = connection.execute("""
            SELECT session_id, patient_id, status, created_at, updated_at, session_data
            FROM patient_sessions
            ORDER BY updated_at DESC
        """).fetchall()

        sessions = []
        for row in results:
            item = dict(row)
            try:
                item["parsed_data"] = json.loads(item["session_data"])
            except Exception:
                item["parsed_data"] = {}
            sessions.append(item)
        return sessions


# ==========================================
# SAVE PATIENT SESSION
# ==========================================

def save_patient_session(
    patient_id,
    session_id,
    session_data,
    status="in_progress"
):

    if status not in {"in_progress", "completed", "crisis_paused"}:
        raise ValueError("Invalid session status.")

    data = json.dumps(
        session_data,
        ensure_ascii=False
    )

    now = datetime.now().isoformat()

    with get_connection() as connection:

        existing = connection.execute("""
            SELECT patient_id
            FROM patient_sessions
            WHERE session_id = ?
        """, (session_id,)).fetchone()

        if existing and existing["patient_id"] != patient_id:
            raise PermissionError(
                "This session does not belong to this patient."
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
        """, (
            session_id,
            patient_id,
            data,
            status,
            now,
            now
        ))


# ==========================================
# GET ONE PATIENT SESSION
# ==========================================

def get_patient_session(patient_id, session_id):

    with get_connection() as connection:

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


# ==========================================
# GET ALL PATIENT SESSIONS
# ==========================================

def get_patient_sessions(patient_id):

    with get_connection() as connection:

        results = connection.execute("""
            SELECT session_id, status, created_at, updated_at
            FROM patient_sessions
            WHERE patient_id = ?
            ORDER BY updated_at DESC
        """, (patient_id,)).fetchall()

        return [dict(row) for row in results]


# ==========================================
# GET LATEST UNFINISHED SESSION
# ==========================================

def get_unfinished_session(patient_id):

    with get_connection() as connection:

        result = connection.execute("""
            SELECT session_id, session_data
            FROM patient_sessions
            WHERE patient_id = ?
            AND status = 'in_progress'
            ORDER BY updated_at DESC
            LIMIT 1
        """, (patient_id,)).fetchone()

        if result:

            return {
                "session_id": result["session_id"],
                "session_data": json.loads(result["session_data"])
            }

        return None


# ==========================================
# COMPLETE PATIENT SESSION
# ==========================================

def complete_patient_session(patient_id, session_id):

    with get_connection() as connection:

        connection.execute("""
            UPDATE patient_sessions
            SET status = 'completed',
                updated_at = ?
            WHERE patient_id = ?
            AND session_id = ?
        """, (
            datetime.now().isoformat(),
            patient_id,
            session_id
        ))


# ==========================================
# DELETE PATIENT SESSION
# ==========================================

def delete_patient_session(patient_id, session_id):

    with get_connection() as connection:

        connection.execute("""
            DELETE FROM patient_sessions
            WHERE patient_id = ?
            AND session_id = ?
        """, (
            patient_id,
            session_id
        ))


# ==========================================
# INITIALIZE DATABASE
# ==========================================

init_db()