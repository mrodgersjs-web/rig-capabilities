---
name: license-gate-witness-denied
description: Fixture asset with no license evidence, used to prove the store gate refuses archival.
license: unknown
---

# License-Gate Witness (denied)

Deliberately unlicensed. Nothing here is cleared for archiving: there is no
`LICENSE`, no SPDX header, and no upstream grant.

The plant copies these exact bytes into a canonical-shaped temporary asset,
passes that asset through `_store_for`, and requires an unresolved result with
no file created under the temporary `docs/skillos/warehouse/`.
