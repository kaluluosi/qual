from qual.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class Device(Base):
    """
    Device model.
    """

    __tablename__ = "devices"

    # 资产编号
    res_id: Mapped[str] = mapped_column(primary_key=True, unique=True, index=True)
    name: Mapped[str] = mapped_column(index=True)
