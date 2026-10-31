import copy
import importlib.util
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("allocation", ROOT / "scripts" / "allocate_costs.py")
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

class AllocationTests(unittest.TestCase):
    def model(self):
        return {"schema_version":"1.0", "currency":"INR", "currency_scale":100, "period":"test",
                "applications":[{"id":"a","direct_cost":7},{"id":"b","direct_cost":3},{"id":"c"}],
                "shared_pools":[{"id":"p","cost":11,"allocation_basis":"test","weights":{"a":"1","b":"1","c":"1"}}]}
    def test_rounding_conserves_amount_and_stable_ties(self):
        r=a.allocate(self.model())
        self.assertEqual(r["shared_pools"][0]["allocations"], {"a":4,"b":4,"c":3})
        self.assertEqual(r["totals"]["allocated_cost"],21)
        self.assertTrue(r["totals"]["reconciled"])
    def test_zero_weights_preserve_unallocated(self):
        m=self.model();m["shared_pools"][0]["weights"]={}
        r=a.allocate(m)
        self.assertEqual(r["totals"]["unallocated_cost"],11)
        self.assertEqual(r["totals"]["allocated_cost"],10)
    def test_invalid_inputs(self):
        for field,value in [("cost",True),("cost",-1),("weights",{"unknown":1}),("weights",{"a":"NaN"}),("weights",{"a":"-1"})]:
            m=self.model();m["shared_pools"][0][field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):a.allocate(m)
    def test_duplicate_application_rejected(self):
        m=self.model();m["applications"].append({"id":"a"})
        with self.assertRaises(ValueError):a.allocate(m)
    def test_large_exact_amount(self):
        m=self.model();m["shared_pools"][0]["cost"]=10**18+1
        r=a.allocate(m)
        self.assertEqual(sum(r["shared_pools"][0]["allocations"].values()),10**18+1)
    def test_zero_weight_never_gets_rounding_unit(self):
        m=self.model();m["shared_pools"][0]["cost"]=1;m["shared_pools"][0]["weights"]={"a":"0","b":"2","c":"1"}
        self.assertEqual(a.allocate(m)["shared_pools"][0]["allocations"],{"a":0,"b":1,"c":0})
    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(ValueError):a.unique_pairs([("cost",1),("cost",2)])

if __name__ == "__main__":unittest.main()
