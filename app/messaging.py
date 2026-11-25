"""Outbound messaging adapters. Call only after explicit recipient consent."""
import requests
from .config import get_secret

def send_africastalking_sms(to: str, message: str):
    username=get_secret("AT_USERNAME"); api_key=get_secret("AT_API_KEY"); sender=get_secret("AT_SENDER_ID")
    if not username or not api_key: raise RuntimeError("AT_USERNAME and AT_API_KEY are required.")
    data={"username":username,"to":to,"message":message}
    if sender: data["from"]=sender
    response=requests.post("https://api.africastalking.com/version1/messaging",data=data,headers={"apiKey":api_key,"Accept":"application/json"},timeout=15)
    response.raise_for_status()
    return response.json()

def send_twilio_whatsapp(to: str, message: str):
    sid=get_secret("TWILIO_ACCOUNT_SID"); token=get_secret("TWILIO_AUTH_TOKEN"); sender=get_secret("TWILIO_WHATSAPP_FROM")
    if not all([sid,token,sender]): raise RuntimeError("Twilio Account SID, Auth Token and WhatsApp sender are required.")
    from twilio.rest import Client
    if not to.startswith("whatsapp:"): to="whatsapp:"+to
    if not sender.startswith("whatsapp:"): sender="whatsapp:"+sender
    msg=Client(sid,token).messages.create(body=message,from_=sender,to=to)
    return {"sid":msg.sid,"status":msg.status}
