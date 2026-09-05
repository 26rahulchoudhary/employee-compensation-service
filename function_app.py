import azure.functions as func
import json
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from db import SessionLocal
from employee_service import (
    create_employee,
    get_employee,
    get_employees,
    update_employee,
    delete_employee,
    get_total_bonus,
    get_employees_without_bonus,
    get_bonus_percentages,
    get_departments_bonus_above_average_salary,
    get_employees_ranked_by_bonus,
    get_salary_and_compensation_leaders,
)
from schemas import EmployeeCreate, EmployeeResponse


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="health", methods=["GET"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({
            "status": "healthy",
            "service": "Employee Compensation Service"
        }),
        mimetype="application/json",
        status_code=200
    )

@app.route(route="employees", methods=["POST"])
def create_employee_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    db = SessionLocal()

    try:
        body = req.get_json()
        employee_data = EmployeeCreate.model_validate(body)

        employee = create_employee(db, employee_data)

        response = EmployeeResponse.model_validate(employee)

        return func.HttpResponse(
            response.model_dump_json(),
            mimetype="application/json",
            status_code=201,
        )

    except ValidationError as exc:
        return func.HttpResponse(
            json.dumps({
                "error": "Validation failed",
                "details": exc.errors(),
            }),
            mimetype="application/json",
            status_code=422,
        )

    except ValueError:
        return func.HttpResponse(
            json.dumps({
                "error": "Invalid JSON request body",
            }),
            mimetype="application/json",
            status_code=400,
        )
    except SQLAlchemyError:
        return func.HttpResponse(
            json.dumps({
                "error": "Database operation failed"
            }),
            mimetype="application/json",
            status_code=500,
        )
    finally:
        db.close()


@app.route(route="employees/{employee_id}", methods=["GET"])
def get_employee_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    employee_id = req.route_params.get("employee_id")

    try:
        employee_id = int(employee_id)
    except (TypeError, ValueError):
        return func.HttpResponse(
            json.dumps({
                "error": "Employee ID must be an integer"
            }),
            mimetype="application/json",
            status_code=400,
        )

    db = SessionLocal()

    try:
        employee = get_employee(db, employee_id)

        if employee is None:
            return func.HttpResponse(
                json.dumps({
                    "error": "Employee not found"
                }),
                mimetype="application/json",
                status_code=404,
            )

        response = EmployeeResponse.model_validate(employee)

        return func.HttpResponse(
            response.model_dump_json(),
            mimetype="application/json",
            status_code=200,
        )
    except SQLAlchemyError:
        return func.HttpResponse(
            json.dumps({
                "error": "Database operation failed"
            }),
            mimetype="application/json",
            status_code=500,
        )
    finally:
        db.close()


@app.route(route="employees", methods=["GET"])
def list_employees_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    department_id = req.params.get("department_id")

    if department_id is not None:
        try:
            department_id = int(department_id)
        except ValueError:
            return func.HttpResponse(
                json.dumps({
                    "error": "department_id must be an integer"
                }),
                mimetype="application/json",
                status_code=400,
            )

    db = SessionLocal()

    try:
        employees = get_employees(db, department_id)

        response = [
            EmployeeResponse.model_validate(employee).model_dump(mode="json")
            for employee in employees
        ]

        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200,
        )
    except SQLAlchemyError:
        return func.HttpResponse(
            json.dumps({
                "error": "Database operation failed"
            }),
            mimetype="application/json",
            status_code=500,
        )
    finally:
        db.close()

@app.route(route="employees/{employee_id}", methods=["PUT"])
def update_employee_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    employee_id = req.route_params.get("employee_id")

    try:
        employee_id = int(employee_id)
    except (TypeError, ValueError):
        return func.HttpResponse(
            json.dumps({
                "error": "Employee ID must be an integer"
            }),
            mimetype="application/json",
            status_code=400,
        )

    try:
        body = req.get_json()
        employee_data = EmployeeCreate.model_validate(body)
    except ValidationError as exc:
        return func.HttpResponse(
            json.dumps({
                "error": "Validation failed",
                "details": exc.errors(),
            }),
            mimetype="application/json",
            status_code=422,
        )
    except ValueError:
        return func.HttpResponse(
            json.dumps({
                "error": "Invalid JSON request body"
            }),
            mimetype="application/json",
            status_code=400,
        )

    db = SessionLocal()

    try:
        employee = update_employee(db, employee_id, employee_data)

        if employee is None:
            return func.HttpResponse(
                json.dumps({
                    "error": "Employee not found"
                }),
                mimetype="application/json",
                status_code=404,
            )

        response = EmployeeResponse.model_validate(employee)

        return func.HttpResponse(
            response.model_dump_json(),
            mimetype="application/json",
            status_code=200,
        )
    except SQLAlchemyError:
        return func.HttpResponse(
            json.dumps({
                "error": "Database operation failed"
            }),
            mimetype="application/json",
            status_code=500,
        )
    finally:
        db.close()


