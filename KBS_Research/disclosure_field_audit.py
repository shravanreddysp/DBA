"""Audit retrospective CORDIS project field availability, not disclosure dates.

A field's presence in the current download is NOT evidence that it was
published before the temporal prediction cutoff.
"""
import argparse
import json
import zipfile
from collections import Counter
from pathlib import Path
from prepare_cordis import field, parse_date, rows_from_zip

CANDIDATES=('publicationDate','publishedDate','datePublished',
            'lastUpdateDate','lastUpdated','updateDate','contentUpdateDate','startDate','endDate',
            'signatureDate','ecSignatureDate')

def audit(archive):
    with zipfile.ZipFile(archive) as z:
        rows=rows_from_zip(z,'project.csv')
        count=0
        field_names=set()
        nonempty=Counter()
        parsed=Counter()
        examples={}
        for row in rows:
            count+=1
            field_names.update(row)
            for key in CANDIDATES:
                value=field(row,key)
                if value:
                    nonempty[key]+=1
                    if parse_date(value):
                        parsed[key]+=1
                    examples.setdefault(key,value[:30])
    return {'project_rows':count,'project_columns':sorted(str(k) for k in field_names if k),
            'candidate_date_fields':{key:{'nonempty':nonempty[key],'parseable':parsed[key],
                                          'sample_value':examples.get(key)}
                                     for key in CANDIDATES},
            'historical_disclosure_verified':False,
            'interpretation':'Retrospective metadata inventory only. Dates may be project dates or latest updates, not first public availability. No leakage-free temporal claim is supported without point-in-time evidence.'}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--zip',type=Path,default=Path('data/raw/cordis-HORIZONprojects-csv.zip'))
    p.add_argument('--out',type=Path,default=Path('data/processed/disclosure_field_audit.json'))
    args=p.parse_args()
    result=audit(args.zip)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'project_rows':result['project_rows'],
                      'candidate_date_fields':result['candidate_date_fields'],
                      'historical_disclosure_verified':False},indent=2))
