# Determinism admission

## Context

Production processes require source-derived evidence before deterministic scoring. D85 admission and Gate-D authorization are independent.

## ADDED Requirements

### Requirement: Source-derived operation inventory
The system MUST derive structural symbols and provisional inventory IDs for exact sequential builtin or locked external-module call-site stages from fixed authority entrypoints and adapter roots.

#### Scenario: Hidden local operation is discovered
- **GIVEN** a registered entrypoint and source hash
- **WHEN** the source adds a statically reachable local function
- **THEN** the extracted inventory MUST include the new structural symbol and any reachable call-site operation
- **AND** a stale submitted inventory MUST return `BLOCK`

#### Scenario: Dynamic reachability is unresolved
- **GIVEN** a registered Python entrypoint
- **WHEN** a call target cannot be resolved from the closed static graph
- **THEN** extraction MUST return `BLOCK`

#### Scenario: External module call is locked without import execution
- **GIVEN** an authority record names one top-level single-file source module, its deterministic origin, its SHA-256, and a statically defined call
- **WHEN** the registered source calls that exact module symbol
- **THEN** the inventory MUST bind module initialization and the call into one provisional stage
- **AND** the stage MUST remain credit-ineligible with runtime loader proof false
- **AND** a preloaded or redirected module, package, extension, missing symbol, undeclared call, or unused declaration MUST return `BLOCK`

### Requirement: Exact inventory comparison
The system MUST compare the submitted inventory with the extracted inventory exactly.

#### Scenario: Caller adds padding
- **GIVEN** a current extracted inventory
- **WHEN** the submitted inventory adds or splits an operation
- **THEN** comparison MUST return `BLOCK`

#### Scenario: Provisional stages cannot improve D85
- **GIVEN** an exact source-derived inventory
- **WHEN** it contains syntactically distinct or semantically redundant call-site stages
- **THEN** every provisional stage MUST remain credit-ineligible
- **AND** classification MUST mint final operation identities before any ratio exists

#### Scenario: Sentinel iter invokes caller code
- **GIVEN** a source function calling two-argument `iter(callable, sentinel)`
- **WHEN** extraction inventories its call sites
- **THEN** extraction MUST return `BLOCK`
- **AND** one-argument `iter(value)` MUST remain an admissible builtin stage

#### Scenario: External artifact aliases a hashed inode
- **GIVEN** an authority record binding an external artifact
- **WHEN** the artifact path resolves to an inode already bound by `file_hashes` or by another external module
- **THEN** extraction MUST return `BLOCK`

### Requirement: Determinism threshold
The system MUST require aggregate weighted, aggregate unweighted, minimum-path weighted, and minimum-path unweighted ratios of at least 0.85.

#### Scenario: One ratio is below threshold
- **GIVEN** a fully classified realized graph
- **WHEN** any required ratio is below 0.85
- **THEN** the D85 gate MUST return `BLOCK`

### Requirement: Critical controls use code
The system MUST classify every critical control as CODE.

#### Scenario: Model owns a critical control
- **GIVEN** a realized process graph
- **WHEN** a model owns scheduling, state, retry, timeout, cancellation, compensation, permission, budget, idempotency, approval, dispatch, verdict, acceptance, or proof
- **THEN** the D85 gate MUST return `BLOCK`

### Requirement: Model use proves necessity
The system MUST require each model operation to provide typed boundaries, positive bounded budgets, necessity evidence, and reachable CODE validator, fallback, and failure-state nodes.

#### Scenario: Model fallback is not reachable
- **GIVEN** a classified model operation
- **WHEN** its declared CODE fallback is not reachable in the realized graph
- **THEN** the D85 gate MUST return `BLOCK`

### Requirement: D85 and Gate-D remain separate
The system MUST treat D85 as eligibility and Gate-D as authorization for one exact outward or irreversible action.

#### Scenario: D85 passes without an effect request
- **GIVEN** a valid internal process with a passing D85 proof
- **WHEN** no outward or irreversible effect is requested
- **THEN** the internal proof MUST terminate without Gate-D

#### Scenario: Effect approval is missing
- **GIVEN** a passing D85 proof and an outward action
- **WHEN** authenticated exact-action approval is missing, corrupt, expired, mismatched, consumed, or redirected
- **THEN** Gate-D MUST return `BLOCK`

### Requirement: Classification is authority-owned
The system MUST bind runtime kind and taxonomy to every extracted operation from a separate authority classification file whose ID set equals the extracted inventory.

#### Scenario: Classification set diverges from inventory
- **GIVEN** an extracted realized inventory
- **WHEN** the classification omits, duplicates, adds, or stale-binds an operation ID
- **THEN** classification MUST return `BLOCK`

#### Scenario: Classification rewires the realized graph
- **GIVEN** a classification covering exactly the extracted IDs
- **WHEN** its edges form a connected acyclic graph with mirrored bindings
- **THEN** final operation identities MUST be minted from the remapped graph

### Requirement: Every failure ends the attempt
The system MUST make each failed gate terminal for the current immutable attempt.

#### Scenario: A gate fails
- **GIVEN** a versioned process attempt
- **WHEN** any admission gate returns `BLOCK`
- **THEN** no outgoing execution edge MUST run
- **AND** a new immutable version MUST be required to re-enter the gate

### Requirement: Four agent surfaces share one rule
Claude Code, Hermes, OMP, and Prime-Agent MUST load and execute the same D85 rule hash.

#### Scenario: One surface diverges
- **GIVEN** four configured coding-agent surfaces
- **WHEN** one surface is missing, unregistered, or has another rule hash
- **THEN** global D85 wiring MUST return `BLOCK`

## Source evidence

- `docs/DETERMINISM_85_DOCTRINE.md`
- `capabilities/skills/rig-determinism-85/d85.py`
- `capabilities/skills/rig-determinism-85/d85_gates.py`
- `tests/test_determinism_85.py`
- `tests/test_d85_gates.py`
