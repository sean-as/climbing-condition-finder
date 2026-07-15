from fastapi import APIRouter, Response
from schemas.forecast import ForecastResponse
from services.forecast import get_forecast

forecast_router = APIRouter()

@forecast_router.get("/api/forecast", response_model=ForecastResponse)
def forecast(area_id: str, response: Response):
    response.headers["Cache-Control"] = "public, max-age=3600"
    return get_forecast(area_id)