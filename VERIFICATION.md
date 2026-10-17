# Verification

- Six automated unittest tests passed, including Streamlit AppTest navigation through all five sections and an empty-filter interaction.
- Pipeline checks cover known defect counts, valid numeric ranges, preserving raw inputs, missing/duplicate IDs, fallback imputation, grade boundaries, pass/fail and risk thresholds, invalid input, empty summaries and formula-safe CSV exports.
- All notebook code cells executed successfully with the shared modules.
- Subject-average chart rendered and visually inspected.
- Tested with Python 3.12, Streamlit 1.66.0, Pandas 2.2.3, NumPy 2.3.5 and Matplotlib 3.10.8.
- No manual browser layout inspection or live hosting deployment was performed. File uploads were checked through the CSV loading/cleaning functions, not a browser upload interaction.

Reproduce automated checks from the project root:
```bash
python -m unittest discover -s tests -v
```
