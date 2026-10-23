"""Build a temporal organization-collaboration dataset from official CORDIS CSV ZIP.

No labels are simulated. Requires network access at runtime. Uses only project start
dates and organization participation identifiers; avoids post-start outcomes.
A retrospective current snapshot is NOT an as-of historical snapshot.
"""
import argparse
import csv
import hashlib
import io
import json
import zipfile
from collections import defaultdict
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

SOURCE = "https://cordis.europa.eu/data/cordis-HORIZONprojects-csv.zip"
SOURCE_PAGE = "https://data.europa.eu/data/datasets/cordis-eu-research-projects-under-horizon-europe-2021-2027"

def canonical(s):
    return "".join(c for c in s.lower() if c.isalnum())

def field(row, *choices):
    lookup = {canonical(k): v for k, v in row.items() if k}
    for key in choices:
        v = lookup.get(canonical(key))
        if v is not None and str(v).strip():
            return str(v).strip()
    return ""

def parse_date(s):
    s = s.strip()[:10]
    if not s: return None
    try: return date.fromisoformat(s)
    except ValueError:
        try:
            from datetime import datetime
            return datetime.strptime(s, "%d/%m/%Y").date()
        except ValueError: return None

def rows_from_zip(zf, stem):
    name = next((n for n in zf.namelist() if Path(n).name.lower() == stem.lower()), None)
    if name is None: raise ValueError(f"Missing {stem}; archive files: {zf.namelist()[:25]}")
    with zf.open(name) as raw:
        text = io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace", newline="")
        sample = text.read(4096)
        text.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        yield from csv.DictReader(text, dialect=dialect)

def prepare(archive, out, train_end, val_end, test_end, max_orgs=60):
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        projects = {}
        for r in rows_from_zip(z, "project.csv"):
            pid = field(r, "id", "projectID", "projectId")
            d = parse_date(field(r, "startDate", "start_date"))
            if pid and d and d <= test_end:
                projects[pid] = d
        memberships = defaultdict(set)
        missing_org = 0
        for r in rows_from_zip(z, "organization.csv"):
            pid = field(r, "projectID", "projectId", "project_id")
            org = field(r, "organisationID", "organizationID", "organisationId", "organizationId")
            if pid not in projects: continue
            if not org:
                missing_org += 1
                continue
            memberships[pid].add(org)
    events = defaultdict(lambda: {"first": None, "projects": set()})
    for pid, orgs in memberships.items():
        if len(orgs) < 2 or len(orgs) > max_orgs: continue
        d = projects[pid]
        ordered = sorted(orgs)
        for i, a in enumerate(ordered):
            for b in ordered[i+1:]:
                pair = (a,b)
                rec = events[pair]
                if rec["first"] is None or d < rec["first"]: rec["first"] = d
                rec["projects"].add(pid)
    # Cohorts are based on FIRST observed collaboration. All organizations in
    # evaluation candidates must have participated in projects by train_end.
    known_orgs = set()
    for pid, orgs in memberships.items():
        if projects[pid] <= train_end: known_orgs.update(orgs)
    first = {pair: rec["first"] for pair,rec in events.items()}
    history = {pair for pair,d in first.items() if d <= train_end}
    eligible = sorted(known_orgs)
    val_pos = {pair for pair,d in first.items() if train_end < d <= val_end and pair[0] in known_orgs and pair[1] in known_orgs}
    test_pos = {pair for pair,d in first.items() if val_end < d <= test_end and pair[0] in known_orgs and pair[1] in known_orgs}
    # Candidate pairs are existing, previously unlinked organizations.
    # Unknown pairs are UNLABELED, not proven negatives. Ranking metrics must
    # be described as observed-positive retrieval with incomplete positives.
    # Every positive is already a new pair by its first-collaboration date.
    # Do not allocate O(number_of_organizations squared) candidate pairs.
    candidate_count = len(eligible)*(len(eligible)-1)//2 - sum(
        1 for a,b in history if a in known_orgs and b in known_orgs
    )
    def write(name, header, iterable):
        with (out/name).open("w", newline="", encoding="utf-8") as f:
            w=csv.writer(f);w.writerow(header);w.writerows(iterable)
    write("train_edges.csv", ["org_a","org_b","first_collaboration_date"], ((a,b,first[(a,b)].isoformat()) for a,b in sorted(history)))
    write("validation_positives.csv", ["org_a","org_b","first_collaboration_date"], ((a,b,first[(a,b)].isoformat()) for a,b in sorted(val_pos)))
    write("test_positives.csv", ["org_a","org_b","first_collaboration_date"], ((a,b,first[(a,b)].isoformat()) for a,b in sorted(test_pos)))
    write("known_organizations.csv", ["organization_id"], ((x,) for x in eligible))
    # Do not enumerate or store the potentially enormous candidate universe.
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    stats = {"source":SOURCE,"source_page":SOURCE_PAGE,"archive_sha256":digest,
      "archive_bytes":archive.stat().st_size,"train_end":str(train_end),"validation_end":str(val_end),
      "test_end":str(test_end),"max_project_organizations":max_orgs,
      "projects_with_dates":len(projects),"projects_with_memberships":len(memberships),
      "organization_rows_missing_id":missing_org,"organizations_known_by_train_end":len(eligible),
      "training_first_collaboration_edges":len(history),
      "validation_first_collaborations":len(val_pos),"test_first_collaborations":len(test_pos),
      "candidate_pairs_after_train_cutoff":candidate_count,
      "limitations":["Retrospective snapshot; no proof of historical publication availability.",
       "First co-participation in funded projects is a collaboration proxy, not innovation success.",
       "Missing collaborations outside CORDIS; unlabeled pairs are not confirmed negatives.",
       "Historical organizations with changed identifiers can cause entity-resolution errors.",
       "Test candidate ranking must remove validation-era edges, and recompute historical features at the validation cutoff. This script exports labels only; it does not run evaluation."]}
    (out/"manifest.json").write_text(json.dumps(stats,indent=2),encoding="utf-8")
    return stats

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip",type=Path,help="Local official CORDIS CSV ZIP; if omitted download")
    p.add_argument("--out",type=Path,default=Path("data/processed"))
    p.add_argument("--train-end",default="2023-12-31")
    p.add_argument("--val-end",default="2024-12-31")
    p.add_argument("--test-end",default="2025-12-31")
    p.add_argument("--max-project-organizations",type=int,default=60)
    a=p.parse_args()
    dates=[date.fromisoformat(x) for x in (a.train_end,a.val_end,a.test_end)]
    if not dates[0] < dates[1] < dates[2]:p.error("Require train-end < val-end < test-end")
    archive=a.zip
    if archive is None:
        cache=Path("data/raw");cache.mkdir(parents=True,exist_ok=True)
        archive=cache/"cordis-HORIZONprojects-csv.zip"
        if not archive.exists():
            req=Request(SOURCE,headers={"User-Agent":"DBA-KBS-research/0.1 (academic reproducibility)"})
            with urlopen(req,timeout=120) as response,archive.open("wb") as dest:
                import shutil
                shutil.copyfileobj(response,dest)
    print(json.dumps(prepare(archive,a.out,*dates,a.max_project_organizations),indent=2))
if __name__=="__main__":main()
