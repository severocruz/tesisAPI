from pydantic import BaseModel
from pydantic import ConfigDict

class InstrumentosBase(BaseModel):
    nombre: str
    tipo: str
    descripcion: str
    imagen: str
    id_genero: int
    created_at: str
    updated_at: str

class InstrumentosCreate(InstrumentosBase):
    pass

class InstrumentosOut(InstrumentosBase):
    id: int

model_config = ConfigDict(from_attributes=True)
