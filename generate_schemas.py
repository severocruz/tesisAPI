import inspect
import os
from sqlalchemy import Integer, String, Boolean, Float, DateTime, Date
from models import Base
import sys

# Carpeta donde se guardarán los schemas
output_dir = "schemas"
os.makedirs(output_dir, exist_ok=True)

# Mapeo de tipos SQLAlchemy a tipos Pydantic/Python
type_map = {
    Integer: "int",
    String: "str",
    Boolean: "bool",
    Float: "float",
    DateTime: "str",  # o datetime.datetime si quieres importar
    Date: "str",      # o datetime.date
}

# Función para obtener tipo Pydantic
def get_type(column):
    for sa_type, py_type in type_map.items():
        if isinstance(column.type, sa_type):
            return py_type
    return "str"  # default

# Iterar sobre todas las clases de modelos
for name, cls in inspect.getmembers(sys.modules['models']):
    if inspect.isclass(cls) and issubclass(cls, Base) and cls != Base:
        cols = [c for c in cls.__table__.columns]
        col_names = [c for c in cols if c.name != "id"]

        lines = ["from pydantic import BaseModel\n"]

        # XBase
        lines.append(f"class {name}Base(BaseModel):")
        if col_names:
            for col in col_names:
                col_type = get_type(col)
                lines.append(f"    {col.name}: {col_type}")
        else:
            lines.append("    pass")
        lines.append("")

        # XCreate
        lines.append(f"class {name}Create({name}Base):")
        lines.append("    pass\n")

        # XOut
        lines.append(f"class {name}Out({name}Base):")
        lines.append("    id: int")
        lines.append("    class Config:")
        lines.append("        orm_mode = True\n")

        # Guardar cada schema en un archivo separado
        filename = os.path.join(output_dir, f"{name.lower()}.py")
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

print(f"Schemas generados correctamente en la carpeta '{output_dir}/'")
