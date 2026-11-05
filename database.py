import sqlite3
import json
import uuid
import hashlib
import secrets

from pathlib import Path
from datetime import datetime


# ==========================================================
# 1. DATABASE CONFIGURATION
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "antara.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# ==========================================================
# 2. PASSWORD SECURITY
# ==========================================================

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200000
    )

    return password_hash.hex(), salt


def verify_password(password, stored_hash, salt):
    calculated_hash, _ = hash_password(password, salt)

    return secrets.compare_digest(
        calculated_hash,
        stored_hash
    )


# ==========================================================
# 3. DATABASE INITIALIZATION AND MIGRATION
# ==========================================================

def init_db():

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                phone TEXT DEFAULT '',
                date_of_birth TEXT DEFAULT '',
                age INTEGER,
                locality TEXT DEFAULT '',
                city TEXT DEFAULT '',
                district TEXT DEFAULT '',
                state TEXT DEFAULT '',
                pincode TEXT DEFAULT '',
                trusted_contact_name TEXT DEFAULT '',
                trusted_contact_relationship TEXT DEFAULT '',
                trusted_contact_number TEXT DEFAULT '',
                emergency_alert_consent INTEGER DEFAULT 0,
                trusted_contact_agreement INTEGER DEFAULT 0,
                reason_for_declining TEXT DEFAULT '',
                pre_session_note TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)

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
                    ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS therapists (
                therapist_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # Migrate older patient tables.

        existing_columns = {
            row["name"]
            for row in cursor.execute(
                "PRAGMA table_info(patients)"
            ).fetchall()
        }

        new_columns = {
            "phone": "TEXT DEFAULT ''",
            "date_of_birth": "TEXT DEFAULT ''",
            "age": "INTEGER",
            "locality": "TEXT DEFAULT ''",
            "city": "TEXT DEFAULT ''",
            "district": "TEXT DEFAULT ''",
            "state": "TEXT DEFAULT ''",
            "pincode": "TEXT DEFAULT ''",
            "trusted_contact_name": "TEXT DEFAULT ''",
            "trusted_contact_relationship": "TEXT DEFAULT ''",
            "trusted_contact_number": "TEXT DEFAULT ''",
            "emergency_alert_consent": "INTEGER DEFAULT 0",
            "trusted_contact_agreement": "INTEGER DEFAULT 0",
            "reason_for_declining": "TEXT DEFAULT ''",
            "pre_session_note": "TEXT DEFAULT ''"
        }

        for column_name, column_type in new_columns.items():

            if column_name not in existing_columns:
                cursor.execute(
                    f"ALTER TABLE patients ADD COLUMN "
                    f"{column_name} {column_type}"
                )

        # Repair patient records with missing IDs.
        # Existing password hashes and patient details are preserved.

        patients_without_ids = cursor.execute("""
            SELECT rowid
            FROM patients
            WHERE patient_id IS NULL
               OR TRIM(patient_id) = ''
        """).fetchall()

        for patient in patients_without_ids:

            new_id = "PAT-" + uuid.uuid4().hex[:10].upper()

            cursor.execute("""
                UPDATE patients
                SET patient_id = ?
                WHERE rowid = ?
            """, (new_id, patient["rowid"]))

        # Session index.

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_patient_sessions
            ON patient_sessions(patient_id)
        """)

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ==========================================================
# 4. REGISTER PATIENT
# ==========================================================

def register_patient(
    full_name,
    email,
    password,
    location="",
    date_of_birth="",
    contact_number="",
    trusted_contact_name="",
    trusted_contact_relationship="",
    trusted_contact_number="",
    emergency_alert_consent=False,
    reason_for_declining="",
    pre_session_note="",
    city="",
    state="",
    district="",
    locality="",
    pincode="",
    trusted_contact_agreement=False,
    age=None
):

    connection = get_connection()

    try:

        email = email.strip().lower()

        existing = connection.execute("""
            SELECT patient_id
            FROM patients
            WHERE email = ?
        """, (email,)).fetchone()

        if existing:
            return False

        password_hash, password_salt = hash_password(password)

        patient_id = "PAT-" + uuid.uuid4().hex[:10].upper()

        created_at = datetime.now().isoformat()

        connection.execute("""
            INSERT INTO patients (
                patient_id,
                full_name,
                email,
                password_hash,
                password_salt,
                phone,
                date_of_birth,
                age,
                locality,
                city,
                district,
                state,
                pincode,
                trusted_contact_name,
                trusted_contact_relationship,
                trusted_contact_number,
                emergency_alert_consent,
                trusted_contact_agreement,
                reason_for_declining,
                pre_session_note,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            patient_id,
            full_name.strip(),
            email,
            password_hash,
            password_salt,
            contact_number,
            str(date_of_birth),
            age,
            locality,
            city,
            district,
            state,
            pincode,
            trusted_contact_name,
            trusted_contact_relationship,
            trusted_contact_number,
            int(bool(emergency_alert_consent)),
            int(bool(trusted_contact_agreement)),
            reason_for_declining,
            pre_session_note,
            created_at
        ))

        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    except Exception as error:
        print("Patient registration error:", error)
        return False

    finally:
        connection.close()


