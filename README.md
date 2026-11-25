# Pula — provider-integrated capstone demo

This version includes provider adapters for OpenWeather, Groq, Africa's Talking SMS, Twilio WhatsApp, Supabase persistence, and an Africa's Talking USSD callback service. **No API credentials are included.** The app runs in fallback/local mode until you configure secrets.

## 1. Local setup

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Windows: copy .env.example .env
```

Fill `.env` with your own credentials. Never commit `.env` or `.streamlit/secrets.toml` to Git. For local Streamlit secrets, create `.streamlit/secrets.toml` with the same TOML key names and quoted values. On Streamlit Community Cloud, add these values under App settings → Secrets.

Start the UI:

```bash
streamlit run app.py
```

Run tests with `pytest -q`.

## 2. Provider configuration

- **OpenWeather:** set `OPENWEATHER_API_KEY`. The app calls Current Weather (`/data/2.5/weather`) and 5 day / 3-hour forecast (`/data/2.5/forecast`). This avoids assuming the account has One Call access. Enter farm/ward coordinates in the UI; defaults are approximate demo coordinates and must be verified before use.
- **Groq:** set `GROQ_API_KEY` and optionally `GROQ_MODEL` (default `llama-3.3-70b-versatile`; change it to a model enabled in your Groq account). Uses the official Groq Python SDK chat-completions API. The model is constrained to supplied facts; template fallback is used if generation fails. Review all generated text before any field use.
- **Africa's Talking SMS:** set `AT_USERNAME`, `AT_API_KEY`, and optionally `AT_SENDER_ID`. The test-send control is intended only for your own verified test phone or an explicitly consenting test recipient.
- **Twilio WhatsApp:** set `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM`. Sandbox recipients may need to join the sandbox first. WhatsApp business-initiated messaging may require approved templates and opt-in; the app does not bypass provider policies.
- **Supabase:** set `SUPABASE_URL` and `SUPABASE_KEY`. Run `supabase/schema.sql` in the Supabase SQL Editor. The supplied schema has RLS enabled and no public policies. Use a restricted server-side key; never put a service-role key in browser/client code or a public repository. Add authenticated policies before enabling multi-user access.
- **Streamlit Cloud:** deploy the repository and configure the same secrets in App settings → Secrets. Do not upload a secrets file to GitHub.

## 3. USSD callback

`ussd_webhook.py` is a separate FastAPI service because Streamlit is not an inbound USSD callback server. Deploy it to an HTTPS host and configure the callback URL as `https://YOUR-HOST/ussd` in your Africa's Talking USSD application. Test with the provider sandbox first. The current menu is a safe informational placeholder and does not register farmers, change consent, or fetch personal records.

Run locally for development:

```bash
uvicorn ussd_webhook:app --host 127.0.0.1 --port 8000
```

A public HTTPS tunnel/host is needed for provider callbacks; localhost is not reachable by the provider.

## 4. Suggested integration test order

1. Run `pytest -q` and launch Streamlit without secrets; confirm fallback mode works.
2. Configure OpenWeather and fetch a known location; check timestamp, units and forecast response.
3. Configure Groq and generate a test advisory; manually review English and Swahili.
4. Configure Supabase and confirm rows appear in the private tables.
5. Test SMS to your own verified number using the provider's test/sandbox setup.
6. Test WhatsApp only with an opted-in sandbox/approved recipient.
7. Deploy and test the USSD callback in sandbox.

## Safety, privacy and limitations

- The crop risk logic is still a prototype signal, **not a validated agronomic model**. Weather data does not automatically establish crop disease or irrigation need.
- No pesticide/fertilizer dose, disease diagnosis, yield promise or numeric crop threshold is generated as an authoritative recommendation.
- Do not enroll or message real farmers until the project has adult/organizational authorization, clear informed consent, an opt-out workflow, a privacy notice, secure authentication, data retention rules and reviewed extension guidance.
- Do not store phone numbers in the prototype database. The test-send interface is for your own test number only.
- Supabase RLS is enabled with no public access policies. Authentication and least-privilege policies are still required before multi-user operation.
- Weather API coverage/entitlements, messaging sender approvals, WhatsApp templates, costs, model availability and account quotas depend on your provider accounts and must be checked in those dashboards.
- Swahili wording requires review by a fluent speaker and local extension staff.
- Synthetic farmer records and toy evaluation metrics are not field research or measured model performance.
