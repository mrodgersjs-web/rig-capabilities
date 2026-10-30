## ADDED Requirements

### Requirement: Employment answers SHALL be bound to the selected résumé
The workflow SHALL pin the résumé hash, use explicit employer aliases, and answer No for prior employment outside the résumé under Mike's standing instruction.

#### Scenario: A partner is misclassified as an employer
- **GIVEN** a company absent from the employer baseline
- **WHEN** an answer claims prior employment there
- **THEN** the structured checker rejects it

#### Scenario: An explicit résumé alias is used
- **GIVEN** a matching résumé hash and an explicit employer alias
- **WHEN** a prior-employment answer is Yes with the corresponding employer source
- **THEN** the structured checker accepts it

#### Scenario: Source bytes change
- **GIVEN** a packet bound to the baseline hash
- **WHEN** the selected résumé bytes differ
- **THEN** the checker rejects the packet until the baseline is rebuilt

### Requirement: Unrelated answers SHALL NOT inherit the employer No rule
The workflow SHALL preserve unknown required answers and demand their own source. The checker SHALL remain a structured check and SHALL NOT claim semantic review or submission authority.

#### Scenario: Sponsorship answer is inferred from employment omission
- **GIVEN** an unrelated required question
- **WHEN** No is sourced only to the employer rule
- **THEN** the checker rejects the answer

#### Scenario: An optional question is left blank
- **GIVEN** an explicitly optional question
- **WHEN** no answer is supplied
- **THEN** the structured checker permits it without inferring an answer

### Requirement: Application state SHALL distinguish preparation from submission
The skill SHALL record a real confirmation before submitted_confirmed and SHALL preserve ambiguous outcomes as submission_unknown. Existing scoped approval SHALL be honored without repeated permission requests. Provider denial SHALL NOT be bypassed.

#### Scenario: A final click times out
- **GIVEN** an authorized application with a recorded attempt
- **WHEN** no role-specific confirmation is observed
- **THEN** the operator records submission_unknown and checks history before any retry
