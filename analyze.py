"""Reproduce all six Auspify Netflix tasks from the supplied CSV. Python 3.10+."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import unicodedata
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
UNKNOWN = 'Unknown'
MISSING = {'', 'not given', 'not available', 'unknown', 'null', 'none', 'n/a', 'nan'}
RATINGS = {'G','PG','PG-13','R','NC-17','TV-Y','TV-Y7','TV-Y7-FV','TV-G','TV-PG','TV-14','TV-MA','NR','UR'}
COLORS = {'Movie': '#275d9d', 'TV Show': '#b45c30'}

def normalize_text(value):
    if pd.isna(value):
        return pd.NA
    text = re.sub(r'\s+', ' ', unicodedata.normalize('NFC', str(value))).strip()
    return pd.NA if text.casefold() in MISSING else text

def normalize_list(value):
    text = normalize_text(value)
    if pd.isna(text):
        return pd.NA
    # Preserve source names; do not infer geography or invent countries.
    parts = [normalize_text(part) for part in text.split(',')]
    return ', '.join(dict.fromkeys(str(part) for part in parts if not pd.isna(part))) or pd.NA

def clean_data(raw):
    required = {'show_id','type','title','director','country','date_added','release_year','rating','duration','listed_in'}
    missing = required - set(raw.columns)
    if missing:
        raise ValueError(f'Missing required columns: {sorted(missing)}')
    frame = raw.copy(deep=True)
    frame.columns = frame.columns.str.strip().str.lower()
    for col in frame:
        if col != 'release_year':
            if col in {'title','show_id'}:
                # Titles such as the movie "Unknown" are real labels, not missing values.
                frame[col] = frame[col].map(lambda v: pd.NA if pd.isna(v) or not str(v).strip() else re.sub(r'\s+', ' ', unicodedata.normalize('NFC', str(v))).strip())
            else:
                frame[col] = frame[col].map(normalize_text)
    if frame[['show_id','type','title']].isna().any().any():
        raise ValueError('Missing essential identifier, content type, or title; manual review required.')
    frame['type'] = frame['type'].str.casefold().map({'movie':'Movie','tv show':'TV Show'})
    if frame['type'].isna().any():
        raise ValueError('Unrecognized content type; manual review required.')
    before = len(frame)
    frame = frame.drop_duplicates().copy()
    if frame['show_id'].duplicated().any():
        raise ValueError('Conflicting rows share a show_id; manual review required.')
    frame['country'] = frame['country'].map(normalize_list)
    frame['listed_in'] = frame['listed_in'].map(normalize_list)
    frame['country_missing'] = frame['country'].isna()
    frame['director_missing'] = frame['director'].isna()
    frame['rating'] = frame['rating'].str.upper()
    if not set(frame['rating'].dropna()).issubset(RATINGS):
        raise ValueError('Unrecognized ratings; manual review required.')
    parsed_date = pd.to_datetime(frame['date_added'], format='mixed', errors='coerce')
    invalid_dates = int((frame['date_added'].notna() & parsed_date.isna()).sum())
    if invalid_dates:
        raise ValueError(f'{invalid_dates} invalid date values require manual review.')
    frame['date_added'] = parsed_date.dt.strftime('%Y-%m-%d').fillna('')
    years = pd.to_numeric(frame['release_year'], errors='coerce')
    if years.isna().any() or (years % 1 != 0).any() or not years.between(1888, 2026).all():
        raise ValueError('Invalid release year; manual review required.')
    frame['release_year'] = years.astype(int)
    duration = frame['duration'].str.extract(r'^(\d+)\s+(min|Season|Seasons)$')
    if (frame['duration'].notna() & duration[0].isna()).any():
        raise ValueError('Unrecognized duration; manual review required.')
    unit = duration[1].map({'min':'minutes','Season':'seasons','Seasons':'seasons'})
    mismatch = ((frame['type'].eq('Movie') & unit.eq('seasons')) |
                (frame['type'].eq('TV Show') & unit.eq('minutes')))
    if mismatch.any():
        raise ValueError('Duration unit does not match content type.')
    frame['duration_value'] = pd.to_numeric(duration[0]).astype('Int64')
    frame['duration_unit'] = unit.fillna(UNKNOWN)
    frame['potential_duplicate_title'] = frame.duplicated(['title','type','release_year'], keep=False)
    for col in ['director','country','rating','duration','listed_in']:
        frame[col] = frame[col].fillna(UNKNOWN)
    audit = {
        'raw_rows':len(raw), 'clean_rows':len(frame), 'removed_exact_duplicates':before-len(frame),
        'duplicate_show_ids':int(frame.show_id.duplicated().sum()),
        'country_unknown':int(frame.country_missing.sum()),
        'director_unknown':int(frame.director_missing.sum()),
        'invalid_dates':invalid_dates,
        'potential_duplicate_title_rows':int(frame.potential_duplicate_title.sum()),
        'missing_cells_raw':{k:int(v) for k,v in raw.isna().sum().items()},
        'release_year_min':int(frame.release_year.min()),'release_year_max':int(frame.release_year.max()),
        'latest_date_added':frame.date_added.max(),
        'policy':'Unknown categories remain explicit; no country/director guessing. Identical title/type/year with distinct IDs are flagged, not deleted.'
    }
    return frame, audit

def memberships(frame, col, label):
    expanded = frame[['show_id','type',col]].copy()
    expanded[label] = expanded[col].str.split(',')
    expanded = expanded.explode(label)
    expanded[label] = expanded[label].str.strip()
    return expanded[['show_id','type',label]].drop_duplicates(['show_id',label])

def aggregate(frame):
    types = frame.groupby('type', as_index=False).agg(titles=('show_id','nunique'))
    types['share_pct'] = types.titles / len(frame) * 100
    countries = memberships(frame, 'country', 'country')
    country_counts = countries.groupby('country', as_index=False).agg(titles=('show_id','nunique')).sort_values(['titles','country'],ascending=[False,True])
    country_counts['share_of_all_titles_pct'] = country_counts.titles / len(frame) * 100
    country_counts['rank_known'] = pd.Series(pd.NA, index=country_counts.index, dtype='Int64')
    known = country_counts.country.ne(UNKNOWN)
    country_counts.loc[known, 'rank_known'] = range(1, int(known.sum())+1)
    years = frame.groupby(['release_year','type']).size().unstack(fill_value=0).reindex(range(int(frame.release_year.min()),int(frame.release_year.max())+1),fill_value=0)
    years.index.name = 'release_year'
    years['total'] = years.sum(axis=1)
    years['change_titles'] = years.total.diff().astype('Int64')
    years['change_pct'] = years.total.div(years.total.shift(1).replace(0,float('nan'))).sub(1).mul(100)
    ratings = frame.groupby(['rating','type']).size().unstack(fill_value=0)
    ratings['total'] = ratings.sum(axis=1)
    ratings = ratings.sort_values('total', ascending=False)
    for typ in ['Movie','TV Show']:
        ratings[f'{typ}_share_pct'] = ratings[typ] / int(types.loc[types.type.eq(typ),'titles'].iloc[0]) * 100
    genres = memberships(frame, 'listed_in', 'genre')
    genre_counts = genres.groupby('genre',as_index=False).agg(titles=('show_id','nunique')).sort_values(['titles','genre'],ascending=[False,True])
    genre_counts['share_of_all_titles_pct'] = genre_counts.titles/len(frame)*100
    return {'types':types,'countries':country_counts,'years':years.reset_index(),'ratings':ratings.reset_index(),'genres':genre_counts}

def save_chart(fig,path):
    fig.savefig(path,dpi=170,bbox_inches='tight',facecolor='white')
    plt.close(fig)

def bar_chart(table, label, value, title, path, note, n=12):
    data = table.head(n).iloc[::-1]
    fig,ax=plt.subplots(figsize=(10,6.2))
    bars=ax.barh(data[label],data[value],color='#275d9d')
    ax.bar_label(bars,fmt='{:,.0f}',padding=5,fontsize=10)
    ax.set_xlim(0,max(data[value])*1.19);ax.set_xlabel('Titles');ax.set_title(title,loc='left',pad=19,weight='bold',fontsize=16)
    ax.spines[['top','right']].set_visible(False);ax.grid(axis='x',alpha=.13);ax.set_axisbelow(True)
    fig.text(.01,.005,note,fontsize=9,color='#525e6b',wrap=True)
    fig.tight_layout(rect=[0,.04,1,1]);save_chart(fig,path)

def charts(tables, audit, out):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
    fig,ax=plt.subplots(figsize=(10,5))
    d=tables['types'];bars=ax.bar(d.type,d.titles,color=[COLORS[t] for t in d.type],width=.5)
    ax.bar_label(bars,labels=[f'{r.titles:,} ({r.share_pct:.1f}%)' for r in d.itertuples()],padding=6)
    ax.set_ylim(0,d.titles.max()*1.2);ax.set_ylabel('Titles');ax.set_title('Movies account for most titles in the supplied dataset',loc='left',pad=20,weight='bold',fontsize=15)
    ax.spines[['top','right']].set_visible(False);fig.text(.12,.01,f"Denominator: {audit['clean_rows']:,} unique title IDs. Historical supplied data.",fontsize=9);fig.tight_layout(rect=[0,.04,1,1])
    save_chart(fig,out/'task_2_content_types.png')
    bar_chart(tables['countries'].query('country != "Unknown"'),'country','titles','Most frequently listed countries',out/'task_3_countries.png','Country tags do not establish streaming availability. Multi-country titles count once per listed country.')
    years=tables['years'];fig,ax=plt.subplots(figsize=(11,5.6))
    for typ in ['Movie','TV Show']:
        ax.plot(years.release_year,years[typ],label=typ,color=COLORS[typ],linestyle='-' if typ=='Movie' else '--',linewidth=2)
    ax.set_xlim(years.release_year.min(),years.release_year.max());ax.set_ylim(bottom=0)
    ax.set_xticks([1925,1940,1960,1980,2000,2021]);ax.set_xlabel('Original release year');ax.set_ylabel('Titles in supplied dataset');ax.legend(frameon=False)
    ax.set_title('Recent release years dominate this historical title sample',loc='left',pad=19,weight='bold',fontsize=16)
    ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.14)
    fig.text(.01,.005,'Release-year composition is not Netflix annual production. 2021 is incomplete; latest addition is 25 Sep 2021.',fontsize=9)
    fig.tight_layout(rect=[0,.04,1,1]);save_chart(fig,out/'task_4_release_trends.png')
    ratings=tables['ratings'].iloc[::-1];fig,ax=plt.subplots(figsize=(10,6.8))
    y=range(len(ratings));ax.barh(y,ratings.Movie,label='Movie',color=COLORS['Movie']);ax.barh(y,ratings['TV Show'],left=ratings.Movie,label='TV Show',color=COLORS['TV Show'])
    ax.set_yticks(list(y),ratings.rating);ax.set_xlabel('Titles');ax.set_xlim(0,ratings.total.max()*1.18)
    for i,v in enumerate(ratings.total):ax.text(v+25,i,f'{v:,}',va='center',fontsize=9)
    ax.set_title('Content ratings vary across Movies and TV Shows',loc='left',pad=19,weight='bold',fontsize=16);ax.legend(frameon=False)
    ax.spines[['top','right']].set_visible(False);fig.tight_layout();save_chart(fig,out/'task_5_ratings.png')
    bar_chart(tables['genres'],'genre','titles','Most frequent genre tags',out/'task_5_genres.png','One title can have several genre tags; counts and shares overlap.')
    missing=pd.DataFrame({'field':['Country unknown','Director unknown','Exact duplicates removed'], 'titles':[audit['country_unknown'],audit['director_unknown'],audit['removed_exact_duplicates']]})
    bar_chart(missing,'field','titles','Data cleaning preserves unknown information',out/'task_1_quality.png','Unknown information stays explicit. Source values are not invented.',n=3)

def make_snapshot(tables,audit):
    ids={'types':'content-types','countries':'country-rankings','years':'release-trend','ratings':'rating-mix','genres':'genre-rankings'}
    defs={'types':'Distinct show_id count per content type. Share denominator is all cleaned titles.',
          'countries':'Distinct title IDs per listed country. Unknown is retained. Multi-country shares can overlap; country is not a viewing-availability field.',
          'years':'Count of title IDs in the supplied sample by original release year and content type. Zero means no record in this sample. 2021 is partial.',
          'ratings':'Distinct title IDs per source rating and content type. Type shares use each type total.',
          'genres':'Distinct title IDs per listed genre. Multiple genre tags per title overlap.'}
    queries={}
    for key,frame in tables.items():
        rows=json.loads(frame.to_json(orient='records'))
        queries[key]={'rows':rows,'methods':[{'language':'python','code':f'Run python analyze.py; see aggregate() for {key} transformation.'}],
         'source':{'name':'Auspify supplied Dataset.csv','provider':'Google Drive','files':['data/raw/Dataset.csv'],
         'updatedAt':audit['latest_date_added']+'T00:00:00Z','links':[{'label':'Supplied dataset','url':'https://drive.google.com/file/d/1xDLw0Z9Uc3YHRgU6ExrZHzWfyRiVtfdz/view'}],
         'metricDefinitions':[{'label':key,'definition':defs[key],'componentIds':[ids[key]]}],
         'evidenceFlow':[{'title':'Retrieve assigned source','detail':'Google Drive fetch of supplied Dataset.csv, file ID 1xDLw0Z9Uc3YHRgU6ExrZHzWfyRiVtfdz; complete raw response, 1,071,619 bytes.'},{'title':'Clean and aggregate','detail':'analyze.py clean_data() and aggregate(); outputs retained under tasks/. Upstream collection methodology and country-tag meaning are undocumented.'}],
         'caveats':['Historical supplied sample; latest date_added is 2021-09-25. Not a current Netflix catalog.',defs[key]]}}
    return {'surface':'report','title':'Movies dominate the supplied Netflix title sample','generatedAt':'2026-10-29T00:00:00Z','status':'reviewed','buildStatus':'complete','filters':[],
        'exportPreferences':{'selected':None,'destinations':[]},'report':{'asOf':audit['latest_date_added']},'queries':queries}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,default=ROOT/'data/raw/Dataset.csv');args=parser.parse_args()
    raw=pd.read_csv(args.input);frame,audit=clean_data(raw)
    audit['raw_sha256']=hashlib.sha256(args.input.read_bytes()).hexdigest()
    out=ROOT/'tasks';out.mkdir(exist_ok=True)
    dirs={i:out/f'task_{i}' for i in range(1,7)}
    for p in dirs.values():p.mkdir(exist_ok=True)
    frame.to_csv(dirs[1]/'netflix_cleaned.csv',index=False)
    frame.loc[frame.potential_duplicate_title].to_csv(dirs[1]/'potential_duplicate_titles.csv',index=False)
    (dirs[1]/'quality_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    tables=aggregate(frame)
    locations={'types':(2,'content_types.csv'),'countries':(3,'country_rankings.csv'),'years':(4,'release_year_trends.csv'),'ratings':(5,'ratings_by_type.csv'),'genres':(5,'genre_rankings.csv')}
    for key,(task,name) in locations.items():tables[key].to_csv(dirs[task]/name,index=False,float_format='%.6f')
    screenshots=ROOT/'screenshots';screenshots.mkdir(exist_ok=True);charts(tables,audit,screenshots)
    snapshot=make_snapshot(tables,audit)
    (dirs[6]/'reviewed_snapshot.json').write_text(json.dumps(snapshot,indent=2)+'\n')
    print(json.dumps(audit,indent=2));print('All six task analyses regenerated successfully.')

if __name__=='__main__':main()
