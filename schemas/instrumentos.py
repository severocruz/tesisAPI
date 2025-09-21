from pydantic import BaseModel
from pydantic import ConfigDict
from datetime import datetime

class InstrumentosBase(BaseModel):
    nombre: str
    tipo: str
    descripcion: str
    imagen: str
    id_genero: int
    created_at: datetime
    updated_at: datetime

class InstrumentosCreate(InstrumentosBase):
    pass

class InstrumentosOut(InstrumentosBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
