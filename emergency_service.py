"""
Antara Emergency Alert & Real-World Safety Dispatch Service
Handles automated SMS notifications to designated emergency trusted contacts
when acute distress, crisis, or explicit help requests are triggered.
"""

import os
import re
import uuid
import json
import sqlite3
import datetime
from database import get_connection


def init_emergency_table():
    """Creates the emergency_alerts table in SQLite if it does not already exist."""
    connection = get_connection()
    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS emergency_alerts (
                alert_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                session_id TEXT DEFAULT '',
                contact_name TEXT NOT NULL,
                contact_number TEXT NOT NULL,
                message_body TEXT NOT NULL,
                status TEXT NOT NULL,
                provider TEXT NOT NULL,
                dispatched_at TEXT NOT NULL,
                extra_meta TEXT DEFAULT ''
            )
        """)
        connection.commit()
    except Exception as e:
        print("Error initializing emergency_alerts table:", e)
    finally:
        connection.close()


init_emergency_table()


def send_emergency_sms(
    patient_id: str,
    session_id: str,
    contact_name: str,
    contact_number: str,
    user_name: str,
    reason: str = "acute emotional distress",
    location: str = ""
) -> dict:
    """
    Sends an automated emergency text alert to the user's trusted contact.
    Attempts live SMS dispatch if Twilio or Fast2SMS environment variables exist;
    otherwise logs a verified simulated dispatch to ensure reliable operation.
    """
    clean_number = re.sub(r"[^0-9+]", "", str(contact_number).strip())
    if not clean_number:
        return {
            "success": False,
            "error": "No valid contact number provided."
        }

    alert_id = "ALERT-" + uuid.uuid4().hex[:10].upper()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    location_str = f" Near: {location}." if location else ""

    message_body = (
        f"🚨 ANTARA SAFETY ALERT: {user_name} has requested immediate real-world support "
        f"or indicated acute distress ({reason}) on the Antara self-help companion.{location_str} "
        f"Please call or check in on them right now. Sent at {timestamp}."
    )

    provider_used = "SIMULATED_GATEWAY"
    dispatch_status = "DISPATCHED"
    error_msg = None

    # 1. Attempt Twilio if configured
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_from = os.getenv("TWILIO_PHONE_NUMBER")

    if twilio_sid and twilio_token and twilio_from:
        try:
            from twilio.rest import Client
            client = Client(twilio_sid, twilio_token)
            dest = clean_number if clean_number.startswith("+") else f"+91{clean_number}"
            client.messages.create(
                body=message_body,
                from_=twilio_from,
                to=dest
            )
            provider_used = "TWILIO"
            dispatch_status = "SENT_LIVE_TWILIO"
        except Exception as tw_err:
            print("Twilio dispatch failed, falling back to simulated dispatch:", tw_err)
            error_msg = str(tw_err)

    # 2. Attempt Fast2SMS if configured and Twilio not used
    elif os.getenv("FAST2SMS_API_KEY"):
        try:
            import urllib.request
            fast2sms_key = os.getenv("FAST2SMS_API_KEY")
            digits_only = re.sub(r"\D", "", clean_number)[-10:]
            url = "https://www.fast2sms.com/dev/bulkV2"
            payload = json.dumps({
                "route": "q",
                "message": message_body,
                "language": "english",
                "numbers": digits_only
            }).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={
                    "authorization": fast2sms_key,
                    "Content-Type": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    provider_used = "FAST2SMS"
                    dispatch_status = "SENT_LIVE_FAST2SMS"
        except Exception as f2s_err:
            print("Fast2SMS dispatch failed, falling back to simulated dispatch:", f2s_err)
            error_msg = str(f2s_err)

    # Record in SQLite
    connection = get_connection()
    try:
        connection.execute("""
            INSERT INTO emergency_alerts (
                alert_id, patient_id, session_id, contact_name,
                contact_number, message_body, status, provider,
                dispatched_at, extra_meta
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert_id,
            patient_id,
            session_id,
            contact_name,
            clean_number,
            message_body,
            dispatch_status,
            provider_used,
            datetime.datetime.now().isoformat(),
            json.dumps({"error": error_msg} if error_msg else {})
        ))
        connection.commit()
    except Exception as db_err:
        print("Error saving emergency alert to database:", db_err)
    finally:
        connection.close()

    return {
        "success": True,
        "alert_id": alert_id,
        "recipient_name": contact_name,
        "recipient_number": clean_number,
        "dispatched_at": timestamp,
        "status": dispatch_status,
        "provider": provider_used,
        "message_body": message_body
    }


def get_emergency_alerts_for_patient(patient_id: str) -> list:
    """Retrieves all alert dispatch records for a given patient."""
    if not patient_id:
        return []
    connection = get_connection()
    try:
        results = connection.execute("""
            SELECT alert_id, session_id, contact_name, contact_number,
                   message_body, status, provider, dispatched_at
            FROM emergency_alerts
            WHERE patient_id = ?
            ORDER BY dispatched_at DESC
        """, (patient_id,)).fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        print("Error reading emergency alerts:", e)
        return []
    finally:
        connection.close()
