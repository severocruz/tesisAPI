from pydantic import BaseModel
from pydantic import ConfigDict
from datetime import datetime

class OrigenesGeograficosBase(BaseModel):
    nombre: str
    descripcion: str
    latitud: float
    longitud: float
    imagen: str
    id_genero: int
    created_at: datetime
    updated_at: datetime

class OrigenesGeograficosCreate(OrigenesGeograficosBase):
    pass

class OrigenesGeograficosOut(OrigenesGeograficosBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
