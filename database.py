# =============================================================================
# database.py  --  WORKING MEMORY
# =============================================================================
#
# WHAT THIS FILE IS FOR
#   Text messages are stateless. Someone texts "yeah 2pm works" and that
#   sentence means nothing by itself. This file is how we remember what came
#   before it.
#
# THE IDEA IN ONE LINE
#   Remember conversations, keyed by phone number.
#
# WHAT THIS IS *NOT*
#   This is not the business's records. This is scratch paper for the agent.
#   The owner never reads this -- the owner reads the call log (CSV/Sheets),
#   which is deliberately separate. If the agent misunderstands a conversation,
#   the owner's view of their own business should still be correct.
#
# HOW MEMORY SHOULD BE ORGANIZED (planned, not built)
#   contacts          - a phone number, and what we know about that person
#   sessions          - ONE conversation. A new call starts a new session.
#   messages          - every text, in and out, attached to a session
#   pending_bookings  - times proposed but not yet OK'd by the owner
#
# THE SESSION RULE (planned)
#   Each phone call opens a fresh session. Texts land on the newest open one.
#   Quiet for N hours (number TBD) -> stale -> next text starts a new session.
#
#   Why not one endless thread per person? Someone texting in March shouldn't
#   get an agent still chewing on their January sink leak.
#   Why not wipe memory every call? Because "can we move Thursday to Friday?"
#   has to work, and that needs to know Thursday exists.
#   So: clean context per job, with past sessions and confirmed bookings
#   summarized in as background. Fresh, but not amnesiac.
#
# CURRENT STATE / KNOWN GAPS
#   - Uses raw sqlite3. requirements.txt lists sqlalchemy; nothing imports it
#     yet. Pick one before the schema grows.
#   - get_history() returns EVERY message for a phone number, forever. That's
#     the "one endless thread" model, i.e. the opposite of the session rule
#     above. Reconciling this is the main open work in this file.
#
# =============================================================================

import sqlite3
from datetime import datetime


def init_db():
    conn = sqlite3.connect("conversations.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_message(phone_number: str, role: str, content: str):
    # Open connection to the database file
    conn = sqlite3.connect("conversations.db")
    
    # Create cursor to execute SQL commands
    cursor = conn.cursor()
    
    # INSERT a new row into the table
    # ? are placeholders — SQLite fills them in safely from the tuple
    # Never put variables directly in SQL strings — that's a security vulnerability
    cursor.execute(
        "INSERT INTO conversations (phone_number, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (phone_number, role, content, datetime.now().isoformat())
    )
    
    # Save the changes
    conn.commit()
    
    # Close the connection
    conn.close()


def get_history(phone_number: str) -> list:
    history = []
    
    # Open connection
    conn = sqlite3.connect("conversations.db")
    cursor = conn.cursor()
    
    # SELECT reads from the database
    # ORDER BY timestamp ASC means oldest messages first
    cursor.execute(
        "SELECT role, content FROM conversations WHERE phone_number = ? ORDER BY timestamp ASC",
        (phone_number,)
    )
    
    # Fetch all matching rows as a list of tuples
    rows = cursor.fetchall()
    
    # Convert each tuple into a dict Claude expects
    for role, content in rows:
        history.append({"role": role, "content": content})
    
    conn.close()
    return history
