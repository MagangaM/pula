import sqlite3, hashlib, os, random
DB_PATH=os.getenv("DB_PATH", "pula.db")


def connect():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c

def init():
    with connect() as c:
        c.executescript('''CREATE TABLE IF NOT EXISTS farmers(id INTEGER PRIMARY KEY, phone_hash TEXT, consent INTEGER, language TEXT, device TEXT, ward TEXT, crop TEXT, planting_date TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP); CREATE TABLE IF NOT EXISTS advisories(id INTEGER PRIMARY KEY, farmer_id INTEGER, risk TEXT, body TEXT, mode TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP); CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY, advisory_id INTEGER, response TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);''')

def seed():
    init()
    wards=["Wundanyi","Voi","Mwatate","Taveta"]
    crops=["Maize","Tomatoes","Onions"]
    with connect() as c:
        if c.execute("select count(*) from farmers").fetchone()[0]: return
        rng=random.Random(42)
        for i in range(50):
            phone=f"SIMULATED-{i:03d}"
            ph=hashlib.sha256(phone.encode()).hexdigest()
            c.execute("insert into farmers(phone_hash,consent,language,device,ward,crop,planting_date) values(?,?,?,?,?,?,?)",(ph,1,rng.choice(["Swahili","English"]),rng.choice(["Feature phone","Smartphone"]),rng.choice(wards),rng.choice(crops),"2026-10-01"))
