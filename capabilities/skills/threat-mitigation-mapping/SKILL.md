---
name: threat-mitigation-mapping
description: Map identified threats to appropriate security controls and mitigations. Use when prioritizing security investments, creating remediation plans, or validating control effectiveness.
outcome: "security-review: every identified threat maps to a named control with its effectiveness and residual risk stated, so remediation is prioritized by evidence"
done_when:
  - file:capabilities/skills/threat-mitigation-mapping/SKILL.md
  - grep:capabilities/skills/threat-mitigation-mapping/SKILL.md:mitigation
great_example: examples/great/security-review/threat-mitigation-mapping.md
quality_floor: 0.6
---

# Threat Mitigation Mapping

Connect threats to controls for effective security planning.

## When to Use This Skill

- Prioritizing security investments
- Creating remediation roadmaps
- Validating control coverage
- Designing defense-in-depth
- Security architecture review
- Risk treatment planning

## Core Concepts

### 1. Control Categories

```
Preventive ────► Stop attacks before they occur
   │              (Firewall, Input validation)
   │
Detective ─────► Identify attacks in progress
   │              (IDS, Log monitoring)
   │
Corrective ────► Respond and recover from attacks
                  (Incident response, Backup restore)
```

### 2. Control Layers

| Layer           | Examples                             |
| --------------- | ------------------------------------ |
| **Network**     | Firewall, WAF, DDoS protection       |
| **Application** | Input validation, authentication     |
| **Data**        | Encryption, access controls          |
| **Endpoint**    | EDR, patch management                |
| **Process**     | Security training, incident response |

### 3. Defense in Depth

```
                    ┌──────────────────────┐
                    │      Perimeter       │ ← Firewall, WAF
                    │   ┌──────────────┐   │
                    │   │   Network    │   │ ← Segmentation, IDS
                    │   │  ┌────────┐  │   │
                    │   │  │  Host  │  │   │ ← EDR, Hardening
                    │   │  │ ┌────┐ │  │   │
                    │   │  │ │App │ │  │   │ ← Auth, Validation
                    │   │  │ │Data│ │  │   │ ← Encryption
                    │   │  │ └────┘ │  │   │
                    │   │  └────────┘  │   │
                    │   └──────────────┘   │
                    └──────────────────────┘
```

## Templates and detailed worked examples

Full template library and detailed mitigation/control mappings live in . Read that file when you need the concrete templates for: Mitigation Model, Defense in Depth scoring, Executive Summary scaffolding, Critical Gaps reporting, Recommendations, Implementation Roadmap, Results by Control.

## Best Practices

### Do's

- **Map all threats** - No threat should be unmapped
- **Layer controls** - Defense in depth is essential
- **Mix control types** - Preventive, detective, corrective
- **Track effectiveness** - Measure and improve
- **Review regularly** - Controls degrade over time

### Don'ts

- **Don't rely on single controls** - Single points of failure
- **Don't ignore cost** - ROI matters
- **Don't skip testing** - Untested controls may fail
- **Don't set and forget** - Continuous improvement
- **Don't ignore people/process** - Technology alone isn't enough
