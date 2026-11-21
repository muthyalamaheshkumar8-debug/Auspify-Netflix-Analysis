# Netflix analysis — Auspify internship project

Prepared for **MUTHYALA MAHESH KUMAR** · Data Analysis Using Python · 29 October 2026.

**Author:** [muthyalamaheshkumar8-debug](https://github.com/muthyalamaheshkumar8-debug)  
**Live report (GitHub Pages):** https://muthyalamaheshkumar8-debug.github.io/auspify-netflix-analysis/

All six assigned project tasks are implemented. The guidelines require any four. This package contains project deliverables; it does not certify internship attendance, acceptance, submission, or company approval.

## Run the Python analysis

Use Python 3.10 or later in a virtual environment:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python analyze.py
python validate.py
```

The input path defaults to `data/raw/Dataset.csv`. To analyze a compatible replacement: `python analyze.py --input /path/to/Dataset.csv`. Do not replace the assigned file when submitting this result.

## Task evidence

| Task | Implementation and evidence |
|---|---|
| 1. Cleaning and preparation | `clean_data()` in `analyze.py`; `tasks/task_1/netflix_cleaned.csv`, `quality_audit.json`, `potential_duplicate_titles.csv`; `screenshots/task_1_quality.png` |
| 2. Content type dashboard | `aggregate()`; `tasks/task_2/content_types.csv`; interactive report content-type chart; `screenshots/task_2_content_types.png` |
| 3. Country analysis | `memberships()` and `aggregate()`; `tasks/task_3/country_rankings.csv`; interactive top-10/top-20 selector; `screenshots/task_3_countries.png` |
| 4. Release-year trends | Complete year grid and year-over-year changes in `tasks/task_4/release_year_trends.csv`; interactive trend; `screenshots/task_4_release_trends.png` |
| 5. Ratings and genres | `tasks/task_5/ratings_by_type.csv`, `genre_rankings.csv`; interactive type selector and genre ranking; `screenshots/task_5_ratings.png`, `task_5_genres.png` |
| 6. Business insights report | Interactive report HTML and React source in `report-app/`; full reviewed snapshot in `tasks/task_6/`; findings, limitations, and business implications in the report |

PNG charts are actual Python-generated output evidence, not fabricated photographs of an application. Rendered report screenshots, where present, are identified separately. The demonstration video is optional and is not included.

## Main findings

- 8,790 title IDs: 6,126 Movies (69.7%) and 2,664 TV Shows (30.3%).
- United States: 3,240 listed titles; India: 1,057; United Kingdom: 638. Unknown country: 287.
- 2018 is the largest original-release-year cohort, with 1,146 titles. The latest recorded addition is 25 September 2021.
- TV-MA: 3,205 titles. Its share within TV Shows is 42.9%, versus 33.7% within Movies, a 9.2 percentage-point difference.
- International Movies: 2,752 genre memberships; Dramas: 2,426; Comedies: 1,674. Genres overlap.

## Cleaning decisions

The supplied file is already partly prepared and contains no literal null cells. `Not Given` is still unknown information: 287 countries and 2,588 directors. These values become explicit `Unknown`, with missingness flags. They are not imputed. Text whitespace and list formatting are standardized, ratings use their source codes, and dates become ISO dates. Numeric durations remain separate from their minutes/seasons units. No invalid dates or exact duplicates were found.

Rows with distinct IDs but identical title/type/year are flagged, not deleted. Eight rows are flagged; matching titles do not establish duplicate entities. The real movie named `Unknown` is preserved. Source identifiers and titles reconcile independently to the cleaned output. Unexpected types, ratings, dates, years, duplicate-ID conflicts, or duration-unit mismatches stop processing for review.

## What the dataset can and cannot establish

This is the assigned historical dataset, not the current Netflix catalog. The original collection method, country attribution, upstream transformations, and license are not documented. Country labels cannot establish streaming availability or independently verify production origins. This supplied version has one country per title; the pipeline also supports multi-country titles. A title with multiple country or genre tags counts once within each distinct tag, so shares can overlap.

Release-year counts describe titles retained in this sample. They are not Netflix annual production, purchases, subscribers, demand, or revenue. The 2021 cohort is partial. No evidence supports a causal or financial conclusion. Business recommendations identify questions to validate with authoritative catalog, engagement, licensing, and cost data.

## Reproducibility and source

- [Assigned task folder](https://drive.google.com/drive/folders/1mJmGbrwELT6iUBrdiP_xHb_yANMI6OZg)
- [Assigned dataset](https://drive.google.com/file/d/1xDLw0Z9Uc3YHRgU6ExrZHzWfyRiVtfdz/view)
- [Task guidelines](https://drive.google.com/file/d/1sLsTRUFUWIrISPGrEDDdEigzT_q0wtkD/view)
- SHA-256: `90b02beeb554921f81d3b9a774d0f7766f6a65240162565f6b4082165dc2a1d3`
- `validate.py` uses independent Python CSV counters to reconcile types, countries, genres, years, and ratings. It also tests meaningful cleaning boundaries. Actual results appear in `VALIDATION.txt`.

## Interactive report

Open `tasks/task_6/Netflix_Business_Insights.html` in a modern browser after extracting the ZIP. It is a complete offline report. The charts provide hover details and the country, genre, and rating selectors are interactive. Source menus retain reviewed values and methods. A private hosted preview, when available, is for the account owner; do not use an owner-private URL as an evaluator-accessible submission link.

The complete React authoring source is included in `report-app/src/content/report/ReportContent.jsx`; `report-app/AGENTS.md` documents its runtime. The complete portable compiled report is included under `tasks/task_6/` so reviewers do not need the authoring toolchain. To serve it locally: `python -m http.server 8000 --directory tasks/task_6`. Then open the HTML report from the server listing. The React source uses the documented Data app authoring runtime; the Python analysis has no dependency on that runtime.

## Assistance disclosure and review

Implementation, analysis, validation code, charts, and documentation were produced with AI assistance. MUTHYALA MAHESH KUMAR should review the code, reproduce the results, and be able to explain the methods. The provided guidelines require original, plagiarism-free submissions and do not state a specific AI policy. Confirm any additional mentor rules before submission. Do not claim independent unaided authorship or fabricate attendance, work logs, screenshots, or approval.

## Final submission

The email specifies **22 November 2026** as the last submission date. Submit the source and output screenshots through the supplied Google Form. GitHub is requested only “if available”; no GitHub repository has been created or changed by this package. A Google sign-in is required to access the form in the available browser. The package is prepared for review; no form response or acceptance email has been sent.

[Submission form](https://docs.google.com/forms/d/e/1FAIpQLSeJLbjJ2H-neq-GHe_RPNkDXYEZ839MaO3TBIesZT8VSrbieQ/viewform)
