from sqlalchemy.orm import Session
from models import GenerosMusicales
from schemas.generosmusicales import GenerosMusicalesCreate, GenerosMusicalesOut


def get_all(db: Session) -> list[GenerosMusicalesOut]:
    return db.query(GenerosMusicales).all()

def get_by_id(db: Session, id: int) -> GenerosMusicalesOut | None:
    return db.query(GenerosMusicales).filter(GenerosMusicales.id == id).first()

def get_by_nombre_prediccion(db: Session, nombre_prediccion: str) -> GenerosMusicalesOut | None:
    return db.query(GenerosMusicales).filter(GenerosMusicales.nombre_prediccion == nombre_prediccion).first()


def create(db: Session, item: GenerosMusicalesCreate) -> GenerosMusicalesOut:
    db_item = GenerosMusicales(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
