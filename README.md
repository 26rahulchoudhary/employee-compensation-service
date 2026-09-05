# Employee Compensation Service

Backend service for managing employees and generating employee compensation reports.

### Tech Stack

* Python
* Azure Functions
* PostgreSQL
* SQLAlchemy
* Pydantic
* Docker

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/26rahulchoudhary/employee-compensation-service.git
cd employee-compensation-service
```

### 2. Create and activate virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Start PostgreSQL

PostgreSQL is run locally using Docker:

```powershell
docker run --name employee-postgres `
  -e POSTGRES_USER=employee_admin `
  -e POSTGRES_PASSWORD=<your-password> `
  -e POSTGRES_DB=employee_compensation `
  -p 5433:5432 `
  -d postgres:16
```

If the container already exists:

```powershell
docker start employee-postgres
```

### 5. Create database tables

```powershell
Get-Content database/schema.sql | docker exec -i employee-postgres psql -U employee_admin -d employee_compensation
```

### 6. Seed sample data

```powershell
Get-Content database/seed.sql | docker exec -i employee-postgres psql -U employee_admin -d employee_compensation
```

### 7. Configure database connection

Set `DATABASE_URL` in `local.settings.json`:

```json
{
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "DATABASE_URL": "postgresql+psycopg2://employee_admin:<your-password>@127.0.0.1:5433/employee_compensation"
  }
}
```

`local.settings.json` is excluded from Git.

### 8. Start the Azure Function

```powershell
func start
```

The API will be available at:

```text
http://localhost:7071/api
```

## API Endpoints

### Employee APIs

| Method | Endpoint                            | Description          |
| ------ | ----------------------------------- | -------------------- |
| POST   | `/api/employees`                    | Create employee      |
| GET    | `/api/employees/{id}`               | Get employee         |
| GET    | `/api/employees`                    | List employees       |
| GET    | `/api/employees?department_id={id}` | Filter by department |
| PUT    | `/api/employees/{id}`               | Update employee      |
| DELETE | `/api/employees/{id}`               | Delete employee      |

### Reporting APIs

| Method | Endpoint                                       | Description                      |
| ------ | ---------------------------------------------- | -------------------------------- |
| GET    | `/api/reports/total-bonus`                     | Total company bonus              |
| GET    | `/api/reports/employees-without-bonus`         | Employees without bonus          |
| GET    | `/api/reports/bonus-percentages`               | Bonus as % of salary             |
| GET    | `/api/reports/departments-bonus-above-average` | Departments above average salary |
| GET    | `/api/reports/employees-ranked-by-bonus`       | Employees ranked by bonus        |
| GET    | `/api/reports/salary-and-compensation-leaders` | Salary and compensation leaders  |

## Database

The database contains two tables:

* `Department`
* `Employee`

SQL scripts are provided in the `database/` directory:

```text
database/
├── schema.sql
└── seed.sql
```

## Error Handling

The API includes:

* Request validation using Pydantic
* `400` for invalid requests
* `404` when an employee is not found
* `422` for validation errors
* `500` for database errors
* Transaction rollback for failed database writes

Database credentials are supplied through environment configuration and are not hardcoded in the application.

## Azure Deployment

The application is designed to be deployed as an **Azure Function App**. For deployment, `DATABASE_URL` should be configured as an Azure application setting and point to a cloud-accessible PostgreSQL database.
