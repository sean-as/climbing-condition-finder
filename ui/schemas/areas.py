from pydantic import BaseModel


class AreaRef(BaseModel):        
    id: str
    area_name: str

class AreaNode(BaseModel):
    id: str
    area_name: str
    latitude: float | None
    longitude: float | None
    parent_id: str | None
    country: str | None
    region: str | None
    is_leaf: bool

class AreaResponse(BaseModel):
    node: AreaNode
    children: list[AreaRef]      # direct children (drill-down)
