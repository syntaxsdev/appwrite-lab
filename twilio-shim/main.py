from fastapi import FastAPI, Body, Form
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

# Twilio-compatible endpoint
@app.post("/2010-04-01/Accounts/{sid}/Messages.json")
async def send_sms(sid: str, To: str = Form(...), From: str = Form(...), Body: str = Form(...)):
    print(f"[FAKE-TWILIO] SID={sid} To={To} From={From} Body={Body}")
    MESSAGES.append({
        "to": To,
        "frm": From,
        "body": Body,
        "ts": datetime.utcnow().isoformat() + "Z"
    })
    return JSONResponse(status_code=201, content={
        "sid": "SM_fake123",
        "status": "queued",
        "to": To,
        "from": From,
        "body": Body,
    })

@app.get("/", response_class=HTMLResponse)
def home():
    rows = "".join(
        f"<tr><td>{m.get('to','')}</td><td>{m.get('frm','')}</td><td>{m.get('body','')}</td><td>{m.get('ts','')}</td></tr>"
        for m in reversed(MESSAGES)
    )
    return f"""
    <html><head><meta charset="utf-8"><title>SMS Capture</title>
    <style>table{{width:100%;border-collapse:collapse}}td,th{{border:1px solid #333;padding:6px}}</style>
    </head><body>
    <h3>Captured SMS (dev)</h3>
    <table><thead><tr><th>To</th><th>From</th><th>Body</th><th>Time (UTC)</th></tr></thead><tbody>{rows}</tbody></table>
    </body></html>"""
