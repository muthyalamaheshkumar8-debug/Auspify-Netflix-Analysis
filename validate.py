"""Meaningful checks of cleaning policies and independent source reconciliation."""
import csv
from collections import Counter
import json
import unittest
import unicodedata
import pandas as pd
from analyze import ROOT, clean_data, memberships

class CleaningTests(unittest.TestCase):
    def setUp(self):
        self.raw=pd.read_csv(ROOT/'data/raw/Dataset.csv').head(3).copy()
    def test_literal_unknown_title_is_preserved(self):
        self.raw.loc[0,'title']='Unknown'
        frame,_=clean_data(self.raw)
        self.assertEqual(frame.loc[0,'title'],'Unknown')
    def test_missing_country_remains_unknown(self):
        self.raw.loc[0,'country']=' Not Given '
        frame,audit=clean_data(self.raw)
        self.assertEqual(frame.loc[0,'country'],'Unknown')
        self.assertTrue(frame.loc[0,'country_missing'])
        self.assertEqual(audit['country_unknown'],1)
    def test_exact_duplicate_removed(self):
        frame,audit=clean_data(pd.concat([self.raw,self.raw.iloc[[0]]]))
        self.assertEqual(len(frame),3)
        self.assertEqual(audit['removed_exact_duplicates'],1)
    def test_conflicting_id_stops_pipeline(self):
        changed=self.raw.iloc[[0]].copy();changed['title']='Different title'
        with self.assertRaisesRegex(ValueError,'Conflicting'):
            clean_data(pd.concat([self.raw,changed]))
    def test_formatting_and_date_normalized(self):
        self.raw.loc[0,'country']=' India , India , United States '
        self.raw.loc[0,'type']=' movie '
        frame,_=clean_data(self.raw)
        self.assertEqual(frame.loc[0,'country'],'India, United States')
        self.assertEqual(frame.loc[0,'type'],'Movie')
        self.assertEqual(frame.loc[0,'date_added'],'2021-09-25')
    def test_bad_date_stops_pipeline(self):
        self.raw.loc[0,'date_added']='invalid'
        with self.assertRaisesRegex(ValueError,'invalid date'):clean_data(self.raw)
    def test_duration_unit_mismatch_stops_pipeline(self):
        self.raw.loc[0,'duration']='1 Season'
        with self.assertRaisesRegex(ValueError,'Duration unit'):clean_data(self.raw)
    def test_multi_country_counts_once_per_title(self):
        self.raw.loc[0,'country']='India, United States, India'
        frame,_=clean_data(self.raw);expanded=memberships(frame,'country','country')
        first=expanded.loc[expanded.show_id.eq(frame.loc[0,'show_id'])]
        self.assertEqual(set(first.country),{'India','United States'})
        self.assertEqual(len(first),2)
    def test_null_country_and_director_not_guessed(self):
        self.raw.loc[0,['country','director']]=None
        frame,_=clean_data(self.raw)
        self.assertEqual(frame.loc[0,'country'],'Unknown')
        self.assertEqual(frame.loc[0,'director'],'Unknown')
    def test_invalid_year_stops_pipeline(self):
        self.raw['release_year']=self.raw['release_year'].astype(float)
        self.raw.loc[0,'release_year']=2020.5
        with self.assertRaisesRegex(ValueError,'release year'):clean_data(self.raw)
    def test_invalid_type_stops_pipeline(self):
        self.raw.loc[0,'type']='Podcast'
        with self.assertRaisesRegex(ValueError,'content type'):clean_data(self.raw)

class SourceReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Independent stdlib CSV/Counter implementation, not aggregate().
        with (ROOT/'data/raw/Dataset.csv').open(newline='',encoding='utf-8-sig') as f:
            cls.raw=list(csv.DictReader(f))
        cls.clean=pd.read_csv(ROOT/'tasks/task_1/netflix_cleaned.csv')
    def test_id_and_title_integrity(self):
        original={r['show_id']:' '.join(unicodedata.normalize('NFC',r['title']).split()) for r in self.raw}
        self.assertEqual(dict(zip(self.clean.show_id,self.clean.title)),original)
    def test_types_independently_reconcile(self):
        counts=Counter(r['type'] for r in self.raw)
        out=pd.read_csv(ROOT/'tasks/task_2/content_types.csv')
        self.assertEqual(dict(zip(out.type,out.titles)),dict(counts))
        self.assertAlmostEqual(out.share_pct.sum(),100,places=5)
    def test_country_memberships_reconcile(self):
        counts=Counter()
        for row in self.raw:
            for country in set(x.strip() for x in row['country'].split(',')):
                counts['Unknown' if country=='Not Given' else country]+=1
        out=pd.read_csv(ROOT/'tasks/task_3/country_rankings.csv')
        self.assertEqual(dict(zip(out.country,out.titles)),dict(counts))
    def test_year_counts_and_yoy_reconcile(self):
        counts=Counter(int(r['release_year']) for r in self.raw)
        out=pd.read_csv(ROOT/'tasks/task_4/release_year_trends.csv')
        self.assertEqual(out.total.sum(),len(self.raw))
        for r in out.itertuples():self.assertEqual(r.total,counts[r.release_year])
        for previous,current in zip(out.itertuples(),list(out.itertuples())[1:]):
            self.assertEqual(current.change_titles,current.total-previous.total)
            if previous.total:
                self.assertAlmostEqual(current.change_pct,(current.total/previous.total-1)*100,places=5)
            else:self.assertTrue(pd.isna(current.change_pct))
    def test_genre_memberships_reconcile(self):
        counts=Counter()
        for row in self.raw:
            counts.update(set(x.strip() for x in row['listed_in'].split(',')))
        out=pd.read_csv(ROOT/'tasks/task_5/genre_rankings.csv')
        self.assertEqual(dict(zip(out.genre,out.titles)),dict(counts))
    def test_rating_matrix_and_shares_reconcile(self):
        counts=Counter((r['rating'],r['type']) for r in self.raw)
        out=pd.read_csv(ROOT/'tasks/task_5/ratings_by_type.csv')
        for row in out.to_dict('records'):
            for typ in ['Movie','TV Show']:self.assertEqual(row[typ],counts[row['rating'],typ])
            self.assertEqual(row['total'],row['Movie']+row['TV Show'])
        for typ in ['Movie','TV Show']:self.assertAlmostEqual(out[typ+'_share_pct'].sum(),100,places=5)
    def test_snapshot_matches_exported_tables(self):
        snapshot=json.loads((ROOT/'tasks/task_6/reviewed_snapshot.json').read_text())
        self.assertEqual(sum(r['titles'] for r in snapshot['queries']['types']['rows']),len(self.raw))
        self.assertEqual(sum(r['total'] for r in snapshot['queries']['years']['rows']),len(self.raw))

if __name__=='__main__':unittest.main(verbosity=2)
