# =============================================================================
# agent.py  --  THE BRAIN
# =============================================================================
#
# WHAT THIS FILE IS FOR
#   This is where Claude lives. Everything about "what do we say back to this
#   person" happens here and nowhere else.
#
# HOW IT WORKS, PLAINLY
#   Someone texts us. main.py hands this file the conversation so far.
#   This file asks Claude what to say next. Claude either:
#     (a) replies with words  -> hand those words back, done
#     (b) asks for a tool     -> run the tool, give Claude the answer, ask again
#   Repeat until Claude has words. Return them.
#   That's the whole thing: a loop around one question -- "what now?"
#
# THE TOOLS CLAUDE WILL GET (planned)
#   check_availability  - look at the calendar, see what's open
#   propose_booking     - write down a tentative time. DOES NOT BOOK IT.
#   log_call            - record who called, what they need, when they want it
#
# THE ONE RULE THAT MATTERS
#   Claude cannot put anything on the real calendar. Ever.
#   The most it can do is PROPOSE a time. The owner says yes before anything
#   becomes real. This is deliberate: a confidently wrong booking is a truck
#   showing up at the wrong house.
#
# WHAT THIS FILE DOES NOT DO
#   Does not know what Twilio is. Does not know what HTTP is.
#   Messages in, a message out. That's the entire contract.
#   Staying this dumb about the outside world is what makes it testable --
#   you can run a whole fake conversation without a phone existing.
#
# CURRENT STATE
#   run_agent() below is a stub -- it ignores the message and returns a canned
#   line. No Claude call, no tools, no memory yet. It's the seam everything
#   else plugs into.
#
# =============================================================================

import anthropic
from dotenv import load_dotenv
from database import save_message, get_history
from tools import TOOL_DEFINITIONS, execute_tool

load_dotenv()

#Create agent using claudes SDK
client = anthropic.Anthropic()

SYSTEM_PROMPT = (
    "You are a missed-call recovery agent for a small business. "
    "Your job is to respond to people who have texted in or a missed call from a poteintial/existing customer. "
    "understand what they need, and collect their information for the business owner. "

    "RULES: "
    "1. Always introduce yourself warmly and ask how you can help. "
    "2. Always use send_sms to communicate with the caller — never respond directly without sending an SMS. "
    "3. Collect three things before logging: the caller's name, what service they need, and their preferred time. "
    "4. Only use log_to_csv once you have all three pieces of information. "
    "5. Never promise specific appointment times — tell them the business owner will confirm. "
    "6. Be concise — this is SMS, not email. Keep messages short. "
    "7. If someone is angry or upset, be empathetic and assure them someone will follow up soon. "
)


def run_agent(incoming_phone_number: str, incoming_message: str):
    save_message(incoming_phone_number, "user", incoming_message)
    history = get_history(incoming_phone_number)
    
    # Inject caller's number so Claude knows who to text
    system_with_number = SYSTEM_PROMPT + f" The caller's phone number is {incoming_phone_number}. Always use this exact number when calling send_sms."
    
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system_with_number,  # use this instead of SYSTEM_PROMPT
            tools=TOOL_DEFINITIONS,
            messages=history
        )
        if response.stop_reason == "tool_use":
                # Step 1 — Add Claude's response to history
                # Claude said "I want to use a tool" — we need to remember that
                history.append({
                    "role": "assistant",
                    "content": response.content  # the full response including tool call
                })

                # Step 2 — Find which tool Claude wants and execute it
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"Claude using tool: {block.name} with args: {block.input}")

                        # Run the actual tool — this calls send_sms or log_to_csv
                        result = execute_tool(block.name, block.input, incoming_phone_number)

                        # Package the result in the format Claude expects back
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,  # must match the tool call id
                            "content": result
                        })

                # Step 3 — Send tool results back to Claude and loop again
                history.append({
                    "role": "user",
                    "content": tool_results
                })
                # loop continues — Claude sees the results and decides next step
        elif response.stop_reason == "end_turn":
            final_response = next(
                block.text for block in response.content
                if hasattr(block, "text")
            )
            save_message(incoming_phone_number, "assistant", final_response)
            return final_response
