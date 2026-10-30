import importlib.util
from pathlib import Path
import json
import shutil
import tempfile
import unittest

ROOT=Path(__file__).parents[1]
spec=importlib.util.spec_from_file_location('verify_catalog',ROOT/'scripts/verify_catalog.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'family'
        shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns('__pycache__','*.pyc','proof','dist'))
        self.path=self.root/'config/meta-catalog.json'
        self.data=json.loads(self.path.read_text())

    def blocked(self):
        self.path.write_text(json.dumps(self.data))
        with self.assertRaises(ValueError):mod.verify(self.root)

    def test_twenty_complete_routers(self):
        self.assertEqual(mod.verify(self.root)['metaskills'],20)

    def test_missing_router(self):
        self.data['metaskills'].pop();self.blocked()

    def test_duplicate_id(self):
        self.data['metaskills'][1]['id']=self.data['metaskills'][0]['id'];self.blocked()

    def test_missing_step(self):
        self.data['metaskills'][0]['routes'][0]='steps/missing/SKILL.md';self.blocked()

    def test_escape_route(self):
        self.data['metaskills'][0]['routes'][0]='../outside/SKILL.md';self.blocked()

    def test_empty_source_provenance(self):
        self.data['metaskills'][0]['source_ids']=[];self.blocked()

    def test_unknown_source_provenance(self):
        self.data['metaskills'][0]['source_ids']=['invented-source'];self.blocked()

    def test_nominal_meta_with_one_route(self):
        self.data['metaskills'][0]['routes']=self.data['metaskills'][0]['routes'][:1];self.blocked()


if __name__=='__main__':unittest.main()
