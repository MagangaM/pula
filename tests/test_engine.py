from app.engine import gsm7_safe, sms_valid, risk_signals

def test_sms_gsm7():
    assert sms_valid("Farm check: monitor crop.")[0]
    assert not gsm7_safe("🌱")

def test_sms_length():
    assert not sms_valid("a"*161)[0]

def test_maize_flag():
    r=risk_signals("Maize","Silking",{}, {"water_stress":True})
    assert "Water-stress" in r[0].risk

def test_no_flag():
    r=risk_signals("Tomatoes","Vegetative",{}, {})
    assert r[0].risk == "Routine monitoring"

def test_weather_range_validation():
    from app.weather import WeatherSnapshot
    assert WeatherSnapshot('demo','now',25,0,55,4).validate()==[]
    assert WeatherSnapshot('demo','now',25,0,120,4).validate()

def test_evaluation_metrics():
    from app.evaluation import confusion_counts, metrics
    c=confusion_counts([1,1,0,0],[1,0,0,1])
    assert c=={'tp':1,'tn':1,'fp':1,'fn':1}
    assert metrics(c)['accuracy']==0.5
