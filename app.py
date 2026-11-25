import streamlit as st
from datetime import date, datetime
from app.db import init, seed, connect
from app.engine import risk_signals, sms_valid
from app.advisory import generate
from app.weather import WeatherSnapshot, as_dict, fetch_openweather
from app.messaging import send_africastalking_sms, send_twilio_whatsapp
from app.supabase_store import save_advisory as save_supabase_advisory, save_feedback as save_supabase_feedback
from app.evidence import EVIDENCE
from app.evaluation import confusion_counts, metrics

st.set_page_config(page_title="Taita AgriAlert AI", page_icon="🌱", layout="wide")
init(); seed()
st.title("🌱 Taita AgriAlert AI")
st.caption("Capstone MVP • synthetic demo data • no live messaging • advisory signals are NOT validated agronomic models")
with st.sidebar:
    st.header("Farm profile")
    farmer_id=st.text_input("Demo farmer ID", "DEMO-001")
    ward=st.selectbox("Ward", ["Wundanyi","Voi","Mwatate","Taveta"])
    crop=st.selectbox("Crop", ["Maize","Tomatoes","Onions"])
    stage=st.selectbox("Reported growth stage", ["Seedling","Vegetative","Tasseling","Silking","Flowering","Fruiting","Bulking","Maturity","Harvest"])
    language=st.selectbox("Language", ["Swahili","English"])
    device=st.selectbox("Device", ["Feature phone","Smartphone"])
    st.caption("Stage is manually selected. Verified GDD stage inference is not implemented.")

st.header("Weather inputs")
st.caption("Live weather is fetched only when you provide coordinates and choose Fetch. Ward-level coordinates should be verified before a real deployment.")
with st.expander("Fetch live OpenWeather data", expanded=False):
    wx1,wx2=st.columns(2)
    with wx1: lat=st.number_input("Latitude", value=-3.3960, format="%.5f", help="Approximate Taita Taveta demo coordinate; verify the exact farm/ward location.")
    with wx2: lon=st.number_input("Longitude", value=38.3570, format="%.5f", help="Approximate Taita Taveta demo coordinate; verify the exact farm/ward location.")
    if st.button("Fetch current weather + forecast"):
        try:
            live=fetch_openweather(lat,lon)
            st.session_state["live_weather"]=as_dict(live)
            st.success("Weather received from OpenWeather.")
        except Exception as exc:
            st.error(f"Weather request failed: {type(exc).__name__}: {exc}")
if st.session_state.get("live_weather"):
    st.info("Live weather is available below. You can still edit manual inputs for testing.")
    st.json(st.session_state["live_weather"])
a,b,c,d=st.columns(4)
with a: temp=st.number_input("Temperature °C", value=25.0, min_value=-20.0, max_value=60.0)
with b: rain=st.number_input("Rainfall mm", value=0.0, min_value=0.0, max_value=500.0)
with c: humidity=st.number_input("Relative humidity %", value=50.0, min_value=0.0, max_value=100.0)
with d: wind=st.number_input("Wind km/h", value=5.0, min_value=0.0, max_value=250.0)
obs_note=st.text_input("Weather observation note (optional)")
if st.session_state.get("live_weather"):
    live=st.session_state["live_weather"]
    weather=WeatherSnapshot(live["source"],live["observed_at"],live["temperature_c"],live["rainfall_mm"],live["humidity_pct"],live["wind_kmh"],live.get("notes",""),live.get("forecast_rain_24h_mm"),live.get("forecast_summary",""))
else:
    weather=WeatherSnapshot("Manual demo input",datetime.now().isoformat(timespec="minutes"),temp,rain,humidity,wind,obs_note)
with st.expander("Weather data record"):
    st.json(as_dict(weather))
    if weather.validate(): st.error("; ".join(weather.validate()))
    else: st.success("Basic range validation passed (not a meteorological quality check).")

st.header("Farmer observations")
x,y=st.columns(2)
with x: wet=st.checkbox("Wet conditions reported")
with y: stress=st.checkbox("Water-stress concern reported")
flags={"wet_conditions":wet,"water_stress":stress}
risks=risk_signals(crop,stage,as_dict(weather),flags)
for r in risks:
    st.warning(r.risk); st.write("**Drivers:** "+"; ".join(r.drivers)); st.caption(r.caveat)

