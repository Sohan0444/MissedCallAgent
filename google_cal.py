# =============================================================================
# google_cal.py  --  THE CALENDAR HANDS
# =============================================================================
#
# WHAT THIS FILE IS FOR
#   The only place in the codebase that talks to Google Calendar. Every read
#   and every write goes through here, so there's exactly one door.
#
# IT DOES TWO THINGS
#   1. READ  - "what times are actually open?"  (free/busy lookup)
#              The agent needs this to offer real slots instead of inventing
#              times that are already booked.
#
#   2. WRITE - "put this appointment on the calendar."
#              Called ONLY after the owner has said yes. Never from the agent
#              loop directly.
#
# THE SPLIT THAT MATTERS
#   Reading is safe. Anyone can ask what's open.
#   Writing is not. A write means a real human drives somewhere.
#   So reads are wired to the agent as a tool; writes are wired to the owner's
#   confirmation, and nothing else can reach them. If you only remember one
#   thing about this file: the agent can look, the owner can touch.
#
# AUTH, PLAINLY
#   Google OAuth, not an API key.
#   credentials.json - identifies the APP. You download this from Google once.
#   token.json       - identifies the USER, and is created the first time
#                      someone clicks "allow" in a browser. Auto-refreshes.
#   Both paths come from .env (GOOGLE_CREDENTIALS_FILE / GOOGLE_TOKEN_FILE).
#   Which calendar and which timezone also come from .env
#   (GOOGLE_CALENDAR_ID=primary, CALENDAR_TIMEZONE=America/New_York).
#
#   The first-run browser click is the awkward part: it needs a human at a
#   screen, which a server doesn't have. Worth thinking about before deploy.
#
# CURRENT STATE
#   Empty. Nothing here yet.
#
# =============================================================================