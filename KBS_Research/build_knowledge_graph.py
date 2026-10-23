"""Build a typed, dated organization-project graph from an official CORDIS ZIP.

This is a reproducible *bipartite* knowledge graph: organization --participates_in-->
project, with project start dates. No labels or features from future projects
are included in a historical snapshot. It does not establish publication dates.
"""
import argparse
import csv
import json
import zipfile
from collections import defaultdict
from datetime import date
from pathlib import Path
from prepare_cordis import field, parse_date, rows_from_zip

def export_graph(archive, output, cutoff, max_project_orgs=60):
    output.mkdir(parents=True,exist_ok=True)
    projects={}
    with zipfile.ZipFile(archive) as z:
        for r in rows_from_zip(z,"project.csv"):
            pid=field(r,"id","projectID","projectId")
            start=parse_date(field(r,"startDate","start_date"))
            if pid and start and start<=cutoff:
                projects[pid]=start
        members=defaultdict(set)
        for r in rows_from_zip(z,"organization.csv"):
            pid=field(r,"projectID","projectId","project_id")
            oid=field(r,"organisationID","organizationID","organisationId","organizationId")
            if pid in projects and oid:members[pid].add(oid)
    retained={pid:sorted(orgs) for pid,orgs in members.items() if 2<=len(orgs)<=max_project_orgs}
    with (output/"kg_nodes.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f);w.writerow(("node_id","node_type","start_date"))
        for org in sorted({o for group in retained.values() for o in group}):
            w.writerow(("org:"+org,"organization",""))
        for pid in sorted(retained):
            w.writerow(("project:"+pid,"project",projects[pid].isoformat()))
    with (output/"kg_edges.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f);w.writerow(("source","relation","target","event_date"))
        for pid in sorted(retained):
            for org in retained[pid]:
                w.writerow(("org:"+org,"participates_in","project:"+pid,projects[pid].isoformat()))
    stats={"cutoff":cutoff.isoformat(),"projects":len(retained),
           "organizations":len({o for group in retained.values() for o in group}),
           "participation_edges":sum(map(len,retained.values())),
           "note":"Current retrospective archive, dated by project start, not historical disclosure."}
    (output/"kg_manifest.json").write_text(json.dumps(stats,indent=2),encoding="utf-8")
    return stats

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip",type=Path,default=Path("data/raw/cordis-HORIZONprojects-csv.zip"))
    p.add_argument("--out",type=Path,default=Path("data/kg_2023"))
    p.add_argument("--cutoff",default="2023-12-31")
    p.add_argument("--max-project-organizations",type=int,default=60)
    a=p.parse_args()
    print(json.dumps(export_graph(a.zip,a.out,date.fromisoformat(a.cutoff),a.max_project_organizations),indent=2))
if __name__=="__main__":main()
