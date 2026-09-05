from sqlalchemy.orm import Session

from db import SessionLocal

from database.models import Department, Employee
from schemas import EmployeeCreate
from sqlalchemy import func, select


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

def get_total_bonus(db: Session):
    statement = select(
        func.coalesce(func.sum(Employee.bonus), 0)
    )

    return db.execute(statement).scalar_one() 


def get_employees_without_bonus(db: Session) -> list[Employee]:
    statement = (
        select(Employee)
        .where(Employee.bonus.is_(None))
        .order_by(Employee.employee_id)
    )

    return list(db.execute(statement).scalars().all())


def get_bonus_percentages(db: Session):
    statement = (
        select(
            Employee,
            func.round(
                (Employee.bonus / Employee.salary) * 100,
                2
            ).label("bonus_percentage")
        )
        .where(Employee.bonus.is_not(None))
        .order_by(Employee.employee_id)
    )

    return db.execute(statement).all()


def get_departments_bonus_above_average_salary(db: Session):
    statement = (
        select(
            Department.department_id,
            Department.department_name,
            func.coalesce(func.sum(Employee.bonus), 0).label("total_bonus"),
            func.avg(Employee.salary).label("average_salary"),
        )
        .join(
            Employee,
            Employee.department_id == Department.department_id,
        )
        .group_by(
            Department.department_id,
            Department.department_name,
        )
        .having(
            func.coalesce(func.sum(Employee.bonus), 0)
            > func.avg(Employee.salary)
        )
        .order_by(Department.department_id)
    )

    return db.execute(statement).all()


def get_employees_ranked_by_bonus(db: Session) -> list[Employee]:
    statement = (
        select(Employee)
        .order_by(
            Employee.bonus.desc().nulls_last(),
            Employee.employee_id,
        )
    )

    return list(db.execute(statement).scalars().all())


def get_salary_and_compensation_leaders(db: Session):
    highest_salary_statement = (
        select(Employee)
        .order_by(Employee.salary.desc(), Employee.employee_id)
        .limit(1)
    )

    highest_salary_employee = (
        db.execute(highest_salary_statement)
        .scalar_one_or_none()
    )

    highest_compensation_statement = (
        select(Employee)
        .order_by(
            (Employee.salary + func.coalesce(Employee.bonus, 0)).desc(),
            Employee.employee_id,
        )
        .limit(1)
    )

    highest_compensation_employee = (
        db.execute(highest_compensation_statement)
        .scalar_one_or_none()
    )

    return highest_salary_employee, highest_compensation_employee