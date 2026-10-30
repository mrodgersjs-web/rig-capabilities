import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('jev_step',Path(__file__).parents[1]/'scripts/jev_step.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)


class JevStepTests(unittest.TestCase):
    def response(self,v):return {'model':'synthetic','answers':{k:{'type':'noul','noul':v} for k in mod.QUESTIONS}}
    def test_typed_values(self):self.assertEqual(len(mod.parse(self.response(.95))),2)
    def test_boolean_is_not_probability(self):
        with self.assertRaises(ValueError):mod.parse(self.response(True))
    def test_nan_fails(self):
        with self.assertRaises(ValueError):mod.parse(self.response(float('nan')))
    def test_out_of_range_fails(self):
        with self.assertRaises(ValueError):mod.parse(self.response(2))
    def test_empty_response_fails(self):
        with self.assertRaises(ValueError):mod.parse({})
    def test_missing_question_fails(self):
        r=self.response(.95);r['answers'].pop(next(iter(mod.QUESTIONS)))
        with self.assertRaises(ValueError):mod.parse(r)
    def test_empty_model_fails(self):
        r=self.response(.95);r['model']=' '
        with self.assertRaises(ValueError):mod.parse(r)
    def test_malformed_answers_fails(self):
        r=self.response(.95);r['answers']='PASS'
        with self.assertRaises(ValueError):mod.parse(r)
    def test_malformed_answer_fails(self):
        r=self.response(.95);r['answers'][next(iter(mod.QUESTIONS))]=True
        with self.assertRaises(ValueError):mod.parse(r)
    def context(self):return dict(hosted_authorized=True,redaction_reviewed=True,binding='a'*64,meta_id='full-persona',evidence={'synthetic':True},report='Synthetic review.',redactions=[])
    def test_valid_context(self):mod.validate_context(self.context())
    def test_malformed_context_fields_fail_before_transport(self):
        for key,value in [('binding','synthetic'),('binding',7),('evidence',True),('evidence',' '),('report',[]),('report',' '),('redactions','name'),('redactions',[3]),('hosted_authorized','true'),('meta_id',None)]:
            with self.subTest(key=key,value=value):
                c=self.context();c[key]=value
                with self.assertRaises(ValueError):mod.validate_context(c)
    def test_missing_redaction_inspection_list_fails(self):
        c=self.context();del c['redactions']
        with self.assertRaises(ValueError):mod.validate_context(c)


if __name__=='__main__':unittest.main()
