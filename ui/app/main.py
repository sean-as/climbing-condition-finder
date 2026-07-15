from fastapi import FastAPI, Request, APIRouter, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from api.forecast import forecast_router
from api.areas import areas_router
from services.areas import get_area


crag_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@crag_router.get("/area/{area_id}", response_class=HTMLResponse)
def crag_page(request: Request, area_id: str):
    result = get_area(area_id)
    if result is None:
        raise HTTPException(404, "area not found")
    if result.node.is_leaf:
        return templates.TemplateResponse(request, "crag.html", {"area_id": area_id, "node": result.node})
    return templates.TemplateResponse(request, "branch.html", {"node": result.node, "children": result.children})

@crag_router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return RedirectResponse(f"/area/1e18b6dd-d8b1-5c36-b555-175190184622")

app = FastAPI(title="Climbing Condition Finder")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(forecast_router)
app.include_router(areas_router)
app.include_router(crag_router)



