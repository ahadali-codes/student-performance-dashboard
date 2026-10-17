"""Streamlit presentation layer. Run: streamlit run app.py."""
from dataclasses import asdict
from pathlib import Path
import io
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from src.data_cleaning import load_csv, clean_data, SUBJECT_COLUMNS
from src.analysis import (calculate_performance, summary_metrics, group_performance,
                          correlation, export_csv, GRADE_ORDER)
from src.visualizations import bar_chart, scatter_chart

DATA_PATH = Path(__file__).resolve().parent / 'data/student_performance.csv'
PAGES = ['Overview Dashboard', 'Student Analysis', 'Subject Analysis', 'Performance Insights', 'Dataset Explorer']


def show_chart(figure):
    """Release Matplotlib resources after sending each figure to Streamlit."""
    try:
        st.pyplot(figure, width='stretch')
    finally:
        plt.close(figure)


def filtered_dataset(data: pd.DataFrame) -> pd.DataFrame:
    """Apply all sidebar predicates to the same cleaned and scored cohort."""
    mask = pd.Series(True, index=data.index)
    for column, label in [('department', 'Department'), ('semester', 'Semester'),
                           ('gender', 'Gender'), ('grade', 'Grade'), ('status', 'Pass/fail status')]:
        choices = [grade for grade in GRADE_ORDER if grade in data.grade.values] if column == 'grade' else sorted(data[column].unique())
        selected = st.sidebar.multiselect(label, choices, default=choices)
        mask &= data[column].isin(selected)
    attendance = st.sidebar.slider('Attendance range (%)', 0, 100, (0, 100))
    mask &= data.attendance_percentage.between(*attendance)
    return data.loc[mask].copy()


