"""The RIG Deviator surface — auditor, dv pipeline, DES2, hooks, reports.

Vendored from the rig-deviator repo. The 40 deviation engines themselves live
in ``rig_lattice.engines``; this package holds the runners that drive them:
``auditor`` (strict criteria audit), ``dv`` (deviation pipeline), ``modes``,
``patch_overlays``, ``fix_suggestions``, ``result_packet``, ``des_squared`` /
``des2_innerloop`` (amplification + Brier calibration), plus ``pipeline``,
``hooks`` and ``reports``.
"""
