# List comprehensions for data transformation
import csv
import json

students = []
with open('student-dataset.csv', 'r') as f:
    for row in csv.DictReader(f):
        students.append(row)

# List comprehensions
names = [s['name'] for s in students]
print(f"Total students: {len(names)}")

# Filter USA students with good English
usa_students = [s['name'] for s in students 
                if s['nationality'] == 'United States of America' 
                and float(s['english.grade']) >= 3.5]
print(f"USA students with English >= 3.5: {len(usa_students)}")

# Dictionary comprehension - name to avg grade
grades = {
    s['name']: round((float(s['english.grade']) + 
                     float(s['math.grade']) + 
                     float(s['sciences.grade'])) / 3, 2)
    for s in students
}
print(f"\nFirst student grade: {list(grades.items())[0]}")

# High achievers only
high_achievers = {name: grade for name, grade in grades.items() if grade >= 3.5}
print(f"High achievers (>= 3.5): {len(high_achievers)}")

# Export to CSV
with open('top-students.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['name', 'avg_grade'])
    writer.writeheader()
    for name, grade in sorted(high_achievers.items(), key=lambda x: x[1], reverse=True)[:10]:
        writer.writerow({'name': name, 'avg_grade': grade})

print("\nTop 10 saved to top-students.csv")
