from typing import Optional
import datetime
import decimal

from sqlalchemy import DECIMAL, ForeignKeyConstraint, Index, Integer, String, TIMESTAMP, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class GenerosMusicales(Base):
    __tablename__ = 'generos_musicales'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre_prediccion: Mapped[Optional[str]] = mapped_column(String(255))
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    imagen: Mapped[Optional[str]] = mapped_column(String(500))
    video_link: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    caracteristicas_culturales: Mapped[list['CaracteristicasCulturales']] = relationship('CaracteristicasCulturales', back_populates='generos_musicales')
    instrumentos: Mapped[list['Instrumentos']] = relationship('Instrumentos', back_populates='generos_musicales')
    origenes_geograficos: Mapped[list['OrigenesGeograficos']] = relationship('OrigenesGeograficos', back_populates='generos_musicales')


class CaracteristicasCulturales(Base):
    __tablename__ = 'caracteristicas_culturales'
    __table_args__ = (
        ForeignKeyConstraint(['id_genero'], ['generos_musicales.id'], ondelete='SET NULL', onupdate='CASCADE', name='fk_cultural_genero'),
        Index('fk_cultural_genero', 'id_genero')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    id_genero: Mapped[Optional[int]] = mapped_column(Integer)
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    imagen: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    generos_musicales: Mapped[Optional['GenerosMusicales']] = relationship('GenerosMusicales', back_populates='caracteristicas_culturales')


class Instrumentos(Base):
    __tablename__ = 'instrumentos'
    __table_args__ = (
        ForeignKeyConstraint(['id_genero'], ['generos_musicales.id'], ondelete='SET NULL', onupdate='CASCADE', name='fk_instrumento_genero'),
        Index('fk_instrumento_genero', 'id_genero')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[Optional[str]] = mapped_column(String(100))
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    imagen: Mapped[Optional[str]] = mapped_column(String(500))
    id_genero: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    generos_musicales: Mapped[Optional['GenerosMusicales']] = relationship('GenerosMusicales', back_populates='instrumentos')


class OrigenesGeograficos(Base):
    __tablename__ = 'origenes_geograficos'
    __table_args__ = (
        ForeignKeyConstraint(['id_genero'], ['generos_musicales.id'], ondelete='SET NULL', onupdate='CASCADE', name='fk_origen_genero'),
        Index('fk_origen_genero', 'id_genero')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    latitud: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(10, 7))
    longitud: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(10, 7))
    imagen: Mapped[Optional[str]] = mapped_column(String(500))
    id_genero: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    generos_musicales: Mapped[Optional['GenerosMusicales']] = relationship('GenerosMusicales', back_populates='origenes_geograficos')
