from pydantic import BaseModel
from pydantic import ConfigDict
from datetime import datetime

class CaracteristicasCulturalesBase(BaseModel):
    nombre: str
    id_genero: int
    descripcion: str
    imagen: str
    created_at: datetime
    updated_at: datetime

class CaracteristicasCulturalesCreate(CaracteristicasCulturalesBase):
    pass

class CaracteristicasCulturalesOut(CaracteristicasCulturalesBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
