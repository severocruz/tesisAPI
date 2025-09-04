from sqlalchemy.orm import Session
from models import Instrumentos
from schemas.instrumentos import InstrumentosCreate, InstrumentosOut


def get_all(db: Session) -> list[InstrumentosOut]:
    return db.query(Instrumentos).all()

def get_by_id(db: Session, id: int) -> InstrumentosOut | None:
    return db.query(Instrumentos).filter(Instrumentos.id == id).first()

def create(db: Session, item: InstrumentosCreate) -> InstrumentosOut:
    db_item = Instrumentos(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_by_id_genero(db: Session, id_genero: int) -> list[InstrumentosOut]:
    return db.query(Instrumentos).filter(Instrumentos.id_genero == id_genero).all()
