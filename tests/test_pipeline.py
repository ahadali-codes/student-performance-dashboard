"""Meaningful regression checks for data integrity and score boundaries."""
import io
import unittest
from pathlib import Path
import pandas as pd
from src.data_cleaning import load_csv, clean_data, SCORE_COLUMNS, RANGES
from src.analysis import calculate_performance, summary_metrics, export_csv

ROOT = Path(__file__).resolve().parents[1]

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.raw = load_csv(ROOT / 'data/student_performance.csv')

    def test_defect_audit_and_ranges(self):
        before = self.raw.copy(deep=True)
        cleaned, report = clean_data(self.raw)
        self.assertEqual((report.input_rows, report.output_rows, report.duplicate_rows_removed), (244, 240, 4))
        self.assertEqual(sum(report.imputed_numeric_values.values()), 9)
        self.assertEqual(sum(report.normalized_numeric_values.values()), 1)
        pd.testing.assert_frame_equal(before, self.raw)
        for column, (lower, upper) in RANGES.items():
            self.assertTrue(cleaned[column].between(lower, upper).all())

    def test_grade_boundaries_and_risk(self):
        base, _ = clean_data(self.raw)
        data = pd.concat([base.iloc[[0]]] * 7, ignore_index=True)
        scores = [90, 80, 70, 60, 50, 49.99, 0]
        for col in SCORE_COLUMNS: data[col] = scores
        data['attendance_percentage'] = [75, 75, 75, 74.9, 75, 75, 0]
        result = calculate_performance(data)
        self.assertEqual(result.grade.tolist(), ['A', 'B', 'C', 'D', 'E', 'F', 'F'])
        self.assertEqual(result.status.tolist(), ['Pass'] * 5 + ['Fail'] * 2)
        self.assertEqual(result.at_risk.tolist(), [False, False, False, True, False, True, True])
        self.assertAlmostEqual(result.academic_score.iloc[5], 49.99)

    def test_invalid_schema_and_files(self):
        for content in [b'', b'col\n']:
            with self.assertRaises(ValueError): load_csv(io.BytesIO(content))
        with self.assertRaises(ValueError): clean_data(pd.DataFrame({'wrong': [1]}))
        with self.assertRaises(ValueError): clean_data(pd.DataFrame(columns=self.raw.columns))

    def test_conflicting_ids_and_fallback(self):
        raw = self.raw.iloc[:3].copy()
        raw.loc[1, 'student_id'] = raw.loc[0, 'student_id']
        raw.loc[2, 'student_id'] = ''
        raw['quiz_score'] = 'invalid'
        cleaned, report = clean_data(raw)
        self.assertEqual(report.conflicting_ids_removed, 1)
        self.assertEqual(report.missing_ids_removed, 1)
        self.assertEqual(cleaned.quiz_score.iloc[0], 50)

    def test_empty_summary_and_safe_export(self):
        self.assertEqual(summary_metrics(pd.DataFrame())['total'], 0)
        payload = export_csv(pd.DataFrame({'name': ['=1+1', 'safe']})).decode('utf-8-sig')
        self.assertIn("'=1+1", payload)

if __name__ == '__main__': unittest.main()
