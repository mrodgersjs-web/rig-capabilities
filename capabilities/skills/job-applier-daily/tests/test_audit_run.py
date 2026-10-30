"""Synthetic negative tests. No fixture is an authentic application or approval."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('audit_run', Path(__file__).parents[1] / 'scripts/audit_run.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.packet = self.fixture()

    def put(self, name, value):
        raw = json.dumps(value, sort_keys=True).encode()
        (self.root / name).write_bytes(raw)
        return {'path': name, 'sha256': hashlib.sha256(raw).hexdigest()}

    def fixture(self):
        target = dict(candidate_id='SYNTHETIC', employer_id='EXAMPLE', requisition_id='TEST-1', official_url='https://example.invalid/jobs/1', title='Test role')
        p = dict(schema='job-applier-daily.packet.v1', stage='ready', target=target,
                 job_key=mod.job_key('SYNTHETIC', 'EXAMPLE', 'TEST-1'), tracker=mod.TRACKER,
                 artifacts={k:self.put(k+'.json', {'synthetic':k}) for k in (*mod.DOCUMENTS, 'jd','persona','requirements','page1','page2')},
                 rendered_pages=['page1','page2'], form_answers={'synthetic':'not for use'},
                 destination='https://example.invalid/apply', submission_state='not_attempted')
        text = 'Synthetic claim, never for real use.'
        confirm = self.put('claim-confirmation.json', dict(claim_id='x',claim_sha256=mod.digest(text),participated=True,include=True,
                          actor='synthetic',source_message_id='synthetic',employer='EXAMPLE',dates='test',personal_action='test',result='test'))
        p['claims'] = [dict(id='x',text=text,status='confirmed',included=True,confirmation=confirm,sources=[self.put('source.json', {'synthetic':True})])]
        p['binding'] = mod.digest({k:p[k] for k in ('job_key','target','artifacts','rendered_pages','form_answers','destination','claims')})
        b=p['binding']
        p['steps']=[{'id':k,'receipt':self.put('step-'+k+'.json',dict(step=k,binding=b,status='PASS',can_advance=True,decision_id='synthetic',request_id='synthetic'))} for k in mod.STEPS]
        p['quality_receipt']=self.put('quality.json',dict(binding=b,status='PASS',can_advance=True,decision_id='synthetic',request_id='synthetic',image_decision_id='synthetic',image_page_artifacts=p['rendered_pages'],criteria=[dict(id=f'c{i:02d}',status='PASS') for i in range(1,16)]))
        p['tracker_receipt']=self.put('tracker.json',dict(tracker=mod.TRACKER,job_key=p['job_key'],schema_verified=True,full_table_scan_complete=True,matching_record_count=1,write_readback=True,record_id='synthetic',schema_sha256='synthetic',binding=b,prior_submission=False,field_map_valid=True,status_map_valid=True))
        p['approvals']={k:self.put('approval-'+k+'.json',dict(kind=k,binding=b,approved=True,actor='synthetic',source_message_id='synthetic')) for k in ('facts','pages','submission')}
        return p

    def run_packet(self):
        path=self.root/'packet.json'
        path.write_text(json.dumps(self.packet))
        try:
            return mod.audit(path)
        except (ValueError,OSError,TypeError,KeyError,AttributeError) as exc:
            return {'status':'BLOCK','errors':[str(exc)],'authorizes_submission':False}

    def change(self,key,**changes):
        ref=self.packet[key]
        value=json.loads((self.root/ref['path']).read_text())
        value.update(changes)
        self.packet[key]=self.put(ref['path'],value)

    def blocked(self):
        self.assertEqual(self.run_packet()['status'],'BLOCK')

    def rebind(self):
        p=self.packet
        p['binding']=mod.digest({k:p[k] for k in ('job_key','target','artifacts','rendered_pages','form_answers','destination','claims')})
        for ref in [s['receipt'] for s in p['steps']]+[p['quality_receipt'],p['tracker_receipt']]+list(p['approvals'].values()):
            value=json.loads((self.root/ref['path']).read_text())
            value['binding']=p['binding']
            ref.update(self.put(ref['path'],value))

    def test_consistent_forged_records_are_never_authorization(self):
        result=self.run_packet()
        self.assertEqual(result['status'],'STRUCTURAL_PASS')
        self.assertFalse(result['authorizes_submission'])
        self.assertIn('authenticate',result['scope'])

    def test_artifact_tamper(self):
        (self.root/'resume_docx.json').write_text('changed')
        self.blocked()

    def test_empty_evidence_even_with_fresh_hash(self):
        (self.root/'resume_docx.json').write_bytes(b'')
        self.packet['artifacts']['resume_docx']['sha256']=hashlib.sha256(b'').hexdigest()
        self.rebind()
        self.blocked()

    def test_stale_cover_letter(self):
        self.packet['artifacts']['cover_letter_docx']=self.put('cover_letter_docx.json',{'updated':True})
        self.blocked()

    def test_missing_cover_letter(self):
        del self.packet['artifacts']['cover_letter_docx']
        self.blocked()

    def test_unconfirmed_included_claim(self):
        self.packet['claims'][0]['status']='unconfirmed'
        self.rebind()
        self.blocked()

    def test_include_does_not_prove_participation(self):
        c=self.packet['claims'][0]
        r=json.loads((self.root/c['confirmation']['path']).read_text())
        r['participated']=False
        c['confirmation']=self.put('claim-confirmation.json',r)
        self.rebind()
        self.blocked()

    def test_participation_does_not_override_omit(self):
        c=self.packet['claims'][0]
        r=json.loads((self.root/c['confirmation']['path']).read_text())
        r['include']=False
        c['confirmation']=self.put('claim-confirmation.json',r)
        self.rebind()
        self.blocked()

    def test_empty_ledger_even_with_fresh_bindings(self):
        self.packet['claims']=[]
        self.rebind()
        self.blocked()

    def test_string_included_cannot_bypass_confirmation(self):
        c=self.packet['claims'][0]
        c['included']='true'
        c['status']='unconfirmed'
        del c['confirmation']
        self.rebind()
        self.blocked()

    def test_duplicate_claim_ids_even_with_fresh_bindings(self):
        self.packet['claims'].append(copy.deepcopy(self.packet['claims'][0]))
        self.rebind()
        self.blocked()

    def test_empty_claim_text_even_with_fresh_bindings(self):
        self.packet['claims'][0]['text']=' '
        self.rebind()
        self.blocked()

    def test_omitted_only_ledger_is_not_ready(self):
        self.packet['claims'][0].update(included=False,status='omitted')
        self.rebind()
        self.blocked()

    def test_unknown_submission_state(self):
        self.packet['submission_state']='invented_state'
        self.blocked()

    def test_stage_state_mismatch(self):
        self.packet['stage']='ready'
        self.packet['submission_state']='receipt_verified'
        self.blocked()

    def test_view_only_dedupe_fails(self):
        self.change('tracker_receipt',full_table_scan_complete=False)
        self.blocked()

    def test_duplicate_tracker_record(self):
        self.change('tracker_receipt',matching_record_count=2)
        self.blocked()

    def test_already_applied(self):
        self.change('tracker_receipt',prior_submission=True)
        self.blocked()

    def test_unread_tracker_write(self):
        self.change('tracker_receipt',write_readback=False)
        self.blocked()

    def test_changed_airtable_schema(self):
        self.change('tracker_receipt',field_map_valid=False)
        self.blocked()

    def test_wrong_base(self):
        self.packet['tracker']={**mod.TRACKER,'base':'wrong'}
        self.blocked()

    def test_contradictory_jev(self):
        self.change('quality_receipt',can_advance=False)
        self.blocked()

    def test_missing_jev_id(self):
        self.change('quality_receipt',decision_id=None)
        self.blocked()

    def test_stale_page_review(self):
        self.change('quality_receipt',image_page_artifacts=['page1'])
        self.blocked()

    def test_empty_criteria(self):
        self.change('quality_receipt',criteria=[])
        self.blocked()

    def test_missing_step(self):
        self.packet['steps'].pop()
        self.blocked()

    def test_generic_approval_not_submission_approval(self):
        self.packet['approvals'].pop('submission')
        self.blocked()

    def test_changed_answers(self):
        self.packet['form_answers']['extra']='new'
        self.blocked()

    def test_uncertain_submit(self):
        self.packet['submission_state']='unknown'
        self.blocked()

    def test_submitted_without_receipt(self):
        self.packet['stage']='submitted'
        self.blocked()

    def test_symlink_evidence(self):
        src=self.root/'resume_docx.json'
        src.unlink()
        src.symlink_to(self.root/'master_docx.json')
        self.blocked()

    def test_alias_case_identity_normalization(self):
        self.assertEqual(mod.job_key(' A ',' B ',' C '),mod.job_key('a','b','c'))
        self.assertNotEqual(mod.job_key('a','b','c'),mod.job_key('a','b','d'))


if __name__=='__main__':
    unittest.main()
