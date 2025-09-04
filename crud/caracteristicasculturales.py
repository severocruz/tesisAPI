from sqlalchemy.orm import Session
from models import CaracteristicasCulturales
from schemas.caracteristicasculturales import CaracteristicasCulturalesCreate, CaracteristicasCulturalesOut


def get_all(db: Session) -> list[CaracteristicasCulturalesOut]:
    return db.query(CaracteristicasCulturales).all()

def get_by_id(db: Session, id: int) -> CaracteristicasCulturalesOut | None:
    return db.query(CaracteristicasCulturales).filter(CaracteristicasCulturales.id == id).first()

def create(db: Session, item: CaracteristicasCulturalesCreate) -> CaracteristicasCulturalesOut:
    db_item = CaracteristicasCulturales(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_by_id_genero(db: Session, id_genero: int) -> list[CaracteristicasCulturalesOut]:
    return db.query(CaracteristicasCulturales).filter(CaracteristicasCulturales.id_genero == id_genero).all()
