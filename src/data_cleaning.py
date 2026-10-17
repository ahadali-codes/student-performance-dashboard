"""CSV validation and transparent, deterministic cleaning."""
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO
import numpy as np
import pandas as pd

SCORE_COLUMNS = ['assignment_score', 'quiz_score', 'midterm_score', 'final_exam_score',
                 'mathematics_score', 'programming_score', 'database_score', 'english_score']
SUBJECT_COLUMNS = SCORE_COLUMNS[4:]
REQUIRED_COLUMNS = ['student_id', 'name', 'gender', 'age', 'department', 'semester',
                    'attendance_percentage', *SCORE_COLUMNS, 'study_hours_per_week',
                    'extracurricular_activity', 'previous_gpa']
RANGES = {'age': (16, 100), 'semester': (1, 8), 'attendance_percentage': (0, 100),
          **{column: (0, 100) for column in SCORE_COLUMNS},
          'study_hours_per_week': (0, 168), 'previous_gpa': (0, 4)}
FALLBACKS = {'age': 20, 'semester': 1, 'attendance_percentage': 75,
             **{column: 50 for column in SCORE_COLUMNS},
             'study_hours_per_week': 10, 'previous_gpa': 2}

@dataclass
class CleaningReport:
    """Counts reflect each sequential cleaning operation, not unique cells."""
    input_rows: int
    output_rows: int
    duplicate_rows_removed: int
    conflicting_ids_removed: int
    missing_ids_removed: int
    invalid_numeric_values: dict[str, int]
    imputed_numeric_values: dict[str, int]
    normalized_numeric_values: dict[str, int]
    unknown_categories: dict[str, int]


def load_csv(source: str | Path | BinaryIO) -> pd.DataFrame:
    """Read UTF-8 CSV without silently skipping malformed records."""
    try:
        # String IDs preserve leading zeroes and identifiers such as 'NA'.
        data = pd.read_csv(source, dtype=str, keep_default_na=False, encoding='utf-8-sig')
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError, OSError, ValueError) as exc:
        raise ValueError('Could not read CSV. Use a nonempty UTF-8, comma-separated file with a header.') from exc
    if data.empty:
        raise ValueError('The CSV contains no student records.')
    return data


def clean_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    """Return cleaned records and audit counts without changing the caller's frame.

    Numeric blanks/invalid values use the valid column median (documented fallback
    if entirely invalid). Integer fields use rounded medians. Duplicate IDs keep
    their first record. Numeric imputations remain flagged for interpretation.
    """
    data = raw.copy()
    data.columns = [str(column).strip().lower().replace(' ', '_') for column in data.columns]
    if data.columns.duplicated().any():
        raise ValueError('Column names must be unique after normalizing spaces and case.')
    missing = sorted(set(REQUIRED_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError('Missing required columns: ' + ', '.join(missing))
    if data.empty:
        raise ValueError('The dataset contains no records.')
    data = data[REQUIRED_COLUMNS].copy()
    input_rows = len(data)
    for column in data.select_dtypes(include=['object', 'string']).columns:
        data[column] = data[column].astype('string').str.strip().replace('', pd.NA)
    duplicate_count = int(data.duplicated().sum())
    data = data.drop_duplicates()
    missing_ids = int(data.student_id.isna().sum())
    data = data.dropna(subset=['student_id'])
    conflicts = int(data.student_id.duplicated().sum())
    data = data.drop_duplicates('student_id', keep='first').reset_index(drop=True)
    if data.empty:
        raise ValueError('No usable records remain: student IDs are missing.')
    invalid, imputed, normalized = {}, {}, {}
    flags = pd.DataFrame(index=data.index)
    for column, (lower, upper) in RANGES.items():
        original = data[column]
        numeric = pd.to_numeric(original, errors='coerce')
        # Accept explicit score units only, rather than extracting arbitrary digits.
        if column in SCORE_COLUMNS:
            extracted = original.astype('string').str.extract(r'^([+-]?\d+(?:\.\d+)?)\s+points?$', expand=False)
            parsed_units = pd.to_numeric(extracted, errors='coerce')
            unit_mask = numeric.isna() & parsed_units.notna()
            numeric = numeric.where(~unit_mask, parsed_units)
            normalized[column] = int(unit_mask.sum())
        else:
            normalized[column] = 0
        valid = numeric.between(lower, upper) & np.isfinite(numeric)
        if column in ['age', 'semester']:
            valid &= numeric.mod(1).eq(0)
        invalid[column] = int((original.notna() & ~valid).sum())
        numeric = numeric.where(valid)
        flags[column] = numeric.isna()
        imputed[column] = int(numeric.isna().sum())
        median = numeric.median() if numeric.notna().any() else FALLBACKS[column]
        if column in ['age', 'semester']:
            median = round(float(median))
        data[column] = numeric.fillna(median)
        if column in ['age', 'semester']:
            data[column] = data[column].astype(int)
    unknown = {}
    for column, allowed in [('gender', ['Female', 'Male', 'Non-binary']),
                            ('extracurricular_activity', ['Yes', 'No'])]:
        mapping = {value.casefold(): value for value in allowed}
        values = data[column].astype('string').str.casefold().map(mapping)
        unknown[column] = int(values.isna().sum())
        data[column] = values.fillna('Unknown')
    for column in ['name', 'department']:
        unknown[column] = int(data[column].isna().sum())
        data[column] = data[column].fillna('Unknown')
    data['imputed_numeric_count'] = flags.sum(axis=1).astype(int)
    data['score_imputed'] = flags[SCORE_COLUMNS].any(axis=1)
    data['attendance_imputed'] = flags['attendance_percentage']
    report = CleaningReport(input_rows, len(data), duplicate_count, conflicts, missing_ids,
                            invalid, imputed, normalized, unknown)
    return data, report
