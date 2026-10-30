import {readFile,writeFile,realpath,stat} from 'node:fs/promises';
import {resolve,relative,isAbsolute} from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
export const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const iso = s => typeof s==='string' && /^\d{4}-\d\d-\d\dT/.test(s) && Number.isFinite(Date.parse(s));
async function bound(root,binding) {
  if (!binding || typeof binding.path!=='string' || !/^[a-f0-9]{64}$/.test(binding.sha256)) throw Error('INVALID_BINDING');
  const base=await realpath(root), target=await realpath(resolve(base,binding.path));
  const rel=relative(base,target);
  if (rel==='..' || rel.startsWith('../') || isAbsolute(rel)) throw Error('PATH_ESCAPE');
  if (!(await stat(target)).isFile()) throw Error('NOT_FILE');
  const bytes=await readFile(target);
  if (!bytes.length) throw Error('EMPTY_ARTIFACT');
  if (sha(bytes)!==binding.sha256) throw Error('SHA_MISMATCH');
  return bytes;
}
export async function verify(r,root,policy={}) {
  const reasons=[];
  if (!r || r.schema!=='rig.receipt.guard.v1' || !iso(r.observed_at) || typeof r.run_id!=='string') reasons.push('INVALID_RECEIPT');
  if (!Array.isArray(r?.artifacts) || !r.artifacts.length) reasons.push('NO_ARTIFACTS');
  for(const b of r?.artifacts??[]) {try {await bound(root,b);} catch(e){reasons.push(e.code==='ENOENT'?'MISSING_ARTIFACT':e.message);}}
  const artifactReasons=[...reasons];
  if (r?.execution?.state!=='complete' || r?.execution?.exit_code!==0) reasons.push('EXECUTION_NOT_COMPLETE');
  const a=r?.acceptance;
  if (a?.state!=='accepted') reasons.push('ACCEPTANCE_NOT_RECORDED');
  else {
    if (!iso(a.observed_at) || !a.verifier || a.verifier===r.producer) reasons.push('INDEPENDENT_VERIFIER_REQUIRED');
    try {
      const e=JSON.parse((await bound(root,a.evidence)).toString());
      if(e.verdict!=='accepted' || e.run_id!==r.run_id || e.test_filter!==r.test_filter || JSON.stringify(e.artifacts)!==JSON.stringify(r.artifacts)) reasons.push('ACCEPTANCE_SCOPE_MISMATCH');
    } catch(e){reasons.push(e.code==='ENOENT'?'MISSING_ACCEPTANCE_EVIDENCE':e.message);}
  }
  if (policy.required_filter && r?.test_filter!==policy.required_filter) reasons.push('TEST_FILTER_MISMATCH');
  // Websites always require human jury, even if a receipt tries to disable the requirement.
  if (r?.kind==='website' || policy.require_human_jury===true) {
    try {
      const j=JSON.parse((await bound(root,a?.jury)).toString());
      if(j.mode!=='human' || j.verdict!=='accepted' || !Array.isArray(j.seats) || !j.seats.length || j.seats.some(s=>!s.name || s.vote!=='accept') || j.run_id!==r.run_id || JSON.stringify(j.artifacts)!==JSON.stringify(r.artifacts)) reasons.push('HUMAN_JURY_INVALID');
    } catch(e){reasons.push('HUMAN_JURY_NOT_RUN');}
  }
  return {status:reasons.length?'BLOCKED':'ACCEPTED', reasons:[...new Set(reasons)], execution_complete:r?.execution?.state==='complete' && r?.execution?.exit_code===0, artifact_verified:artifactReasons.length===0, quality_accepted:reasons.length===0, runtime_loaded:'UNVERIFIED', external_outcome:'UNVERIFIED', observed_at:r?.observed_at, checked_at:new Date().toISOString(), fixture:r?.fixture===true};
}
export async function saveOriginal(path,receipt) {
  if (!iso(receipt?.observed_at)) throw Error('INVALID_OBSERVATION_TIME');
  // Exclusive creation. Reruns do not update receipts or original observation times.
  await writeFile(path,JSON.stringify(receipt,null,2)+'\n',{flag:'wx'});
}
if (process.argv[1] && import.meta.url===pathToFileURL(resolve(process.argv[1])).href) {
  try {const r=JSON.parse(await readFile(process.argv[2],'utf8')); const policy=process.argv[4]?JSON.parse(await readFile(process.argv[4],'utf8')):{}; const out=await verify(r,process.argv[3],policy); console.log(JSON.stringify(out,null,2)); process.exitCode=out.status==='ACCEPTED'?0:2;}
  catch(e){console.log(JSON.stringify({status:'BLOCKED',reasons:[e.message]}));process.exitCode=2;}
}
