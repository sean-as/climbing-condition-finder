from datetime import datetime
from pydantic import BaseModel

class Point(BaseModel):
    t: datetime
    v: float | None

class Series(BaseModel):
    source: str
    unit: str | None
    label: str | None = None
    points: list[Point]

class ForecastResponse(BaseModel):
    area_id: str
    series: dict[str, list[Series]]