def main() -> None:
    """Load, validate, filter and render the selected dashboard section."""
    st.set_page_config(page_title='Student Academic Performance', page_icon='🎓', layout='wide')
    st.markdown('''<style>
    .block-container {padding-top:2rem;padding-bottom:3rem;max-width:1400px;}
    [data-testid="stMetric"] {background:var(--secondary-background-color);padding:1rem;border-radius:10px;}
    </style>''', unsafe_allow_html=True)
    st.sidebar.title('Student dashboard')
    page = st.sidebar.radio('Navigation', PAGES)
    st.sidebar.divider()
    uploaded = st.sidebar.file_uploader('Upload student CSV', type=['csv'], help='UTF-8 CSV, all 18 required columns. Maximum 10 MB.')
    try:
        if uploaded is not None:
            if uploaded.size > 10 * 1024 * 1024:
                raise ValueError('Please upload a CSV smaller than 10 MB.')
            raw = load_csv(io.BytesIO(uploaded.getvalue()))
        else:
            raw = load_csv(DATA_PATH)
        cleaned, report = clean_data(raw)
        data = calculate_performance(cleaned)
    except ValueError as exc:
        st.error(str(exc))
        st.info('Use the supplied student_performance.csv as a schema template. Remove the upload to restore demo data.')
        st.stop()
    st.sidebar.caption('Uploaded data' if uploaded is not None else 'Fictional demo data')
    st.sidebar.subheader('Filter the cohort')
    filtered = filtered_dataset(data)
    st.title(page)
    st.caption(f'Student dashboard · {len(filtered):,} of {len(data):,} students selected')
    if uploaded is None:
        st.caption('This sample dataset is fictional and meant for demo purposes.')
    st.sidebar.download_button('Download filtered CSV', export_csv(filtered), 'filtered_students.csv', 'text/csv', width='stretch')
    st.sidebar.caption('Score: assignments 15% · quizzes 10% · midterm 20% · final 30% · subject mean 25%.')
    if filtered.empty:
        st.warning('No students match these filters. Broaden your sidebar selections.')
        st.stop()
    imputed = int((filtered.imputed_numeric_count > 0).sum())
    if imputed:
        st.info(f'{imputed} selected students have imputed numeric values. Check Dataset Explorer before interpreting rankings or risk flags.')
    if page == 'Overview Dashboard':
        metrics = summary_metrics(filtered)
        columns = st.columns(5)
        for col, label, value in zip(columns, ['Total students', 'Average score', 'Average attendance', 'Pass rate', 'Highest score'],
            [f"{metrics['total']:,}", f"{metrics['average_score']:.1f}", f"{metrics['average_attendance']:.1f}%", f"{metrics['pass_rate']:.1f}%", f"{metrics['highest_score']:.1f}"]):
            col.metric(label, value)
        left, right = st.columns(2)
        with left:
            grades = filtered.grade.value_counts().reindex(GRADE_ORDER, fill_value=0)
            show_chart(bar_chart(grades.index, grades.values, 'Grade distribution'))
        with right:
            counts = filtered.status.value_counts().reindex(['Pass', 'Fail'], fill_value=0)
            show_chart(bar_chart(counts.index, counts.values, 'Pass / fail distribution'))
        groups = group_performance(filtered, 'department')
        show_chart(bar_chart(groups.department, groups.average_score, 'Department performance', 'Mean academic score', True))
    elif page == 'Student Analysis':
        labels = {row.student_id: f'{row.student_id} · {row.name}' for row in filtered.itertuples()}
        student_id = st.selectbox('Select a student', list(labels), format_func=labels.get)
        student = filtered[filtered.student_id == student_id].iloc[0]
        a, b, c, d = st.columns(4)
        a.metric('Academic score', f'{student.academic_score:.1f}')
        b.metric('Grade', student.grade)
        c.metric('Attendance', f'{student.attendance_percentage:.1f}%')
        d.metric('Result', student.status)
        if student.at_risk:
            st.warning(f'Support indicator: {student.risk_reason}. Review the record and imputation flags before taking action.')
        details, subjects = st.tabs(['Student record', 'Subject scores'])
        with details:
            st.dataframe(student.to_frame('Value').astype(str), width='stretch')
        with subjects:
            show_chart(bar_chart([c.replace('_score', '').title() for c in SUBJECT_COLUMNS],
                                  student[SUBJECT_COLUMNS].astype(float).values, 'Individual subject scores', 'Score'))
        st.subheader('Top-performing students in the filtered cohort')
        top = filtered.sort_values(['academic_score', 'student_id'], ascending=[False, True]).head(10)
        show_chart(bar_chart(top.student_id, top.academic_score, 'Top 10 students', 'Academic score', True))
        st.dataframe(top[['student_id', 'name', 'department', 'academic_score', 'grade', 'score_imputed']], hide_index=True, width='stretch')
    elif page == 'Subject Analysis':
        means = filtered[SUBJECT_COLUMNS].mean().sort_values(ascending=False)
        show_chart(bar_chart([x.replace('_score', '').title() for x in means.index], means.values, 'Subject averages', 'Mean score'))
        st.subheader('Subject summary')
        stats = filtered[SUBJECT_COLUMNS].agg(['mean', 'median', 'min', 'max', 'std']).T
        stats.index = stats.index.str.replace('_score', '').str.title()
        st.dataframe(stats.round(2), width='stretch')
        st.caption('Standard deviation is undefined for a cohort of one student.')
        groups = group_performance(filtered, 'semester')
        show_chart(bar_chart(groups.semester, groups.average_score, 'Semester performance', 'Mean academic score'))
        st.dataframe(groups.round(2), hide_index=True, width='stretch')
    elif page == 'Performance Insights':
        st.caption('Orange points indicate academic risk. Associations do not establish causation.')
        attendance, study, risk = st.tabs(['Attendance', 'Study time', 'Academic risk'])
        for tab, column, label in [(attendance, 'attendance_percentage', 'Attendance (%)'), (study, 'study_hours_per_week', 'Study hours per week')]:
            with tab:
                show_chart(scatter_chart(filtered, column, label, f'{label} vs academic score'))
                value = correlation(filtered, column)
                st.write('Pearson correlation: ' + (f'{value:.2f}' if value is not None else 'Unavailable: at least 3 observations with variation are required.'))
        with risk:
            students = filtered[filtered.at_risk]
            st.metric('Students who may need support', len(students))
            st.write('Flagged when attendance is below 75% or academic score is below 50. A flag is an invitation to review and offer support.')
            st.dataframe(students[['student_id', 'name', 'department', 'attendance_percentage', 'academic_score', 'risk_reason', 'score_imputed', 'attendance_imputed']], hide_index=True, width='stretch')
    else:
        records, quality, schema = st.tabs(['Filtered results', 'Cleaning audit', 'CSV schema'])
        with records:
            st.dataframe(filtered, hide_index=True, width='stretch')
            st.download_button('Download this table', export_csv(filtered), 'student_analysis.csv', 'text/csv')
        with quality:
            st.caption('Audit counts describe the full loaded dataset before sidebar filters.')
            audit = asdict(report)
            st.json({key: value for key, value in audit.items() if not isinstance(value, dict)})
            table = pd.DataFrame({'Invalid numeric': report.invalid_numeric_values, 'Imputed numeric': report.imputed_numeric_values, 'Unit strings converted': report.normalized_numeric_values}).fillna(0).astype(int)
            st.dataframe(table, width='stretch')
            st.write('Unknown categorical values:', report.unknown_categories)
            st.write('Numeric blanks and invalid values use the valid column median. Entirely invalid columns use documented defaults. Integer medians are rounded. Exact duplicates are removed, then repeated IDs keep the first record. Raw input is never overwritten.')
            st.dataframe(raw.head(30), hide_index=True, width='stretch')
        with schema:
            st.markdown('See the README for the 18 required columns and valid ranges. Column names accept case differences and spaces in place of underscores.')
            st.code(','.join(raw.columns))
            st.write('Grading: A ≥90, B ≥80, C ≥70, D ≥60, E ≥50, F <50. Passing score: 50. Grades use the unrounded score.')


if __name__ == '__main__':
    main()
