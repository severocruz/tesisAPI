from pydantic import BaseModel
from pydantic import ConfigDict
from datetime import datetime

class GenerosMusicalesBase(BaseModel):
    nombre: str
    nombre_prediccion: str
    descripcion: str
    imagen: str
    video_link: str
    created_at: datetime
    updated_at: datetime

class GenerosMusicalesCreate(GenerosMusicalesBase):
    pass

class GenerosMusicalesOut(GenerosMusicalesBase):
    id: int

    model_config = {"from_attributes": True}
    
model_config = ConfigDict(from_attributes=True)