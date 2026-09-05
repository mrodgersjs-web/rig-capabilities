---
name: great-hA-11-infra-iac-yaml
lane: infra-ops
exemplar_of: hA-11-infra-iac.yaml
description: Reference exemplar for a reviewable Terraform plan with state, policy, cost, blast-radius, and rollback proof before apply.
---

# hA-11-infra-iac.yaml — great example

## Input

Change a pinned Terraform module in a named workspace backed by remote, lock-enabled state. The request changes an application service and shared IAM policy, so the plan must expose replacements, cost delta, affected services, and an exact rollback path. Applying the plan is outside this session.

## Output

The operator records format and validation output, static security findings, a binary plan plus JSON rendering, destroy/replace review, policy verdict, cost estimate, drift-before snapshot, blast-radius map, rollback commands, and `.rig/iac/APPLY-REQUEST.md`.

```console
$ terraform fmt -check -recursive && terraform validate
# expected: exit 0; output copied to .rig/iac/fmt-validate.txt

$ terraform plan -out=.rig/iac/tfplan && terraform show -json .rig/iac/tfplan > .rig/iac/tfplan.json
# expected: both plan artifacts exist; every destroy or replacement is dispositioned

$ conftest test .rig/iac/tfplan.json
# expected: policy checks pass or each violation has an approved waiver
```

## Acceptance

- Remote backend, state locking, and refresh-only drift evidence are named.
- Provider/module references are pinned and the secret scan has no live credential finding.
- The plan review accounts for every destroy/replace and maps shared resources to services.
- `APPLY-REQUEST.md` carries plan path, destroy summary, cost delta, blast radius, and rollback pointer; no `terraform apply` occurs.
