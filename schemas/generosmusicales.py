from pydantic import BaseModel
from pydantic import ConfigDict
from datetime import datetime
from typing import List, Optional

from schemas.caracteristicasculturales import CaracteristicasCulturalesOut

class GenerosMusicalesBase(BaseModel):
    nombre: str
    nombre_prediccion: str
    descripcion: str
    imagen: str
    video_link: str
    porcentaje: float
    created_at: datetime
    updated_at: datetime

class GenerosMusicalesCreate(GenerosMusicalesBase):
    pass

class GenerosMusicalesOut(GenerosMusicalesBase):
    id: int

    model_config = {"from_attributes": True}
    
model_config = ConfigDict(from_attributes=True)