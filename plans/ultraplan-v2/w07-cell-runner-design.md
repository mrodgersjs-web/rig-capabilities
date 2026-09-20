# W07 approach (design note, not a stub — implementation follows)

Nine studios exist as VALID CELLS (tree 33/33). The W07 board rows name per-op
cells (persona-panel, bank-harvest, ... 23 ops). One runner, 23 configs:

- runtime/cell_runner.py: load cell dir -> validate_cell (contract holds or refuse)
  -> read harness.yaml (inputs, outputs, gates, budget, red_path) -> execute the
  op's declared code-check command over an input envelope -> route each declared
  gate via rig-ultra (offline first; --live only with explicit flag) -> attach a
  receipt event (receipt.attach with evidence path+sha) through runtime/cli.py.
- Per-op config files live at the cell itself (studios/<studio>/<op>/...), built
  from the existing stage dirs (question/, research/ exist at root today; the
  contract's op names map 1:1 to the canvas cell map classes).
- JEX per op: claim "the <op> cell's harness gate refuses an empty input" with
  cmd running validate + the plant-failure runner. One PASS per op closes one row.

Why not stubs: a generated 8-slot bundle with vacuous prompts is inventory, not
behavior. Each op's done-test must EXECUTE something. Order: build runner + 3
anchor ops (persona-panel, corpus-first, forecast-brief), then replicate.
