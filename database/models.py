from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric
from sqlalchemy.orm import relationship



class Base(DeclarativeBase):
    pass


class Department(Base):
    __tablename__ = "department"

    department_id: Mapped[int] = mapped_column(
        "departmentid",
        Integer,
        primary_key=True,
    )

    department_name: Mapped[str] = mapped_column(
        "departmentname",
        String(100),
        nullable=False,
    )

    location: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )


class Employee(Base):
        __tablename__ = "employee"

        employee_id: Mapped[int] = mapped_column(
            "employeeid",
            Integer,
            primary_key=True,
        )

        first_name: Mapped[str] = mapped_column(
            "firstname",
            String(50),
            nullable=False,
        )

        last_name: Mapped[str] = mapped_column(
            "lastname",
            String(50),
            nullable=False,
        )

        department_id: Mapped[int] = mapped_column(
            "departmentid",
            ForeignKey("department.departmentid"),
            nullable=False,
        )

        salary: Mapped[Decimal] = mapped_column(
            Numeric(12, 2),
            nullable=False,
        )

        bonus: Mapped[Decimal | None] = mapped_column(
            Numeric(12, 2),
            nullable=True,
        )

        hire_date: Mapped[date | None] = mapped_column(
            "hiredate",
            Date,
            nullable=True,
        )

        department: Mapped["Department"] = relationship()