@app.route(route="employees/{employee_id}", methods=["DELETE"])
def delete_employee_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    employee_id = req.route_params.get("employee_id")

    try:
        employee_id = int(employee_id)
    except (TypeError, ValueError):
        return func.HttpResponse(
            json.dumps({
                "error": "Employee ID must be an integer"
            }),
            mimetype="application/json",
            status_code=400,
        )

    db = SessionLocal()

    try:
        deleted = delete_employee(db, employee_id)

        if not deleted:
            return func.HttpResponse(
                json.dumps({
                    "error": "Employee not found"
                }),
                mimetype="application/json",
                status_code=404,
            )

        return func.HttpResponse(
            status_code=204,
        )
    except SQLAlchemyError:
        return func.HttpResponse(
            json.dumps({
                "error": "Database operation failed"
            }),
            mimetype="application/json",
            status_code=500,
        )
    finally:
        db.close()


@app.route(route="reports/total-bonus", methods=["GET"])
def total_bonus_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    db = SessionLocal()

    try:
        total_bonus = get_total_bonus(db)

        return func.HttpResponse(
            json.dumps({
                "total_bonus": float(total_bonus)
            }),
            mimetype="application/json",
            status_code=200,
        )
    except SQLAlchemyError:
        return func.HttpResponse(
            json.dumps({
                "error": "Database operation failed"
            }),
            mimetype="application/json",
            status_code=500,
        )
    finally:
        db.close()


@app.route(route="reports/employees-without-bonus", methods=["GET"])
def employees_without_bonus_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    db = SessionLocal()

    try:
        employees = get_employees_without_bonus(db)

        response = [
            EmployeeResponse.model_validate(employee).model_dump(mode="json")
            for employee in employees
        ]

        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200,
        )
    except SQLAlchemyError:
        return func.HttpResponse(
            json.dumps({
                "error": "Database operation failed"
            }),
            mimetype="application/json",
            status_code=500,
        )
    finally:
        db.close()


@app.route(route="reports/bonus-percentages", methods=["GET"])
def bonus_percentages_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    db = SessionLocal()

    try:
        results = get_bonus_percentages(db)

        response = [
            {
                "employee_id": employee.employee_id,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "salary": float(employee.salary),
                "bonus": float(employee.bonus),
                "bonus_percentage": float(bonus_percentage),
            }
            for employee, bonus_percentage in results
        ]

        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200,
        )
    except SQLAlchemyError:
        return func.HttpResponse(
            json.dumps({
                "error": "Database operation failed"
            }),
            mimetype="application/json",
            status_code=500,
        )
    finally:
        db.close()


@app.route(
    route="reports/departments-bonus-above-average",
    methods=["GET"],
)
def departments_bonus_above_average_endpoint(
    req: func.HttpRequest,
) -> func.HttpResponse:
    db = SessionLocal()

    try:
        results = get_departments_bonus_above_average_salary(db)

        response = [
            {
                "department_id": department_id,
                "department_name": department_name,
                "total_bonus": float(total_bonus),
                "average_salary": float(average_salary),
            }
            for (
                department_id,
                department_name,
                total_bonus,
                average_salary,
            ) in results
        ]

        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200,
        )
    except SQLAlchemyError:
        return func.HttpResponse(
            json.dumps({
                "error": "Database operation failed"
            }),
            mimetype="application/json",
            status_code=500,
        )
    finally:
        db.close()


@app.route(route="reports/employees-ranked-by-bonus", methods=["GET"])
def employees_ranked_by_bonus_endpoint(
    req: func.HttpRequest,
) -> func.HttpResponse:
    db = SessionLocal()

    try:
        employees = get_employees_ranked_by_bonus(db)

        response = [
            EmployeeResponse.model_validate(employee).model_dump(mode="json")
            for employee in employees
        ]

        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200,
        )
    except SQLAlchemyError:
        return func.HttpResponse(
            json.dumps({
                "error": "Database operation failed"
            }),
            mimetype="application/json",
            status_code=500,
        )
    finally:
        db.close()


@app.route(
    route="reports/salary-and-compensation-leaders",
    methods=["GET"],
)
def salary_and_compensation_leaders_endpoint(
    req: func.HttpRequest,
) -> func.HttpResponse:
    db = SessionLocal()

    try:
        highest_salary_employee, highest_compensation_employee = (
            get_salary_and_compensation_leaders(db)
        )

        if highest_salary_employee is None:
            return func.HttpResponse(
                json.dumps({
                    "error": "No employees found"
                }),
                mimetype="application/json",
                status_code=404,
            )

        response = {
            "highest_base_salary": EmployeeResponse.model_validate(
                highest_salary_employee
            ).model_dump(mode="json"),
            "highest_total_compensation": EmployeeResponse.model_validate(
                highest_compensation_employee
            ).model_dump(mode="json"),
            "same_employee": (
                highest_salary_employee.employee_id
                == highest_compensation_employee.employee_id
            ),
        }

        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200,
        )
    except SQLAlchemyError:
        return func.HttpResponse(
            json.dumps({
                "error": "Database operation failed"
            }),
            mimetype="application/json",
            status_code=500,
        )
    finally:
        db.close()