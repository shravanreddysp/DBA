import unittest
from datetime import date
from bipartite_model import historical_context,bipartite_score

class BipartiteModelTests(unittest.TestCase):
    def test_historical_two_project_path(self):
        projects={'p1':date(2023,1,1),'p2':date(2023,2,1),'future':date(2025,1,1)}
        members={'p1':{'a','b'},'p2':{'b','c'},'future':{'a','c'}}
        op,po=historical_context(projects,members,date(2023,12,31),{'a','b','c'})
        self.assertGreater(bipartite_score('a','c',op,po),0)
        self.assertEqual(bipartite_score('a','b',op,po),0)
        self.assertNotIn('future',po)
    def test_no_future_only_signal(self):
        op,po=historical_context({'p':date(2025,1,1)},{'p':{'a','b'}},date(2023,12,31),{'a','b'})
        self.assertEqual(bipartite_score('a','b',op,po),0)

if __name__=='__main__':
    unittest.main()
