import azure.functions as func
import json
from pydantic import ValidationError

from db import SessionLocal
from employee_service import (
    create_employee,
    get_employee,
    get_employees,
    update_employee,
    delete_employee
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

    finally:
        db.close()