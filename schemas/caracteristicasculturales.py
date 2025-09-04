from pydantic import BaseModel
from pydantic import ConfigDict

class CaracteristicasCulturalesBase(BaseModel):
    nombre: str
    id_genero: int
    descripcion: str
    imagen: str
    created_at: str
    updated_at: str

class CaracteristicasCulturalesCreate(CaracteristicasCulturalesBase):
    pass

class CaracteristicasCulturalesOut(CaracteristicasCulturalesBase):
    id: int
   

model_config = ConfigDict(from_attributes=True)
