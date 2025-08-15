from fastapi import FastAPI, Body, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List, Dict
from datetime import datetime

app = FastAPI()
MESSAGES: List[Dict] = []


@app.post("/inbox")
async def inbox(payload: Dict = Body(...)):
    payload["ts"] = datetime.utcnow().isoformat() + "Z"
    MESSAGES.append(payload)
    if len(MESSAGES) > 100:
        del MESSAGES[:-100]
    return {"ok": True}


@app.get("/inbox")
def list_inbox():
    return {"messages": MESSAGES}


@app.post("/clear")
def clear_inbox():
    MESSAGES.clear()
    return {"ok": True}


# Twilio-compatible endpoint
@app.post("/2010-04-01/Accounts/{sid}/Messages.json")
async def send_sms(sid: str, request: Request):
    form = await request.form()
    data = dict(form)  # includes any extra fields
    to = data.get("To")
    body = data.get("Body")
    from_ = data.get("From")  # optional
    mssid = data.get("MessagingServiceSid")  # optional

    # Log everything we got to see what Appwrite is actually posting
    print(f"[FAKE-TWILIO] sid={sid} payload={data}")
    MESSAGES.append(
        {
            "to": to,
            "frm": from_,
            "body": body,
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    )

    # Minimal Twilio-style validation: need To + Body + (From or MessagingServiceSid)
    if not to or not body or not (from_ or mssid):
        return JSONResponse(
            status_code=400,
            content={
                "code": 21601,
                "message": "Missing required parameter: 'To'/'Body' or sender",
            },
        )

    # Return Twilio-like success
    return JSONResponse(
        status_code=201,
        content={
            "sid": "SM_fake123",
            "status": "queued",
            "to": to,
            "from": from_,
            "messaging_service_sid": mssid,
            "body": body,
        },
    )


@app.get("/", response_class=HTMLResponse)
def home():
    rows = "".join(
        f"<tr><td>{m.get('to', '')}</td><td>{m.get('frm', '')}</td><td>{m.get('body', '')}</td><td>{m.get('ts', '')}</td></tr>"
        for m in reversed(MESSAGES)
    )
    return f"""
    <html><head><meta charset="utf-8"><title>SMS Capture</title>
    <style>table{{width:100%;border-collapse:collapse}}td,th{{border:1px solid #333;padding:6px}}</style>
    </head><body>
    <h3>Captured SMS (dev)</h3>
    <table><thead><tr><th>To</th><th>From</th><th>Body</th><th>Time (UTC)</th></tr></thead><tbody>{rows}</tbody></table>
    </body></html>"""
