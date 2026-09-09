# MissedCallAgent

An AI-powered SMS agent that automatically responds to missed calls for small businesses, qualifies the lead, and captures appointment details — so the business doesn't lose the customer to a competitor who picked up.

**Live:** https://missedcallagent.onrender.com

## The problem

When a small business (plumber, HVAC, landscaper) misses a call, most callers don't leave a voicemail — they call the next business on the list. This agent texts them back immediately, figures out what they need, and collects a preferred appointment time for the owner to confirm.

## How it works

1. A call comes into the business's Twilio number and goes unanswered
2. Twilio fires a webhook to the FastAPI server
3. The agent (Claude) sends an SMS asking what the customer needs
4. It runs a tool-calling loop to qualify the request — service type, urgency, preferred time
5. Conversation state is stored in SQLite, keyed by phone number, so context carries across messages
6. The captured lead is surfaced for the business owner to confirm

## Stack

| Layer | Tech |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| LLM | Anthropic API (Claude) |
| Messaging | Twilio SMS |
| Storage | SQLite via SQLAlchemy |
| Calendar | Google Calendar API |
| Hosting | Render |

## Project structure
<img width="1358" height="312" alt="Screenshot 2026-09-09 at 5 34 38 PM" src="https://github.com/user-attachments/assets/1d1bd6fd-4198-4ec3-a1e8-42e4646a78a4" />
