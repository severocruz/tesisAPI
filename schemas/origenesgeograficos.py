from pydantic import BaseModel
from pydantic import ConfigDict

class OrigenesGeograficosBase(BaseModel):
    nombre: str
    descripcion: str
    latitud: str
    longitud: str
    imagen: str
    id_genero: int
    created_at: str
    updated_at: str

class OrigenesGeograficosCreate(OrigenesGeograficosBase):
    pass

class OrigenesGeograficosOut(OrigenesGeograficosBase):
    id: int

model_config = ConfigDict(from_attributes=True)
