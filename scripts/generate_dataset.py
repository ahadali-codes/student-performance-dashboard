"""Generate reproducible fictional records; uses only the Python standard library.

Run from the repository root: python scripts/generate_dataset.py
"""
import csv
import random
from pathlib import Path

COLUMNS = ["student_id", "name", "gender", "age", "department", "semester",
           "attendance_percentage", "assignment_score", "quiz_score", "midterm_score",
           "final_exam_score", "mathematics_score", "programming_score", "database_score",
           "english_score", "study_hours_per_week", "extracurricular_activity", "previous_gpa"]
SCORE_COLUMNS = COLUMNS[7:15]


def generate_dataset(destination: Path, seed: int = 42) -> None:
    """Write 240 fictional students plus 4 deliberate duplicate records.

    Numeric relationships are simulated, not evidence about real students.
    Gender is sampled independently of academic ability.
    """
    rng = random.Random(seed)
    rows = []
    departments = ["Computer Science", "Software Engineering", "Information Technology", "Data Science"]
    for number in range(1, 241):
        ability = rng.uniform(30, 94)
        attendance = round(max(20, min(100, 45 + ability * .48 + rng.gauss(0, 13))), 1)
        row = dict(zip(COLUMNS[:7], [f"STU{number:04d}", f"Fictional Student {number:03d}",
            rng.choice(["Female", "Male", "Non-binary"]), rng.randint(18, 27),
            departments[(number - 1) % 4], (number - 1) % 8 + 1, attendance]))
        for column in SCORE_COLUMNS:
            row[column] = round(max(0, min(100, ability + rng.gauss(0, 11))), 1)
        row.update(study_hours_per_week=round(max(0, min(45, ability * .22 + rng.gauss(0, 5))), 1),
                   extracurricular_activity=rng.choice(["Yes", "No"]),
                   previous_gpa=round(max(0, min(4, ability / 25 + rng.gauss(0, .3))), 2))
        rows.append(row)
    # Controlled defects for Stage 2; distinct rows keep the audit counts clear.
    for index, column, value in [(2, "assignment_score", ""), (8, "attendance_percentage", ""),
        (13, "department", ""), (20, "quiz_score", "absent"), (27, "age", "twenty"),
        (34, "final_exam_score", 145), (41, "attendance_percentage", -10),
        (48, "previous_gpa", 4.8), (55, "study_hours_per_week", -3),
        (62, "semester", 0), (69, "programming_score", "85 points")]:
        rows[index][column] = value
    rows.extend(dict(rows[index]) for index in [100, 110, 120, 130])
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    generate_dataset(Path(__file__).resolve().parents[1] / "data/student_performance.csv")
