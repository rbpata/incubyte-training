# Data Aggregation with CSV and Collections
import csv
import json
from collections import defaultdict, Counter

# Read CSV
students = []
with open('student-dataset.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        students.append(row)

print(f"Loaded {len(students)} students")

# Nationality count
nationalities = Counter([s['nationality'] for s in students])
print(f"\nTop 3 countries: {nationalities.most_common(3)}")

# Group by city
by_city = defaultdict(list)
for s in students:
    by_city[s['city']].append(s['name'])

cities_2plus = [(city, len(names)) for city, names in by_city.items() if len(names) >= 2]
print(f"\nCities with multiple students: {cities_2plus[:3]}")

# Average grades
avg_math = sum(float(s['math.grade']) for s in students) / len(students)
avg_english = sum(float(s['english.grade']) for s in students) / len(students)
print(f"\nAvg Math: {avg_math:.2f}, Avg English: {avg_english:.2f}")

# Export summary
summary = {
    'total': len(students),
    'countries': len(nationalities),
    'avg_math': round(avg_math, 2),
    'avg_english': round(avg_english, 2)
}

with open('data-summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("\nSummary saved to data-summary.json")
