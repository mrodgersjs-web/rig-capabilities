import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('validator', Path(__file__).parents[1] / 'scripts/validate_packet.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.artifacts = {}
        self.target = dict(company='Example', role='Operations Director', id='123', url='https://example.test/jobs/123')
        self.put('jd', 'Lead operations. Requires degree. Hybrid Denver.')
        self.binding = dict(target=self.target, jd_sha256=self.artifacts['jd']['sha256'])
        self.ids = ['r1', 'r2', 'r3']
        self.coverage = self.put('coverage', dict(status='PASS', requirement_ids=self.ids, jd_sha256=self.binding['jd_sha256']))
        self.inventory = dict(**self.binding, requirements=[dict(id=i,kind=k,jd_quote=q) for i,k,q in zip(self.ids,['responsibility','minimum','constraint'],['Lead operations.','Requires degree.','Hybrid Denver.'])],coverage_review=dict(requirement_ids=self.ids,receipt=self.coverage))
        self.put('inventory',self.inventory)
        self.persona = dict(**self.binding,kind='role_research_not_candidate_facts',requirement_ids=self.ids)
        for field in v.PERSONA_FIELDS:
            self.persona[field] = [dict(text='Role-specific expectation for '+field,basis='inference',source_ids=['jd'])]
        self.put('persona',self.persona)
        self.review = dict(status='PASS',decision_id='test-only-je v'.replace(' ',''),**{k:self.artifacts[n]['sha256'] for k,n in [('jd_sha256','jd'),('persona_sha256','persona'),('inventory_sha256','inventory')]})
        self.review['provider_response'] = self.put('provider',copy.deepcopy(self.review))
        self.put('persona_review',self.review)
        self.bank = dict(**self.binding,persona_sha256=self.artifacts['persona']['sha256'],examples=[dict(id='e'+str(n),requirement_ids=[i],result='Illustrative result '+i,personal_action='Ideal action '+i,strategy='Ideal strategy '+i,status='hypothetical_not_candidate_fact') for n,i in enumerate(self.ids)])
        self.put('achievement_bank',self.bank)
        self.alignment = dict(**self.binding,persona_sha256=self.artifacts['persona']['sha256'],achievement_bank_sha256=self.artifacts['achievement_bank']['sha256'],claims=[dict(id='c'+str(n),example_id='e'+str(n),requirement_ids=[i],status='unconfirmed',origin='hypothetical') for n,i in enumerate(self.ids)])
        self.put('alignment',self.alignment)
        for name in ('red_docx','clean_docx'):
            path=self.root/(name+'.docx')
            with zipfile.ZipFile(path,'w') as z:
                z.writestr('[Content_Types].xml','<Types/>')
                z.writestr('word/document.xml','<document/>')
            self.artifacts[name]=dict(path=path.name,sha256=v.sha(path))
        self.put('changes',dict(changes=['role-specific summary and experience']))
        self.packet = dict(target=self.target,stage='working',tailoring_status='complete',artifacts=self.artifacts)

    def put(self,name,body):
        path=self.root/(name+'.json' if not isinstance(body,str) else name+'.txt')
        path.write_text(json.dumps(body) if not isinstance(body,str) else body)
        reference=dict(path=path.name,sha256=v.sha(path))
        self.artifacts[name]=reference
        return reference

    def seal(self):
        logs=[]
        count={'persona':2,'working':5,'final':7,'submitted':8}[self.packet['stage']]
        for i,step in enumerate(v.STEPS[:count]):
            names=['jd','inventory']+v.OUTPUTS[i]+(['persona'] if i>=1 else [])
            bindings={n:self.artifacts[n]['sha256'] for n in names if n in self.artifacts}
            response=self.put('response-'+step,dict(step=step,artifact_hashes=bindings))
            receipt=self.put('receipt-'+step,dict(step=step,command_or_tool='fixture only',started_at='2026-10-29T00:00:00Z',completed_at='2026-10-29T00:01:00Z',artifact_hashes=bindings,response_artifact=response))
            logs.append(dict(step=step,leaf='steps/'+step+'/SKILL.md',artifact_hashes=bindings,execution_receipt=receipt))
        self.packet['step_log']=logs
        return self.write()

    def write(self):
        path=self.root/'packet.json';path.write_text(json.dumps(self.packet));return path

    def verdict(self):
        try: return v.validate(self.write())['status']
        except (ValueError,KeyError,TypeError,zipfile.BadZipFile): return 'BLOCK'

    def test_valid_working(self):
        self.seal();self.assertEqual(self.verdict(),'STRUCTURALLY_VALID')

    def test_persona_checkpoint_needs_no_future_steps(self):
        self.packet['stage']='persona'
        for n in ('achievement_bank','alignment','red_docx','clean_docx','changes'): self.artifacts.pop(n)
        self.seal();self.assertEqual(self.verdict(),'STRUCTURALLY_VALID')

    def test_missing_persona_flag_cannot_substitute(self):
        self.artifacts.pop('persona');self.packet['persona_complete']=True
        self.assertEqual(self.verdict(),'BLOCK')

    def test_incomplete_persona(self):
        self.persona['industry_economics']=[];self.put('persona',self.persona);self.seal()
        self.assertEqual(self.verdict(),'BLOCK')

    def test_missing_requirement_coverage(self):
        self.bank['examples'].pop();self.put('achievement_bank',self.bank);self.seal()
        self.assertEqual(self.verdict(),'BLOCK')

    def test_invented_jd_quote(self):
        self.inventory['requirements'][0]['jd_quote']='Invented duty'
        self.put('inventory',self.inventory);self.seal();self.assertEqual(self.verdict(),'BLOCK')

    def test_stale_jd(self):
        self.put('jd','Different role requires relocation.');self.seal();self.assertEqual(self.verdict(),'BLOCK')

    def test_stale_persona(self):
        self.persona['mandate'][0]['text']='Changed mandate';self.put('persona',self.persona)
        self.seal();self.assertEqual(self.verdict(),'BLOCK')

    def test_skipped_leaf(self):
        self.seal();self.packet['step_log'].pop(1);self.assertEqual(self.verdict(),'BLOCK')

    def test_hypothetical_promoted(self):
        self.alignment['claims'][0]['status']='confirmed';self.put('alignment',self.alignment)
        self.seal();self.assertEqual(self.verdict(),'BLOCK')

    def make_final(self):
        self.packet['stage']='final'
        page=self.put('page','synthetic image fixture, not real visual evidence')
        self.put('images',dict(docx_sha256=self.artifacts['clean_docx']['sha256'],pages=[page]))
        human=self.put('human','synthetic omit decisions and page approval')
        self.confirmations=dict(decisions={c['id']:dict(action='omit',human_response=human) for c in self.alignment['claims']},page_approval=dict(docx_sha256=self.artifacts['clean_docx']['sha256'],images_sha256=self.artifacts['images']['sha256'],human_response=human))
        self.put('confirmations',self.confirmations)
        quality=dict(status='PASS',decision_id='synthetic-quality',criteria_ids=list(range(1,16)))
        for n in ('jd','persona','clean_docx','images','alignment','confirmations'):
            quality[n+'_sha256']=self.artifacts[n]['sha256']
        quality['jev_receipt']=self.put('quality-provider',copy.deepcopy(quality))
        self.put('quality',quality)
        self.seal()

    def test_valid_final_structure_only(self):
        self.make_final();self.assertEqual(self.verdict(),'STRUCTURALLY_VALID')

    def test_missing_final_image_approval(self):
        self.make_final();self.confirmations.pop('page_approval')
        self.put('confirmations',self.confirmations);self.seal();self.assertEqual(self.verdict(),'BLOCK')

    def test_old_quality_after_document_change(self):
        self.make_final()
        path=self.root/self.artifacts['clean_docx']['path']
        with zipfile.ZipFile(path,'a') as z:z.writestr('word/new-part.xml','<changed/>')
        self.artifacts['clean_docx']['sha256']=v.sha(path)
        self.seal();self.assertEqual(self.verdict(),'BLOCK')

    def test_empty_provider_response(self):
        self.review['provider_response']=self.put('provider',{})
        self.put('persona_review',self.review);self.seal();self.assertEqual(self.verdict(),'BLOCK')

    def test_empty_coverage_receipt(self):
        self.inventory['coverage_review']['receipt']=self.put('coverage',{})
        self.put('inventory',self.inventory);self.seal();self.assertEqual(self.verdict(),'BLOCK')

    def test_empty_execution_response(self):
        self.seal()
        log=self.packet['step_log'][0]
        path=self.root/log['execution_receipt']['path'];receipt=json.loads(path.read_text())
        receipt['response_artifact']=self.put('response-posting-inventory',{})
        log['execution_receipt']=self.put('receipt-posting-inventory',receipt)
        self.assertEqual(self.verdict(),'BLOCK')

    def test_non_word_artifact(self):
        self.put('red_docx',{});self.seal();self.assertEqual(self.verdict(),'BLOCK')

    def test_duplicate_claims(self):
        self.alignment['claims'][1]['id']=self.alignment['claims'][0]['id']
        self.put('alignment',self.alignment);self.seal();self.assertEqual(self.verdict(),'BLOCK')

    def test_generic_semantic_hold(self):
        self.review['status']='BLOCK';self.review['provider_response']=self.put('provider',{k:val for k,val in self.review.items() if k!='provider_response'})
        self.put('persona_review',self.review);self.seal();self.assertEqual(self.verdict(),'BLOCK')

    def test_duplicate_examples(self):
        for k in ('result','personal_action','strategy'): self.bank['examples'][1][k]=self.bank['examples'][0][k]
        self.put('achievement_bank',self.bank);self.seal();self.assertEqual(self.verdict(),'BLOCK')

    def test_source_only_cannot_complete(self):
        self.packet['source_only_recovery']=True;self.seal();self.assertEqual(self.verdict(),'BLOCK')


if __name__=='__main__': unittest.main()
