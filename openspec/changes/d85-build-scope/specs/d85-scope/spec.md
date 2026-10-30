## ADDED Requirements

### Requirement: Ordinary authorized work remains available

D85 SHALL NOT deny ordinary pre-tool calls based on production-directory membership, unknown shell verbs, missing admissions, or use of Python. Other active-loop and authorization checks SHALL remain effective.

#### Scenario: No build is active
- **WHEN** an agent requests a startup, memory, shell, Python, read, or edit operation
- **THEN** the D85 layer permits the request without requiring build certification

#### Scenario: An active loop requires Gate-D
- **WHEN** an outward action is requested without the loop's required approval
- **THEN** the existing Gate-D policy denies the action

#### Scenario: D85 is unavailable during ordinary work
- **WHEN** the D85 admission module cannot be loaded
- **THEN** ordinary work remains available through the normal loop policy

### Requirement: D85 advises and repair remains available

D85 SHALL keep its session and turn checks active as advisory guidance. A RED or unavailable D85 check SHALL withhold certification while allowing ordinary work and remediation. The agent SHALL fix reachable findings and report the applied changes plus any remaining certification gaps.

#### Scenario: D85 reports RED during work
- **WHEN** the advisory check reports missing, stale, or failing evidence
- **THEN** the agent can continue using tools to repair the issue
- **AND** the build remains uncertified until the explicit certification gate passes

#### Scenario: Repair work completes
- **WHEN** the agent has addressed reachable D85 findings
- **THEN** it reports what it changed, the verification evidence, and any unresolved certification gaps

### Requirement: Builds require source-derived determinism and Lattice evidence

D85 certification SHALL recompute the registered process score and require REALIZED_PASS. Certification SHALL validate canonical Lattice context and recompute its BMS result. Missing, malformed, stale, or inconsistent evidence SHALL fail closed at the build boundary.

#### Scenario: A submitted pass disagrees with source
- **WHEN** a build claims d85_realized_pass but the live score fails
- **THEN** certification refuses CHECKLIST_PASS

#### Scenario: Lattice context is invalid
- **WHEN** routing context is missing, malformed, nonfinite, or disagrees with the computed BMS mode
- **THEN** certification refuses the build

#### Scenario: Source changes after certification
- **WHEN** a saved certificate is verified against changed source or build evidence
- **THEN** verification refuses CERTIFICATION_VERIFIED
