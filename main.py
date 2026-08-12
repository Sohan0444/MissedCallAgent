# =============================================================================
# main.py  --  THE FRONT DOOR
# =============================================================================
#
# WHAT THIS FILE DOES
#   The only part of the system Twilio can see. Two routes:
#
#   POST /sms    — someone TEXTED in. Save it, run the agent, return 200.
#
#   POST /voice  — someone CALLED and we missed it. Trigger a proactive
#                  outbound text to open the conversation.
#
# WHAT THIS FILE DOES NOT DO
#   No Claude. No SQL. No business logic. It receives, routes, responds.
#   Every real decision happens in agent.py.
#
# KNOWN GAPS
#   - run_agent() is called inline, so we're inside Twilio's 15s timeout window.
#     Future fix: background tasks, return 200 immediately, reply via REST.
#   - No routing between owner texts and customer texts yet.
#   - @app.on_event("startup") is deprecated in new FastAPI. Works for now.
# =============================================================================

from dotenv import load_dotenv
load_dotenv()  # must be first — loads API keys before anything else imports

from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from database import init_db
from agent import run_agent

app = FastAPI()

# ── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    # Creates the SQLite database and conversations table if they don't exist
    init_db()

# ── SMS Route ─────────────────────────────────────────────────────────────────

@app.post("/sms")
async def sms_webhook(
    From: str = Form(...),   # caller's phone number e.g. "+14155552671"
    Body: str = Form(...)    # what they typed e.g. "Hi I called earlier"
):
    print(f"Incoming SMS from {From}: {Body}")

    # Run the full ReAct agent loop
    # Agent reads history, reasons, uses tools, loops until done
    agent_response = run_agent(
        incoming_phone_number=From,
        incoming_message=Body
    )

    print(f"Agent responded: {agent_response}")

    # Return empty TwiML — agent already sent the reply via send_sms tool
    # This just tells Twilio we received the webhook (200 OK)
    resp = MessagingResponse()
    return Response(content=str(resp), media_type="text/xml")

# ── Voice Route ───────────────────────────────────────────────────────────────

@app.post("/voice")
async def voice_webhook(
    From: str = Form(...),      # caller's phone number
    CallStatus: str = Form(...) # "no-answer", "busy", "failed", "completed"
):
    print(f"Call from {From} with status: {CallStatus}")

    # Only trigger the agent if the call was actually missed
    if CallStatus in ["no-answer", "busy", "failed"]:
        run_agent(
            incoming_phone_number=From,
            incoming_message="MISSED_CALL"
        )

    # Return empty TwiML — no voice response needed, agent handles it via SMS
    return Response(content="<Response/>", media_type="text/xml")