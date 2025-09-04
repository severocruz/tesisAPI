from pydantic import BaseModel

# Schema base (campos comunes)
class GenerosMusicalesBase(BaseModel):
    nombre: str
    nombre_prediccion: str
    descripcion: str
    imagen: str
    video_link: str
    created_at: str | None = None
    updated_at: str | None = None

# Para crear un usuario (no incluye id porque lo genera la BD)
class GenerosMusicalesCreate(GenerosMusicalesBase):
    pass

# Para actualizar un usuario (puede ser parcial, con todos los campos opcionales)
class GenerosMusicalesUpdate(BaseModel):
    nombre: str | None = None
    nombre_prediccion: str | None = None
    descripcion: str | None = None
    imagen: str | None = None
    video_link: str | None = None

# Lo que devuelve la API (incluye id)
class GenerosMusicalesOut(GenerosMusicalesBase):
    id: int

    class Config:
        orm_mode = True   # 👈 Importante para trabajar con SQLAlchemy
