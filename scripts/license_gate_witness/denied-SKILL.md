---
name: license-gate-witness-denied
description: Fixture asset with no license evidence, used to prove the store gate refuses archival.
license: unknown
---

# License-Gate Witness (denied)

Deliberately unlicensed. Nothing here is cleared for archiving: there is no
`LICENSE`, no SPDX header, and no upstream grant.

The store gate must refuse to write this asset into
`docs/skillos/warehouse/`, and `skillos check --stores` must not count it as
valid even if a ledger entry is forged after the fact.
