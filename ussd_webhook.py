"""Africa's Talking USSD callback. Deploy separately as a small HTTPS web service."""
import os
from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse
app=FastAPI(title="Pula USSD callback")

@app.post("/ussd", response_class=PlainTextResponse)
async def ussd(sessionId: str = Form(...), serviceCode: str = Form(...), phoneNumber: str = Form(...), text: str = Form("")):
    parts=text.split("*") if text else []
    if not parts: return "CON Karibu Pula\n1. Ushauri wa mazao\n2. Msaada\n3. Toka"
    choice=parts[0]
    if choice=="1": return "END Tafadhali kagua shamba lako na wasiliana na afisa ugani kwa ushauri uliothibitishwa."
    if choice=="2": return "END Pula hutoa taarifa za hali ya hewa. Ushauri wa kilimo uthibitishwe na afisa ugani."
    if choice=="3": return "END Asante. Hakuna usajili uliobadilishwa kwenye demo hii."
    return "END Chaguo si sahihi. Tafadhali jaribu tena."
