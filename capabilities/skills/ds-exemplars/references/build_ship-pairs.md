# build_ship: looks like / does not

Owning main skill: ds-build-ship. Every row paraphrases a good-versus-bad contrast a creator showed, cited to the moment. Use as calibration before judging a screen; a card is only reusable as a visual reference after Jev ui.design scores the good side above the bad side.

| # | looks like (good) | does not (bad) | why | citation |
|---|-------------------|----------------|-----|----------|
| 1 | A pasted design that arrives with responsive behavior, working buttons and named classes. | A pasted design that arrives as fixed or absolutely placed boxes. | The exporter can only transfer layout logic that was authored as layout logic. | CLAIM(xHXqj006Q2k@00:44, xHXqj006Q2k@02:49) |
| 2 | A hero whose text sits in a wrapper with center alignment and cannot be moved. | A hero where an element is dragged to a spot that happens to look right. | Free placement looks right at one width and breaks at every other. | CLAIM(P5H7zs0RsUM@07:37, P5H7zs0RsUM@08:14) |
| 3 | Content centered in a fixed container with equal side tracks on a wide screen. | Content pinned to the full canvas width of the desktop artboard. | The container is what makes one design work across screen widths. | CLAIM(BNYLKuIlazA@01:54, xHXqj006Q2k@00:26) |
| 4 | One grid class shared by every aligned group, with a combo class for the single exception. | Three near-identical grids styled separately. | Separate copies must be re-tuned three times per breakpoint. | CLAIM(WLDfFqnqbxI@03:38, WLDfFqnqbxI@04:40) |
| 5 | A card whose corner radius clips its own image via overflow hidden. | A rounded card whose square image still bleeds past the corners. | Radius applies to the container, the child image needs clipping to obey it. | CLAIM(WLDfFqnqbxI@11:34, WLDfFqnqbxI@11:49) |
| 6 | A button reused from one master with a hover variant. | Several hand-styled button copies with slightly different padding. | Copies drift; a master keeps the system consistent. | CLAIM(P5H7zs0RsUM@16:40, P5H7zs0RsUM@18:14) |
| 7 | Text aligned on a shared baseline after a deliberate margin nudge. | Text that looks aligned by box but sits high or low on the line. | Bounding boxes include descender space, so box alignment is not optical alignment. | CLAIM(WLDfFqnqbxI@08:25, WLDfFqnqbxI@09:00) |
| 8 | A heading that scales down smoothly with the window. | A heading fixed in pixels that overflows the narrow viewport. | Viewport sizing keeps a display line to one piece across widths. | CLAIM(WLDfFqnqbxI@07:23, WLDfFqnqbxI@07:35) |
