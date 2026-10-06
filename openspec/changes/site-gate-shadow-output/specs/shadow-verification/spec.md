## ADDED Requirements

### Requirement: Preserve the input workspace in shadow mode
The gate SHALL implement an explicit stdout-only dry-run mode that performs existing validation without creating directories or replacing any input result, artifact or metadata.

#### Scenario: Successful signed synthetic fixture
- **GIVEN** a complete signed fixture and an existing v1 PASS result
- **WHEN** the gate runs with `--dry-run` and mocked external boundaries
- **THEN** it SHALL emit a JSON PASS report, exit 0 and preserve all input bytes and directory/file metadata

#### Scenario: Failed quality or missing trust
- **GIVEN** a low actual Lighthouse score or missing authorized verifier trust
- **WHEN** the gate runs with `--dry-run`
- **THEN** it SHALL emit a JSON FAIL report, exit 1 and preserve the entire input tree

### Requirement: Refuse unsafe shadow side effects
Shadow mode SHALL reject Airtable writes and any output-path option before evaluation and SHALL propagate the mode to every portfolio child.

#### Scenario: Provider-write request
- **GIVEN** `--dry-run --airtable-record`
- **WHEN** arguments are parsed
- **THEN** the command SHALL exit 2 without evaluation or workspace/provider writes

#### Scenario: Output aliases
- **GIVEN** an output argument naming an existing file, symlink, hardlink, input directory or new path
- **WHEN** the stdout-only command receives `--output`
- **THEN** the command SHALL reject the unsupported option without mutating any path

#### Scenario: Portfolio child rejection
- **GIVEN** ten distinct offering slugs and untrusted evidence
- **WHEN** the portfolio runs in dry-run mode
- **THEN** each launched child SHALL receive `--dry-run` and rejection SHALL leave the input tree unchanged

### Requirement: Preserve legacy non-shadow semantics
Invocations without dry-run SHALL retain existing RUNNING invalidation, final result writes, exit codes and explicitly requested Airtable behavior.

#### Scenario: Legacy failed recheck
- **GIVEN** a planted PASS report and missing authorized trust
- **WHEN** the gate runs without `--dry-run`
- **THEN** the legacy report SHALL be overwritten by FAIL and requested Airtable Done SHALL be false
