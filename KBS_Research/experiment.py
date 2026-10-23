"""Reproducible link-prediction benchmark on Zachary's observed karate-club network.
NOT an entrepreneurial dataset: methodological feasibility only. Run: python experiment.py
"""
import csv, json
from pathlib import Path
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, average_precision_score
from scipy.stats import wilcoxon

OUT=Path(__file__).resolve().parent
SEEDS=range(30)
METHODS=('degree','common_neighbors','adamic_adar','community','hybrid')

def split_graph(seed):
    g=nx.karate_club_graph(); rng=np.random.default_rng(seed)
    edges=list(g.edges()); rng.shuffle(edges)
    train=nx.Graph(); train.add_nodes_from(g.nodes(data=True));train.add_edges_from(edges)
    hold=[]
    # Preserve connectivity, selecting a random non-bridge edge for each deletion.
    for u,v in edges:
        if len(hold)>=int(round(.2*g.number_of_edges())):break
        if not train.has_edge(u,v):continue
        train.remove_edge(u,v)
        if nx.is_connected(train):hold.append(tuple(sorted((u,v))))
        else:train.add_edge(u,v)
    positive=set(hold); rng=np.random.default_rng(seed+1000)
    pool=[(u,v) for u in train for v in train if u<v and not g.has_edge(u,v)]
    ids=rng.choice(len(pool),size=len(positive),replace=False)
    neg=[pool[i] for i in ids]
    return train,list(positive),neg

def score(g,pairs):
    community={}
    for idx,group in enumerate(nx.community.greedy_modularity_communities(g)):
        for node in group:community[node]=idx
    degrees=dict(g.degree())
    aa={(min(u,v),max(u,v)):s for u,v,s in nx.adamic_adar_index(g,pairs)}
    rows=[]
    for u,v in pairs:
        cn=len(list(nx.common_neighbors(g,u,v)))
        d=degrees[u]*degrees[v]
        a=aa[(min(u,v),max(u,v))]
        same=float(community[u]==community[v])
        # Predefined, untrained fusion; no label-derived weights.
        hybrid=a+0.8*same+0.15*cn
        rows.append(dict(degree=d,common_neighbors=cn,adamic_adar=a,community=same,hybrid=hybrid))
    return rows

def run():
    allrows=[]; first=None
    for seed in SEEDS:
        g,pos,neg=split_graph(seed)
        pairs=pos+neg; labels=np.array([1]*len(pos)+[0]*len(neg))
        pred=score(g,pairs)
        for m in METHODS:
            vals=np.array([p[m] for p in pred])
            allrows.append(dict(seed=seed,method=m,auc=roc_auc_score(labels,vals),ap=average_precision_score(labels,vals),n_positive=len(pos),n_negative=len(neg)))
        if seed==0:first=(g,pos)
    with open(OUT/'results.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
    summary={}
    for m in METHODS:
        sub=[r for r in allrows if r['method']==m]
        summary[m]={k:{'mean':float(np.mean([r[k] for r in sub])),'sd':float(np.std([r[k] for r in sub],ddof=1))} for k in ('auc','ap')}
    base=np.array([r['auc'] for r in allrows if r['method']=='adamic_adar'])
    hybrid=np.array([r['auc'] for r in allrows if r['method']=='hybrid'])
    delta=hybrid-base
    summary['paired_hybrid_vs_aa']={'mean_delta_auc':float(delta.mean()),'wilcoxon_p_two_sided':float(wilcoxon(delta).pvalue) if np.any(delta) else 1.,'bootstrap_ci_95':list(map(float,np.quantile([np.mean(np.random.default_rng(i).choice(delta,size=len(delta),replace=True)) for i in range(2000)],[.025,.975])))}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2))
    g,pos=first
    fig,ax=plt.subplots(figsize=(9,5.4)); layout=nx.spring_layout(g,seed=7)
    groups={n:dat['club'] for n,dat in g.nodes(data=True)}
    colors=['#2675a6' if groups[n]=='Mr. Hi' else '#e4a23b' for n in g]
    nx.draw_networkx_nodes(g,layout,node_size=190,node_color=colors,ax=ax,edgecolors='white',linewidths=.5)
    nx.draw_networkx_edges(g,layout,edge_color='#c0cbd5',width=.9,ax=ax)
    nx.draw_networkx_edges(g,layout,edgelist=pos,edge_color='#c94343',width=1.9,style='dashed',ax=ax)
    ax.set_title('Observed network and withheld positive ties (seed 0)');ax.axis('off');fig.tight_layout();fig.savefig(OUT/'Figure_1.png',dpi=350);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5.2));x=np.arange(len(METHODS));means=[summary[m]['auc']['mean'] for m in METHODS];sds=[summary[m]['auc']['sd'] for m in METHODS]
    ax.bar(x,means,yerr=sds,capsize=4,color=['#71869a']*4+['#2675a6']);ax.set_xticks(x,('Degree','Common neighbors','Adamic–Adar','Community','Hybrid'));ax.set_ylabel('ROC AUC (mean ± SD; 30 splits)');ax.set_ylim(0,1.03);ax.set_title('Held-out edge discrimination on observed social network');fig.tight_layout();fig.savefig(OUT/'Figure_2.png',dpi=350);plt.close(fig)
    print(json.dumps(summary,indent=2))
if __name__=='__main__':run()
