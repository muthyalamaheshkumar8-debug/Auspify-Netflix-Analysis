import React, {useState} from 'react';
import {EvidenceChart, ReportSection, RichNarrative, Dropdown, useDataApp} from '../../data-app-public.jsx';
const fmt = n => Number(n).toLocaleString('en-US');
function Text({id,children}) {return <RichNarrative id={id} value={children} label="Edit report text"/>;}
export function ReportContent(){
 const {appTitle, reviewedRows, visible, canEdit,mode,setAppTitle}=useDataApp();
 const [countryLimit,setCountryLimit]=useState('10');
 const [genreLimit,setGenreLimit]=useState('10');
 const [ratingType,setRatingType]=useState('All');
 const types=reviewedRows('types'), countries=reviewedRows('countries'),years=reviewedRows('years'),ratings=reviewedRows('ratings'),genres=reviewedRows('genres');
 const total=types.reduce((s,r)=>s+r.titles,0),movie=types.find(r=>r.type==='Movie'),tv=types.find(r=>r.type==='TV Show');
 const known=countries.filter(r=>r.country!=='Unknown');
 const peak=years.reduce((a,b)=>a.total>b.total?a:b);
 const ratingRows=ratings.map(r=>({rating:r.rating,titles:ratingType==='All'?r.total:r[ratingType]}));
 const base={valueDecimals:0,colors:['var(--chart-1)','var(--chart-2)'],startAtZero:true};
 return <article className="report-content" aria-label="Netflix internship report">
 <header className="report-hero"><Text id="byline">Auspify Technologies · Data Analysis Using Python · MUTHYALA MAHESH KUMAR</Text>
 <h1 data-data-app-title contentEditable={canEdit&&mode==='edit'} suppressContentEditableWarning onBlur={canEdit&&mode==='edit'?e=>setAppTitle(e.currentTarget.textContent.trim()||appTitle):undefined}>{appTitle}</h1></header>
 <ReportSection id="executive-summary" title="Executive Summary" queryId="types" queryIds={['types','countries','years','ratings','genres']} sourceRowsByQuery={{types,countries,years,ratings,genres}} showHeading={false}>
 <Text id="summary-body">{`## Executive Summary

The supplied sample contains ${fmt(total)} distinct title IDs: ${fmt(movie.titles)} Movies (${movie.share_pct.toFixed(1)}%) and ${fmt(tv.titles)} TV Shows (${tv.share_pct.toFixed(1)}%). Movies account for about ${(movie.titles/tv.titles).toFixed(1)} times as many titles as TV Shows.

The United States is the most frequently listed country, with ${fmt(known[0].titles)} titles. Country is unknown for 287 titles (3.3%). Country tags describe the supplied records; streaming availability cannot be inferred.

The largest release-year cohort is ${peak.release_year}, with ${fmt(peak.total)} titles. The latest recorded addition is 25 September 2021, so the smaller 2021 cohort cannot establish a full-year decline.

Use this analysis to prioritize metadata review and frame content-mix questions. Investment decisions require viewing, revenue, licensing, territory, and cost data that this sample does not provide.`}</Text></ReportSection>
 <section className="report-section"><Text id="quality-body">{`## Task 1 · Preserve records and make unknown values visible

All 8,790 source rows were retained. There were no exact duplicate rows or duplicate title IDs. “Not Given” was standardized to “Unknown”: 287 country values and 2,588 director values. Dates use ISO format; duration values have separate numeric and unit columns.

Eight rows share a title, type, and release year with another row. They are flagged for review and retained because their IDs differ. The movie named “Unknown” is also preserved. No country or director values were guessed.`}</Text></section>
 <section className="report-section"><Text id="types-body">{`## Task 2 · Movies account for ${movie.share_pct.toFixed(1)}% of titles

The remaining ${tv.share_pct.toFixed(1)}% are TV Shows. Counts measure title records: a multi-season show and a single movie each contribute one title. This does not compare viewing hours, popularity, or content spending.`}</Text>
 {visible('content-types')&&<EvidenceChart id="content-types" queryId="types" title="Movies and TV Shows in the supplied sample" spec={{...base,type:'bar',x:'type',y:'titles',yLabel:'Titles'}} rows={types} sourceRows={types} height={320}/>}</section>
 <section className="report-section"><Text id="countries-body">{`## Task 3 · The United States leads the listed country ranking

India follows with 1,057 titles; the United Kingdom has 638. The full ranking retains unknown country separately. The pipeline supports multiple country tags, counting each title once per distinct country; country shares can then overlap. This supplied file has one country per title, and its upstream attribution methodology is undocumented.

Country labels cannot establish where customers can watch a title or verify its production origin. Geographic expansion decisions need territory-level licensing and viewing data.`}</Text>
 {visible('country-rankings')&&<EvidenceChart id="country-rankings" queryId="countries" title="Most frequently listed countries" spec={{...base,type:'horizontalBar',x:'country',y:'titles',yLabel:'Titles',stackable:false}} rows={known.slice(0,Number(countryLimit))} sourceRows={countries} height={countryLimit==='10'?420:720} headerControls={<Dropdown label="Countries shown" showLabel value={countryLimit} choices={['10','20']} onChange={setCountryLimit}/>}/>}</section>
 <section className="report-section"><Text id="years-body">{`## Task 4 · The 2018 cohort contains the most titles

The sample spans original release years 1925–2021. The trend table includes every year in that range, counts by content type, and year-over-year changes. A zero means no record in this sample. Percentage change is undefined when the preceding year has zero titles.

This is a release-year composition of retained titles, not Netflix's annual production or acquisition rate. The 2021 cohort is incomplete. Differences may reflect catalog coverage or retention as well as release activity.`}</Text>
 {visible('release-trend')&&<EvidenceChart id="release-trend" queryId="years" title="Title counts by original release year" spec={{...base,type:'line',x:'release_year',y:'Movie',fields:['Movie','TV Show'],xLabel:'Original release year',yLabel:'Titles'}} rows={years} sourceRows={years} height={350}/>}</section>
 <section className="report-section"><Text id="ratings-body">{`## Task 5 · TV-MA is the most common rating

TV-MA appears on 3,205 titles (36.5%). TV-14 follows with 2,157. Within each content type, TV-MA represents 33.7% of Movies and 42.9% of TV Shows. The difference is 9.2 percentage points. Select a content type to compare its counts; the exported table also contains shares within each type.

Ratings describe content guidance, not measured audience ages or demand. NR and UR retain their source labels without an invented age group.`}</Text>
 {visible('rating-mix')&&<EvidenceChart id="rating-mix" queryId="ratings" title={`Content ratings · ${ratingType}`} spec={{...base,type:'horizontalBar',x:'rating',y:'titles',yLabel:'Titles'}} rows={ratingRows} sourceRows={ratings} height={520} headerControls={<Dropdown label="Content type" showLabel value={ratingType} choices={['All','Movie','TV Show']} onChange={setRatingType}/>}/>}
 <Text id="genres-body">{`### Genre tags overlap

International Movies is the most frequent tag, attached to 2,752 titles (31.3%). Dramas has 2,426 and Comedies has 1,674. Each title can appear in several genres; genre counts and shares must not be added as mutually exclusive categories. Hover charts for exact values and use source menus for reviewed rows.`}</Text>
 {visible('genre-rankings')&&<EvidenceChart id="genre-rankings" queryId="genres" title="Most frequent genre tags" spec={{...base,type:'horizontalBar',x:'genre',y:'titles',yLabel:'Titles',stackable:false}} rows={genres.slice(0,Number(genreLimit))} sourceRows={genres} height={genreLimit==='10'?440:760} headerControls={<Dropdown label="Genres shown" showLabel value={genreLimit} choices={['10','20']} onChange={setGenreLimit}/>}/>}</section>
 <ReportSection id="business-implications" title="Task 6 · Business implications" queryId="types" queryIds={['types','countries','years','ratings','genres']} sourceRowsByQuery={{types,countries,years,ratings,genres}} showHeading={false}>
 <Text id="implications-body">{`## Task 6 · Identify questions worth validating

- **Improve metadata first.** Review the 287 unknown countries and 2,588 unknown directors using an authoritative catalog source. Filling these with the most frequent value would inflate specific groups.
- **Validate the content-mix opportunity.** Compare watch hours per title, engagement, completion rates, and licensing costs by content type before proposing a portfolio shift.
- **Check territory coverage.** Reconcile country labels with documented origin and territory availability before considering expansion. The country ranking does not measure local demand.
- **Pair audience and cost evidence.** Use common rating and genre groups as segmentation hypotheses. Test against viewing behavior, revenue, and rights costs before investment decisions.

No causal claims, market forecasts, or financial returns are estimated from this descriptive sample.`}</Text></ReportSection>
 <section className="report-section"><Text id="methods-body">{`## Sources, methods, and assistance

Source: [Dataset.csv supplied by Auspify](https://drive.google.com/file/d/1xDLw0Z9Uc3YHRgU6ExrZHzWfyRiVtfdz/view). Requirements: [Data Analysis Using Python task list](https://drive.google.com/file/d/1sLsTRUFUWIrISPGrEDDdEigzT_q0wtkD/view). Historical supplied records; not a live Netflix feed. Collection date, coverage, upstream transformations, and redistribution license are undocumented.

Run \`python analyze.py\` to regenerate the cleaned dataset, audit, tables, charts, and reviewed snapshot. The package retains the source file SHA-256 and independent reconciliation checks. Country and genre lists are split, trimmed, deduplicated within each title, and counted by distinct show_id. No external enrichment is applied.

Prepared on 29 October 2026 for MUTHYALA MAHESH KUMAR. Implementation, analysis, and documentation were produced with AI assistance. The intern should review and explain the code and confirm that this assistance meets Auspify's rules before submission. Project deliverables do not certify attendance or company approval.`}</Text></section>
 </article>;
}
