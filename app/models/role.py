from sqlalchemy import Column, Integer, String
from app.db.base import Base

class Role(Base):
    """
    Modelo que representa un rol del sistema.
    """

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)