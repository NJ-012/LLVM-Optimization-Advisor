import unittest
from src.features import extract
from src.config import BENCH,FEATURES
class FeatureTests(unittest.TestCase):
 def test_matrix_features(self):
  f=extract(BENCH/"matrix_multiply.c")
  for k in FEATURES: self.assertIn(k,f)
  self.assertGreater(f["ir_instruction_count"],0)
  self.assertGreater(f["source_loop_count"],0)
if __name__=="__main__": unittest.main()
