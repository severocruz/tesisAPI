import inspect
import os
from sqlalchemy import ForeignKey
from models import Base
import sys

output_dir = "crud"
os.makedirs(output_dir, exist_ok=True)

for name, cls in inspect.getmembers(sys.modules['models']):
    if inspect.isclass(cls) and issubclass(cls, Base) and cls != Base:
        model_name = name
        model_file = f"from models import {model_name}"
        schema_file = f"from schemas.{model_name.lower()} import {model_name}Create, {model_name}Out"
        
        lines = [
            "from sqlalchemy.orm import Session",
            model_file,
            schema_file,
            "\n"
        ]

        # get_all
        lines.append(f"def get_all(db: Session) -> list[{model_name}Out]:")
        lines.append(f"    return db.query({model_name}).all()\n")

        # get_by_id
        lines.append(f"def get_by_id(db: Session, id: int) -> {model_name}Out | None:")
        lines.append(f"    return db.query({model_name}).filter({model_name}.id == id).first()\n")

        # create
        lines.append(f"def create(db: Session, item: {model_name}Create) -> {model_name}Out:")
        lines.append(f"    db_item = {model_name}(**item.dict())")
        lines.append("    db.add(db_item)")
        lines.append("    db.commit()")
        lines.append("    db.refresh(db_item)")
        lines.append("    return db_item\n")

        # Métodos para claves foráneas
        for col in cls.__table__.columns:
            if col.foreign_keys:
                fk_name = col.name
                lines.append(f"def get_by_{fk_name}(db: Session, {fk_name}: int) -> list[{model_name}Out]:")
                lines.append(f"    return db.query({model_name}).filter({model_name}.{fk_name} == {fk_name}).all()\n")

        # Guardar archivo
        filename = os.path.join(output_dir, f"{model_name.lower()}.py")
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

print(f"CRUDs básicos con métodos por clave foránea generados en '{output_dir}/'")
