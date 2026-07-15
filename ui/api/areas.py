from fastapi import APIRouter, Response, HTTPException
from schemas.areas import AreaResponse
from services.areas import get_area

areas_router = APIRouter()


@areas_router.get("/api/areas/{id}", response_model=AreaResponse)
def area(id: str, response: Response):
    result = get_area(id)
    if result is None:
        raise HTTPException(404, "area not found")
    response.headers["Cache-Control"] = "public, max-age=3600"   # hierarchy ~static
    return result