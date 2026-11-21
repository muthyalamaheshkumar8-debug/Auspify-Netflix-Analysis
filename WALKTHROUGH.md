# Explain the project in simple words

## A short introduction

“I analyzed the Netflix dataset supplied for the Auspify internship. I used Python and Pandas to clean and group the records, and Matplotlib to generate charts. The interactive report presents content types, listed countries, release-year trends, ratings, genres, and business questions. The work was prepared with AI assistance, and I reviewed the assumptions and code before submission.”

Use the final sentence about review only after actually reviewing the work.

## Task 1: What did cleaning change?

The CSV has 8,790 rows. Each show ID identifies one title. There were no exact duplicates, so no records needed deletion. Some cells say “Not Given.” Those cells are not real country or director information. I changed them to “Unknown” and kept flags showing what is missing. I standardized spaces, dates, content types, and ratings. I separated duration values from their units, because a movie's minutes and a show's seasons cannot be combined.

## Task 2: What did you count?

There are 6,126 Movies and 2,664 TV Shows. A movie counts once and a TV Show counts once, even if it has many seasons. To calculate a type's percentage, divide its title count by 8,790 and multiply by 100. This measures titles, not viewing time.

## Task 3: Why is country analysis limited?

I counted the titles associated with each listed country. Unknown country is kept separate. The file does not explain exactly how country labels were collected. These labels do not tell us which countries can stream each title. If a title has several country labels, it counts once per distinct country, so country shares may overlap.

## Task 4: Is this Netflix's annual production?

No. It shows original release years for titles present in this historical sample. A title released in 2010 might have been added to Netflix later. A title that was removed may be absent. The 2018 cohort is largest, with 1,146 titles. The data stops during 2021, so I do not compare its partial count as a full-year production decline.

## Task 5: Why normalize ratings within each type?

Movies have more records overall. Comparing only raw counts may hide differences in rating mix. I calculate TV-MA's percentage separately within Movies and TV Shows. It is about 33.7% for Movies and 42.9% for TV Shows. That is a 9.2 percentage-point difference. Ratings are guidance labels, not proof of the real viewers' ages. Genres overlap because a title can belong to several genres.

## Task 6: What should a business do next?

First improve missing metadata. Then combine this sample with real viewing behavior, licensing territories, content costs, and revenue before making investment decisions. The descriptive data helps ask questions; it does not prove which content will earn money.

## How do you know the results are correct?

I compare the output to independent counts made directly from the original CSV. Type counts add up to all 8,790 titles. Release-year totals also add up to 8,790. Rating counts reconcile by type. Country and genre memberships reconcile separately. The validation script checks that actual titles and IDs were preserved, and tests cases such as bad dates and conflicting IDs. The file hash records the exact input used.

## Review before submitting

Run `python analyze.py` and `python validate.py`. Open the CSV tables, inspect the charts, and try the report selectors. Explain one title's journey through cleaning and grouping. Read the AI-assistance note and confirm any mentor rules. Submit the actual project package; do not claim a submission or certificate until the company confirms it.
