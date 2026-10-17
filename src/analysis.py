"""Institution-independent demonstration scoring and descriptive analysis."""
import numpy as np
import pandas as pd
from src.data_cleaning import SUBJECT_COLUMNS

WEIGHTS = {'assignment_score': .15, 'quiz_score': .10, 'midterm_score': .20,
           'final_exam_score': .30, 'subject_average': .25}
GRADE_ORDER = ['A', 'B', 'C', 'D', 'E', 'F']
PASS_THRESHOLD = 50
ATTENDANCE_THRESHOLD = 75


def calculate_performance(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Score on unrounded values; rounding is for display only."""
    data = cleaned.copy()
    data['subject_average'] = data[SUBJECT_COLUMNS].mean(axis=1)
    data['academic_score'] = sum(data[column] * weight for column, weight in WEIGHTS.items())
    score = data.academic_score
    data['grade'] = np.select([score >= 90, score >= 80, score >= 70, score >= 60, score >= 50],
                              ['A', 'B', 'C', 'D', 'E'], default='F')
    data['status'] = np.where(score >= PASS_THRESHOLD, 'Pass', 'Fail')
    low_attendance = data.attendance_percentage < ATTENDANCE_THRESHOLD
    low_score = score < PASS_THRESHOLD
    data['at_risk'] = low_attendance | low_score
    data['risk_reason'] = np.select([low_attendance & low_score, low_attendance, low_score],
        ['Low attendance and low score', 'Low attendance', 'Low score'], default='No current flag')
    return data


def summary_metrics(data: pd.DataFrame) -> dict[str, float]:
    """Empty cohorts return zero rather than NaN or division errors."""
    if data.empty:
        return dict(total=0, average_score=0, average_attendance=0, pass_rate=0, highest_score=0)
    return dict(total=len(data), average_score=data.academic_score.mean(),
                average_attendance=data.attendance_percentage.mean(),
                pass_rate=data.status.eq('Pass').mean() * 100, highest_score=data.academic_score.max())


def group_performance(data: pd.DataFrame, column: str) -> pd.DataFrame:
    """Include cohort size to keep group averages in context."""
    return data.groupby(column, observed=True).agg(students=('student_id', 'size'),
        average_score=('academic_score', 'mean'), average_attendance=('attendance_percentage', 'mean')).reset_index()


def correlation(data: pd.DataFrame, column: str) -> float | None:
    """Return None for insufficient or constant-valued observations."""
    pairs = data[[column, 'academic_score']].dropna()
    if len(pairs) < 3 or (pairs.nunique() < 2).any():
        return None
    return float(pairs.corr().iloc[0, 1])


def export_csv(data: pd.DataFrame) -> bytes:
    """Export UTF-8 CSV and neutralize spreadsheet formula prefixes in text."""
    safe = data.copy()
    for column in safe.select_dtypes(include=['object', 'string']).columns:
        safe[column] = safe[column].map(lambda value: "'" + value if isinstance(value, str)
            and value.lstrip().startswith(('=', '+', '-', '@')) else value)
    return safe.to_csv(index=False).encode('utf-8-sig')
