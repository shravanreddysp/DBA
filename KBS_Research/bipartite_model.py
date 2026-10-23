"""Historical bipartite participation signal for matched-pool collaboration ranking.

Uses project membership as of each cutoff, with no future labels in features.
The shared-project-neighbor signal is exploratory, not a validated novel method.
"""
import math
from collections import defaultdict

def historical_context(projects, memberships, cutoff, known, max_orgs=60):
    org_projects=defaultdict(set)
    project_orgs={}
    for pid, members in memberships.items():
        if projects[pid] > cutoff:
            continue
        members=set(members)&known
        if not 2 <= len(members) <= max_orgs:
            continue
        project_orgs[pid]=members
        for org in members:
            org_projects[org].add(pid)
    return org_projects,project_orgs

def bipartite_score(source,target,org_projects,project_orgs):
    """Degree-discounted paths org -> project -> org -> project -> org.

    The intermediate organization is not allowed to be source or target.
    Each distinct historical project pair contributes a capped inverse-size
    term, reducing the influence of large consortia.
    """
    if source==target:
        return 0.0
    source_projects=org_projects.get(source,())
    target_projects=org_projects.get(target,())
    if not source_projects or not target_projects:
        return 0.0
    intermediary=defaultdict(float)
    for pid in source_projects:
        group=project_orgs[pid]
        scale=1.0/max(1,len(group)-1)
        for org in group:
            if org!=source and org!=target:
                intermediary[org]+=scale
    score=0.0
    for pid in target_projects:
        group=project_orgs[pid]
        scale=1.0/max(1,len(group)-1)
        for org in group:
            if org!=source and org!=target and org in intermediary:
                score+=intermediary[org]*scale/math.log1p(len(org_projects[org])+1)
    return score
