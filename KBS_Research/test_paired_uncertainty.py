import unittest
from paired_uncertainty import interval

class PairedTests(unittest.TestCase):
    def test_deduplicates_overlapping_sources(self):
        q={'query_key':'x','positives':2,'hits':{'kg':1,'aa':0}}
        data={'test':[{'per_query':[q]},{'per_query':[q]}]}
        result=interval(data,'aa',draws=100)
        self.assertEqual(result['unique_queries_with_positives'],1)
        self.assertEqual(result['kg_minus_baseline'],0.5)
    def test_requires_positive_labels(self):
        with self.assertRaises(ValueError):
            interval({'test':[{'per_query':[]}]},'aa',draws=100)

if __name__=='__main__': unittest.main()
