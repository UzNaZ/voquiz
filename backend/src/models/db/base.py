from re import sub

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr

CONVENTION = {
    "ix": "%(table_name)s_%(column_0_N_name)s_idx",
    "uq": "%(table_name)s_%(column_0_N_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_N_name)s_fkey",
    "pk": "%(table_name)s_pkey",
    "seq": "%(table_name)s_%(column_0_N_name)s_seq",
}


class BaseModel(DeclarativeBase):
    """Base class for all models"""

    metadata = MetaData(naming_convention=CONVENTION)

    @classmethod
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower() + "s"
