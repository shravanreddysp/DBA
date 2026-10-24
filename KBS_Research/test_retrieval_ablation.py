import unittest
from retrieval_ablation import candidates

class RetrievalAblationTests(unittest.TestCase):
    def test_fixed_budget_and_no_existing_neighbors(self):
        known=set('ABCDEFG')
        adj={n:set() for n in known}
        adj['A']={'B','C'}
        adj['B']={'A','D','E'}
        adj['C']={'A','E','F'}
        adj['D']={'B'}
        adj['E']={'B','C'}
        adj['F']={'C'}
        degree={n:len(adj[n]) for n in known}
        for strategy in ('degree_twohop','shared_twohop','resource_twohop','random','degree_global'):
            result=candidates('A',known,adj,degree,11,strategy,budget=3)
            self.assertEqual(len(result),3)
            self.assertFalse(result & {'A','B','C'})
            self.assertEqual(result,candidates('A',known,adj,degree,11,strategy,budget=3))
    def test_budget_larger_than_eligible(self):
        known={'A','B','C'}
        adj={'A':{'B'},'B':{'A'},'C':set()}
        degree={n:len(adj[n]) for n in known}
        self.assertEqual(candidates('A',known,adj,degree,11,'random',budget=10),{'C'})

if __name__=='__main__':unittest.main()
