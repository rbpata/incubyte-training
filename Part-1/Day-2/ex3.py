# Collections Module Practice: namedtuple, defaultdict, Counter
from collections import namedtuple, defaultdict, Counter

# 1. NAMEDTUPLE - structured data
Student = namedtuple('Student', ['name', 'age', 'grade', 'city'])
ram = Student('Ram', 22, 85, 'Mumbai')
print(f"Student: {ram}")
print(f"Name: {ram.name}, Grade: {ram.grade}")

# 2. DEFAULTDICT - automatic default values
students_by_city = defaultdict(list)
students_by_city['Mumbai'].append('Ram')
students_by_city['Delhi'].append('Priya')
print(f"\nStudents by city: {dict(students_by_city)}")

# 3. COUNTER - count elements
grades = [85, 92, 78, 85, 90, 78, 85]
grade_counter = Counter(grades)
print(f"\nGrade frequency: {grade_counter}")
print(f"Most common: {grade_counter.most_common(2)}")

# 4. Combining all three
DetailedStudent = namedtuple('DetailedStudent', ['name', 'city', 'subjects'])
students = [
    DetailedStudent('Ram', 'Mumbai', ['Math', 'Physics']),
    DetailedStudent('Priya', 'Delhi', ['Math', 'Chemistry']),
    DetailedStudent('Amit', 'Mumbai', ['Physics', 'CS'])
]

# Group by city using defaultdict
city_groups = defaultdict(list)
for s in students:
    city_groups[s.city].append(s.name)
print(f"\nGrouped by city: {dict(city_groups)}")

# Count subjects using Counter
all_subjects = [subj for s in students for subj in s.subjects]
print(f"Subject popularity: {Counter(all_subjects)}")
print("\nCollections exercise completed!")
