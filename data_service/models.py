from datetime import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    Interval,
    LargeBinary,
    String,
    Table,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Measures(Base):
    __tablename__ = "measures"

    key: Mapped[str] = mapped_column(String(255), primary_key=True, doc="主键")
    fresh_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, doc="刷新时间"
    )
    time: Mapped[datetime] = mapped_column(DateTime, nullable=True, doc="时间")
    service_time: Mapped[datetime] = mapped_column(
        DateTime,
        doc="业务时间",
        default=datetime.now,
        onupdate=datetime.now,
    )
    value: Mapped[float] = mapped_column(Float, nullable=True, doc="值")
    unit: Mapped[str] = mapped_column(String(255), nullable=True, doc="单位")
    name: Mapped[str] = mapped_column(String(255), nullable=True, doc="名称")
    path: Mapped[str] = mapped_column(String(255), nullable=True, doc="路径")
    quality: Mapped[int] = mapped_column(Integer, nullable=True, doc="质量")


def create_measures_monthly_table(table_name: str) -> Table:
    return Table(
        table_name,
        Base.metadata,
        Column("key", String, nullable=False, doc="主键", primary_key=True),
        Column("fresh_time", DateTime, nullable=True, doc="刷新时间"),
        Column("time", DateTime, nullable=False, doc="时间", primary_key=True),
        Column(
            "service_time",
            DateTime,
            nullable=True,
            server_default=func.now(),
            doc="业务时间",
        ),
        Column("value", Float, nullable=True, doc="值"),
    )