# ==========================================================
# 5. AUTHENTICATE PATIENT
# ==========================================================

def authenticate_patient(email, password):

    connection = get_connection()

    try:

        patient = connection.execute("""
            SELECT *
            FROM patients
            WHERE email = ?
        """, (email.strip().lower(),)).fetchone()

        if not patient:
            return None

        if not patient["patient_id"]:
            print("Patient account has no valid patient ID.")
            return None

        if verify_password(
            password,
            patient["password_hash"],
            patient["password_salt"]
        ):
            return dict(patient)

        return None

    except Exception as error:
        print("Authentication error:", error)
        return None

    finally:
        connection.close()


# ==========================================================
# 6. SAVE PATIENT SESSION
# ==========================================================

def save_patient_session(
    patient_id,
    session_id,
    session_data,
    status="in_progress"
):

    if not patient_id or not session_id:
        raise ValueError("Patient ID and session ID are required.")

    connection = get_connection()

    try:

        current_time = datetime.now().isoformat()

        serialized_data = json.dumps(
            session_data,
            ensure_ascii=False
        )

        patient = connection.execute("""
            SELECT patient_id
            FROM patients
            WHERE patient_id = ?
        """, (patient_id,)).fetchone()

        if not patient:
            raise ValueError("Patient account was not found.")

        existing = connection.execute("""
            SELECT created_at
            FROM patient_sessions
            WHERE session_id = ?
              AND patient_id = ?
        """, (session_id, patient_id)).fetchone()

        if existing:

            connection.execute("""
                UPDATE patient_sessions
                SET session_data = ?,
                    status = ?,
                    updated_at = ?
                WHERE session_id = ?
                  AND patient_id = ?
            """, (
                serialized_data,
                status,
                current_time,
                session_id,
                patient_id
            ))

        else:

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
            """, (
                session_id,
                patient_id,
                serialized_data,
                status,
                current_time,
                current_time
            ))

        connection.commit()

    except Exception as error:

        connection.rollback()
        print("Session saving error:", error)
        raise

    finally:
        connection.close()


# ==========================================================
# 7. GET ONE PATIENT SESSION
# ==========================================================

def get_patient_session(patient_id, session_id):

    connection = get_connection()

    try:

        result = connection.execute("""
            SELECT session_data
            FROM patient_sessions
            WHERE patient_id = ?
              AND session_id = ?
        """, (patient_id, session_id)).fetchone()

        if not result:
            return None

        return json.loads(result["session_data"])

    except Exception as error:
        print("Session retrieval error:", error)
        return None

    finally:
        connection.close()


# ==========================================================
# 8. GET ALL PATIENT SESSIONS
# ==========================================================

def get_patient_sessions(patient_id):

    if not patient_id:
        return []

    connection = get_connection()

    try:

        results = connection.execute("""
            SELECT
                session_id,
                status,
                created_at,
                updated_at
            FROM patient_sessions
            WHERE patient_id = ?
            ORDER BY updated_at DESC
        """, (patient_id,)).fetchall()

        return [dict(row) for row in results]

    except Exception as error:
        print("Session history error:", error)
        return []

    finally:
        connection.close()


# ==========================================================
# 9. GET UNFINISHED SESSION
# ==========================================================

def get_unfinished_session(patient_id):

    if not patient_id:
        return None

    connection = get_connection()

    try:

        result = connection.execute("""
            SELECT session_id, session_data
            FROM patient_sessions
            WHERE patient_id = ?
              AND status = 'in_progress'
            ORDER BY updated_at DESC
            LIMIT 1
        """, (patient_id,)).fetchone()

        if not result:
            return None

        return {
            "session_id": result["session_id"],
            "session_data": json.loads(result["session_data"])
        }

    except Exception as error:
        print("Unfinished session error:", error)
        return None

    finally:
        connection.close()


# ==========================================================
# 10. COMPLETE PATIENT SESSION
# ==========================================================

def complete_patient_session(patient_id, session_id):

    connection = get_connection()

    try:

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

        connection.commit()

    except Exception as error:
        connection.rollback()
        print("Session completion error:", error)
        raise

    finally:
        connection.close()


# ==========================================================
# 11. DELETE PATIENT SESSION
# ==========================================================

def delete_patient_session(patient_id, session_id):

    connection = get_connection()

    try:

        cursor = connection.execute("""
            DELETE FROM patient_sessions
            WHERE patient_id = ?
              AND session_id = ?
        """, (patient_id, session_id))

        connection.commit()

        return cursor.rowcount > 0

    except Exception as error:
        connection.rollback()
        print("Session deletion error:", error)
        return False

    finally:
        connection.close()


# ==========================================================
# 12. GET PATIENT DETAILS
# ==========================================================

def get_patient_details(patient_id):

    connection = get_connection()

    try:

        result = connection.execute("""
            SELECT *
            FROM patients
            WHERE patient_id = ?
        """, (patient_id,)).fetchone()

        if not result:
            return None

        patient = dict(result)

        patient.pop("password_hash", None)
        patient.pop("password_salt", None)

        return patient

    except Exception as error:
        print("Patient details error:", error)
        return None

    finally:
        connection.close()


# ==========================================================
# 13. UPDATE PATIENT DETAILS
# ==========================================================

def update_patient_details(patient_id, updates):

    allowed_fields = {
        "full_name",
        "phone",
        "date_of_birth",
        "age",
        "locality",
        "city",
        "district",
        "state",
        "pincode",
        "trusted_contact_name",
        "trusted_contact_relationship",
        "trusted_contact_number",
        "emergency_alert_consent",
        "trusted_contact_agreement",
        "reason_for_declining",
        "pre_session_note"
    }

    if not isinstance(updates, dict):
        return False

    filtered_updates = {
        key: value
        for key, value in updates.items()
        if key in allowed_fields
    }

    if not filtered_updates:
        return False

    connection = get_connection()

    try:

        assignments = ", ".join(
            f"{key} = ?"
            for key in filtered_updates
        )

        values = list(filtered_updates.values())
        values.append(patient_id)

        cursor = connection.execute(
            f"""
            UPDATE patients
            SET {assignments}
            WHERE patient_id = ?
            """,
            values
        )

        connection.commit()

        return cursor.rowcount > 0

    except Exception as error:
        connection.rollback()
        print("Patient update error:", error)
        return False

    finally:
        connection.close()


# ==========================================================
# 14. INITIALIZE DATABASE
# ==========================================================

init_db()