from sqlalchemy.orm import Session

from db import SessionLocal

from database.models import Employee
from schemas import EmployeeCreate
from sqlalchemy import select


def get_db() -> Session:
    return SessionLocal()


def create_employee(db: Session, employee_data: EmployeeCreate) -> Employee:
    employee = Employee(
        first_name=employee_data.first_name,
        last_name=employee_data.last_name,
        department_id=employee_data.department_id,
        salary=employee_data.salary,
        bonus=employee_data.bonus,
        hire_date=employee_data.hire_date,
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


def get_employee(db: Session, employee_id: int) -> Employee | None:
    statement = select(Employee).where(Employee.employee_id == employee_id)

    return db.execute(statement).scalar_one_or_none()


def get_employees(
    db: Session,
    department_id: int | None = None,
) -> list[Employee]:
    statement = select(Employee)

    if department_id is not None:
        statement = statement.where(
            Employee.department_id == department_id
        )

    statement = statement.order_by(Employee.employee_id)

    return list(db.execute(statement).scalars().all())

def update_employee(
    db: Session,
    employee_id: int,
    employee_data: EmployeeCreate,
) -> Employee | None:
    employee = get_employee(db, employee_id)

    if employee is None:
        return None

    employee.first_name = employee_data.first_name
    employee.last_name = employee_data.last_name
    employee.department_id = employee_data.department_id
    employee.salary = employee_data.salary
    employee.bonus = employee_data.bonus
    employee.hire_date = employee_data.hire_date

    db.commit()
    db.refresh(employee)

    return employee

def delete_employee(
    db: Session,
    employee_id: int,
) -> bool:
    employee = get_employee(db, employee_id)

    if employee is None:
        return False

    db.delete(employee)
    db.commit()

    return True