import { classifyAnswers, type VerificationAnswers } from "../src/extension";

const clean: VerificationAnswers = {
  unsupported_factual_claim: 0.04,
  contradicts_evidence: 0.02,
  overstates_completion: 0.03,
  fabricated_citation_or_path: 0.01,
  uncertainty_presented_as_fact: 0.05,
};

const planted = classifyAnswers({ ...clean, unsupported_factual_claim: 0.92 });
if (planted.verdict !== "review" || planted.trigger !== "unsupported_factual_claim") {
  throw new Error(`PLANT_FAILED ${JSON.stringify(planted)}`);
}
console.log(`PLANT_RED unsupported_factual_claim -> ${planted.verdict}`);

const restored = classifyAnswers(clean);
if (restored.verdict !== "pass") throw new Error(`RESTORE_FAILED ${JSON.stringify(restored)}`);
console.log(`RESTORE_GREEN clean_evidence -> ${restored.verdict}`);
