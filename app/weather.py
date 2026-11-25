"""OpenWeather adapter using Current Weather + 5 day / 3-hour forecast APIs."""
from dataclasses import dataclass
from datetime import datetime, timezone
import requests
from .config import get_secret

@dataclass
class WeatherSnapshot:
    source: str
    observed_at: str
    temperature_c: float | None = None
    rainfall_mm: float | None = None
    humidity_pct: float | None = None
    wind_kmh: float | None = None
    notes: str = ""
    forecast_rain_24h_mm: float | None = None
    forecast_summary: str = ""

    def validate(self):
        errors=[]
        if self.temperature_c is not None and not (-20 <= self.temperature_c <= 60): errors.append("Temperature outside demo validation range.")
        if self.rainfall_mm is not None and not (0 <= self.rainfall_mm <= 500): errors.append("Rainfall outside demo validation range.")
        if self.humidity_pct is not None and not (0 <= self.humidity_pct <= 100): errors.append("Humidity must be 0–100%.")
        if self.wind_kmh is not None and not (0 <= self.wind_kmh <= 250): errors.append("Wind outside demo validation range.")
        return errors

def fetch_openweather(lat: float, lon: float, api_key: str | None = None) -> WeatherSnapshot:
    key = api_key or get_secret("OPENWEATHER_API_KEY")
    if not key:
        raise RuntimeError("OPENWEATHER_API_KEY is not configured.")
    if not (-90 <= float(lat) <= 90 and -180 <= float(lon) <= 180):
        raise ValueError("Latitude/longitude are outside valid ranges.")
    params={"lat":lat,"lon":lon,"appid":key,"units":"metric"}
    current=requests.get("https://api.openweathermap.org/data/2.5/weather",params=params,timeout=12)
    current.raise_for_status(); cur=current.json()
    forecast=requests.get("https://api.openweathermap.org/data/2.5/forecast",params=params,timeout=12)
    forecast.raise_for_status(); fc=forecast.json()
    now=datetime.now(timezone.utc).timestamp()
    upcoming=[x for x in fc.get("list",[]) if now <= x.get("dt",0) <= now+24*3600]
    rain24=sum(float(x.get("rain",{}).get("3h",0) or 0) for x in upcoming)
    summaries=list(dict.fromkeys(x.get("weather",[{}])[0].get("description","") for x in upcoming if x.get("weather")))
    w=cur.get("wind",{}).get("speed")
    snap=WeatherSnapshot(
        source="OpenWeather Current Weather + 5 day / 3-hour forecast",
        observed_at=datetime.fromtimestamp(cur.get("dt",now),timezone.utc).isoformat(),
        temperature_c=cur.get("main",{}).get("temp"),
        rainfall_mm=float(cur.get("rain",{}).get("1h",0) or 0),
        humidity_pct=cur.get("main",{}).get("humidity"),
        wind_kmh=round(float(w)*3.6,1) if w is not None else None,
        notes=(cur.get("weather",[{}])[0].get("description","") or ""),
        forecast_rain_24h_mm=round(rain24,1),
        forecast_summary="; ".join(summaries[:3])
    )
    errors=snap.validate()
    if errors: raise ValueError("Weather response failed validation: "+"; ".join(errors))
    return snap

def as_dict(snapshot):
    return {"temperature_c":snapshot.temperature_c,"rainfall_mm":snapshot.rainfall_mm,"humidity_pct":snapshot.humidity_pct,"wind_kmh":snapshot.wind_kmh,"source":snapshot.source,"observed_at":snapshot.observed_at,"notes":snapshot.notes,"forecast_rain_24h_mm":snapshot.forecast_rain_24h_mm,"forecast_summary":snapshot.forecast_summary}
