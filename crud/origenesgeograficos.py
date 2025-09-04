from sqlalchemy.orm import Session
from models import OrigenesGeograficos
from schemas.origenesgeograficos import OrigenesGeograficosCreate, OrigenesGeograficosOut


def get_all(db: Session) -> list[OrigenesGeograficosOut]:
    return db.query(OrigenesGeograficos).all()

def get_by_id(db: Session, id: int) -> OrigenesGeograficosOut | None:
    return db.query(OrigenesGeograficos).filter(OrigenesGeograficos.id == id).first()

def create(db: Session, item: OrigenesGeograficosCreate) -> OrigenesGeograficosOut:
    db_item = OrigenesGeograficos(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_by_id_genero(db: Session, id_genero: int) -> list[OrigenesGeograficosOut]:
    return db.query(OrigenesGeograficos).filter(OrigenesGeograficos.id_genero == id_genero).all()
