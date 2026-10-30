module.exports = (output, context) => {
  const p = JSON.parse(output);
  const v = context.vars;
  const checks = [
    p.schema === 'rig.mission.v1',
    v.expected_status === 'any' || p.status === v.expected_status,
    p.execution.authorized === false,
    p.execution.outward_actions_authorized === false,
    p.execution.one_writer === true,
    p.memory.fallback_used === false,
    typeof p.packet_sha256 === 'string' && p.packet_sha256.length === 64,
    p.eval.promotion_ready === false,
    p.prompt_stack.task.status !== 'calibrated',
  ];
  if (v.expected_agent) checks.push(p.agent_stack.agent?.asset.id === v.expected_agent);
  if (v.expected_skill) checks.push(p.skills.some((s) => s.id === v.expected_skill));
  if (v.expected_child) checks.push(p.skills[1]?.id === v.expected_child);
  if (v.expected_status === 'abstain') checks.push(p.agent_stack.agent === null);
  if (p.status === 'candidate') {
    checks.push(p.skills.length === 2);
    checks.push(!p.blocks.includes('child_skill_unresolved'));
  }
  return { pass: checks.every(Boolean), score: checks.filter(Boolean).length / checks.length,
    reason: checks.every(Boolean) ? 'route contract satisfied' : `route contract failed: ${JSON.stringify({
      status: p.status, agent: p.agent_stack.agent?.asset.id, blocks: p.blocks,
    })}` };
};