st.header("Advisory")
risk=risks[0].risk
result=generate(crop,ward,stage,risk,language,weather=as_dict(weather))
body=result["text"]
st.text_area("SMS preview",body,height=100)
ok,why=sms_valid(body)
st.write(f"**SMS validation:** {'PASS' if ok else 'FAIL'} — {why}")
st.write(f"**Generation mode:** `{result['mode']}`")
st.caption("Evidence status: "+result.get("grounding",""))
if result.get("reason"): st.caption("Fallback reason: "+result["reason"])
if st.button("Save demo advisory",disabled=not ok):
    with connect() as db:
        cur=db.execute("insert into advisories(farmer_id,risk,body,mode) values(?,?,?,?)",(None,risk,body,result['mode']))
        st.session_state["last_advisory_id"]=cur.lastrowid
        st.session_state["last_advisory_text"]=body
    st.success("Saved to local advisory log.")
    try:
        saved=save_supabase_advisory({"farmer_ref":farmer_id,"ward":ward,"crop":crop,"stage":stage,"risk":risk,"body":body,"mode":result['mode'],"language":language,"weather_source":weather.source})
        if saved: st.success("Also saved to Supabase.")
    except Exception as exc: st.warning(f"Supabase save not completed: {type(exc).__name__}")

last_id=st.session_state.get("last_advisory_id")
if last_id:
    st.subheader("Advisory feedback (simulation)")
    feedback=st.radio("Was this message useful?",["Useful","Not useful","Unsure"],horizontal=True,key="feedback_choice")
    fb_note=st.text_input("Optional feedback note",key="feedback_note")
    if st.button("Save feedback"):
        with connect() as db:
            db.execute("insert into feedback(advisory_id,response) values(?,?)",(last_id,feedback+ (" — "+fb_note if fb_note else "")))
        st.success("Feedback recorded locally.")
        try:
            save_supabase_feedback({"advisory_local_id":int(last_id),"response":feedback,"note":fb_note})
        except Exception as exc: st.warning(f"Supabase feedback save not completed: {type(exc).__name__}")

st.header("Send a test message (to your own verified test device only)")
st.caption("Do not message farmers or other people without informed consent and project/organization authorization. Provider fees and sandbox rules may apply.")
channel=st.radio("Channel",["Africa's Talking SMS","Twilio WhatsApp"],horizontal=True)
test_number=st.text_input("Your own test phone number",placeholder="+2547XXXXXXXX")
confirm=st.checkbox("I confirm this is my own number or a test recipient who has explicitly agreed.")
if st.button("Send test message",disabled=not (confirm and test_number.strip())):
    try:
        if channel.startswith("Africa"):
            receipt=send_africastalking_sms(test_number.strip(),body)
        else:
            receipt=send_twilio_whatsapp(test_number.strip(),body)
        st.success("Provider accepted the test message request.")
        st.json(receipt)
    except Exception as exc:
        st.error(f"Message was not sent: {type(exc).__name__}: {exc}")

st.header("Feature-phone USSD simulator")
menu=st.radio("Menu",["1 Today's advice","2 Three-day outlook","3 Help","4 Opt out"],horizontal=True)
if menu.startswith("1"): st.code("CON "+body)
elif menu.startswith("2"): st.code("CON Outlook unavailable in demo. Use a verified forecast and local extension guidance.")
elif menu.startswith("3"): st.code("CON Review your crop and stage. Contact an extension officer for verified recommendations.")
else: st.code("END Opt-out preview only. This simulation does not change consent or contact a service.")

st.header("Evidence registry")
st.dataframe(EVIDENCE,use_container_width=True)
st.warning("The listed sources are placeholders, not citations. Replace with authoritative, dated sources and review crop-specific advice before field use.")

st.header("Evaluation sandbox")
st.caption("Toy example to demonstrate metric calculations; this is not model performance or field validation.")
expected=[1,1,0,0,1,0,1,0]; predicted=[1,0,0,0,1,1,1,0]
counts=confusion_counts(expected,predicted); ms=metrics(counts)
cols=st.columns(4)
for col,key in zip(cols,["tp","tn","fp","fn"]): col.metric(key.upper(),counts[key])
cols=st.columns(4)
for col,key in zip(cols,["precision","recall","specificity","accuracy"]): col.metric(key.capitalize(),"N/A" if ms[key] is None else ms[key])

st.header("Synthetic cohort and logs")
with connect() as db:
    farmers=db.execute("select ward,crop,language,device,planting_date from farmers").fetchall()
    logs=db.execute("select id,risk,body,mode,created_at from advisories order by id desc limit 20").fetchall()
    feedback_rows=db.execute("select advisory_id,response,created_at from feedback order by id desc limit 20").fetchall()
st.metric("Synthetic farmers",len(farmers)); st.dataframe([dict(x) for x in farmers],use_container_width=True)
st.write("Advisory log"); st.dataframe([dict(x) for x in logs],use_container_width=True)
st.write("Feedback log"); st.dataframe([dict(x) for x in feedback_rows],use_container_width=True)
st.info("No messages are sent. No real farmers are contacted. Seeded records are synthetic. Treat all risk signals as demonstrations only.")
