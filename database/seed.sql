INSERT INTO Department (DepartmentName, Location)
VALUES
    ('Engineering', 'Mumbai'),
    ('Human Resources', 'Pune'),
    ('Finance', 'Mumbai'),
    ('Marketing', 'Bangalore');


INSERT INTO Employee
    (FirstName, LastName, DepartmentID, Salary, Bonus, HireDate)
VALUES
    ('Rahul', 'Sharma', 1, 85000.00, 10000.00, '2022-06-15'),
    ('Priya', 'Patel', 1, 95000.00, 15000.00, '2021-03-10'),
    ('Amit', 'Verma', 2, 65000.00, NULL, '2023-01-20'),
    ('Sneha', 'Joshi', 3, 78000.00, 5000.00, '2020-11-05'),
    ('Arjun', 'Mehta', 4, 72000.00, NULL, '2024-02-12');