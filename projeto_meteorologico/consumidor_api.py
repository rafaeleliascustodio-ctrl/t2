from datetime import datetime
from typing import TypedDict
from zoneinfo import ZoneInfo

import openmeteo_requests
import requests_cache
from retry_requests import retry

API_URL = "https://api.open-meteo.com/v1/forecast"
LATITUDE = -26.4851
LONGITUDE = -49.0713
TIMEZONE = "America/Sao_Paulo"

cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


class DadosMeteorologicos(TypedDict):
    temperatura: float
    umidade_relativa: float
    sensacao_termica: float
    precipitacao: float
    velocidade_vento: float
    horario: str


def obter_dados_meteorologicos(atualizar: bool = False) -> DadosMeteorologicos:
    if atualizar:
        cache_session.cache.clear()

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "wind_speed_10m",
        ],
        "timezone": TIMEZONE,
        "wind_speed_unit": "kmh",
    }
    response = openmeteo.weather_api(API_URL, params=params)[0]
    current = response.Current()
    timezone = response.Timezone().decode("utf-8")

    return {
        "temperatura": float(current.Variables(0).Value()),
        "umidade_relativa": float(current.Variables(1).Value()),
        "sensacao_termica": float(current.Variables(2).Value()),
        "precipitacao": float(current.Variables(3).Value()),
        "velocidade_vento": float(current.Variables(4).Value()),
        "horario": datetime.fromtimestamp(
            current.Time(), tz=ZoneInfo(timezone)
        ).strftime("%d/%m/%Y %H:%M"),
    }
	