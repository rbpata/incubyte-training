import csv
import os

SAMPLE_DATA = [
    {"name": "Ram", "department": "Engineering", "salary": "95000", "years": "5"},
    {"name": "Sahil", "department": "Marketing", "salary": "72000", "years": "3"},
    {"name": "Mihir", "department": "Engineering", "salary": "110000", "years": "8"},
    {"name": "Dhruv", "department": "HR", "salary": "65000", "years": "2"},
    {"name": "Arjun", "department": "Engineering", "salary": "125000", "years": "10"},
    {"name": "Karan", "department": "Marketing", "salary": "80000", "years": "6"},
    {"name": "Neha", "department": "HR", "salary": "70000", "years": "4"},
    {"name": "Vivek", "department": "Engineering", "salary": "88000", "years": "3"},
    {"name": "Priya", "department": "Marketing", "salary": "91000", "years": "7"},
    {"name": "Rohan", "department": "Engineering", "salary": "105000", "years": "6"},
]

DATA_FILE = os.path.join(os.path.dirname(__file__), "employees.csv")


def create_sample_csv():
    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "department", "salary", "years"])
        writer.writeheader()
        writer.writerows(SAMPLE_DATA)


def read_employees(filepath: str):
    with open(filepath) as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def filter_department(employees, dept: str):
    for emp in employees:
        if emp["department"] == dept:
            yield emp


def parse_salary(employees):
    for emp in employees:
        yield {**emp, "salary": int(emp["salary"]), "years": int(emp["years"])}


def high_earners(employees, min_salary: int):
    for emp in employees:
        if emp["salary"] >= min_salary:
            yield emp


def format_report(employees):
    for emp in employees:
        yield f"{emp['name']:>10} | {emp['department']:<12} | ${emp['salary']:>8,} | {emp['years']} yrs"


def group_by_department(employees):
    groups: dict[str, list[int]] = {}
    for emp in employees:
        dept = emp["department"]
        salary = int(emp["salary"])
        if dept not in groups:
            groups[dept] = []
        groups[dept].append(salary)
    for dept, salaries in groups.items():
        yield dept, sum(salaries) / len(salaries)


create_sample_csv()

print("=== Engineering High Earners (>= $100k) ===")
pipeline = format_report(
    high_earners(
        parse_salary(filter_department(read_employees(DATA_FILE), "Engineering")),
        100_000,
    )
)
for line in pipeline:
    print(line)

print("\n=== Average Salary by Department ===")
for dept, avg in group_by_department(read_employees(DATA_FILE)):
    print(f"  {dept:<15} ${avg:>10,.2f}")

print("\n=== Senior Engineers (5+ years) ===")
rows = read_employees(DATA_FILE)
engineers = (r for r in rows if r["department"] == "Engineering")
seniors = (r for r in engineers if int(r["years"]) >= 5)
names = (r["name"] for r in seniors)
for name in names:
    print(f"  {name}")

os.remove(DATA_FILE)
