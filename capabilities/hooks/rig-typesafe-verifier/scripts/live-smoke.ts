import { classifyAnswers, verifyStateLive } from "../src/extension";

const result = await verifyStateLive({
  request: "Report exactly what the observed test output proves.",
  response: "The observed output reports eight passing tests and zero failures.",
  evidence: [{ tool: "bun", text: "8 pass\n0 fail" }],
});
const decision = classifyAnswers(result.answers);
if (!result.model || Object.keys(result.answers).length !== 5) {
  throw new Error("live response did not satisfy the verifier contract");
}
console.log(`LIVE_SMOKE_PASS ${JSON.stringify({ model: result.model, decision, answers: result.answers })}`);
