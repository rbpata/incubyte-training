students = [
    {"name": "Ram", "score": 85},
    {"name": "Shyam", "score": 72},
    {"name": "Amit", "score": 90},
    {"name": "Neha", "score": 65},
]


def get_average_score():
    total_score = sum(student["score"] for student in students)
    average_score = total_score / len(students)
    return average_score

def highest_score():
    return max(student["score"] for student in students)

def score_above_threshold(threshold):
    return [student for student in students if student["score"] > threshold]

average = get_average_score()
highest_score = highest_score()
above_80 = score_above_threshold(80)

with open("results.txt","w") as file:
    file.write(f"Average Score: {average}\n")
    file.write(f"Highest Score: {highest_score}\n")
    file.write("Students with score above 80:\n")
    for student in above_80:
        file.write(f"{student['name']}: {student['score']}\n")

