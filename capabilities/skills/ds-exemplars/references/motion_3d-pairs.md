# motion_3d: looks like / does not

Owning main skill: ds-motion-3d. Every row paraphrases a good-versus-bad contrast a creator showed, cited to the moment. Use as calibration before judging a screen; a card is only reusable as a visual reference after Jev ui.design scores the good side above the bad side.

| # | looks like (good) | does not (bad) | why | citation |
|---|-------------------|----------------|-----|----------|
| 1 | A board of named states drawn before any arrow | One screen, with the path invented while prototyping | You cannot animate a story you have not mapped | CLAIM(20IfkyJigKg@00:49, 20IfkyJigKg@02:00) |
| 2 | Drag arrows only between neighboring carousel states | A single drag from the far-right card straight to the far-left card | A finger cannot skip the middle card | CLAIM(4YFRYho3vuM@03:48, 4YFRYho3vuM@03:56) |
| 3 | Fill present at 0 percent in the empty state, then rising as the icon grows | Fill added only on the last frame, so the color pops | Interpolation needs the same layer in both states | CLAIM(hHp4FGVcHjY@02:21, hHp4FGVcHjY@02:45) |
| 4 | One tap grows the icon, then a 1 ms delay settles it | A second click required to finish the bounce | The settle is not a user decision | CLAIM(hHp4FGVcHjY@04:14, hHp4FGVcHjY@04:19) |
| 5 | Knob shrunk so a spring hits the track edge and returns inside | Default bounce that leaves the pill | Overshoot past the container reads as a bug | CLAIM(hHp4FGVcHjY@10:00, hHp4FGVcHjY@10:34) |
| 6 | Plus rotates into a minus, color held constant | Plus that changes shape and color in the same beat | Two signals at once feel jarring | CLAIM(hHp4FGVcHjY@15:16, hHp4FGVcHjY@15:46) |
| 7 | Incoming chips parked below the clip in the previous frame | Chips that exist only on the destination and fade in | Travel needs the layer in both frames | CLAIM(20IfkyJigKg@16:45, 20IfkyJigKg@17:02) |
| 8 | Back control returns to the resting card | Back control returns to the hovered card | Leaving should clear the hover | CLAIM(20IfkyJigKg@18:32) |
| 9 | Headline cycle that mixes short and long words | A cycle that always grows then shrinks | Predictable size order feels mechanical | CLAIM(vCru1T5ajF8@25:34, vCru1T5ajF8@25:38) |
| 10 | Layers eased, then offset so they do not start together | Every layer on a linear keyframe at the same time | Simultaneous starts do not look physical | CLAIM(-QuzxYtwkyU@09:46, -QuzxYtwkyU@10:54) |
| 11 | Sticky block, parents set to visible overflow, blank gaps underneath | Sticky with a hidden parent overflow and no space below | Sticky is ignored unless parents can overflow | CLAIM(P8hh8K1EuWE@02:30, P8hh8K1EuWE@03:14) |
| 12 | Scroll variant on a component, both directions | Scroll variant attempted on plain text, or only on the way down | The effect needs variants, and a one-way hijack feels broken on the way up | CLAIM(P8hh8K1EuWE@05:09, P8hh8K1EuWE@05:43) |
| 13 | One face, near-monochrome, air, then motion | Motion dropped on a cramped, multi-font page | Restraint is what makes the scroll shot look costly | CLAIM(q5UFK4ziDuE@01:01, q5UFK4ziDuE@02:18) |
| 14 | A clip scrubbed between a first frame and a last frame, edges faded | A prompt that only says to make a cool video, or a hard rectangle where colors miss | Vague prompts fight you, and monitors grade color differently | CLAIM(q5UFK4ziDuE@04:03, q5UFK4ziDuE@07:50) |
| 15 | Card scaled with a transform, neighbors unmoved | Card resized in the layout, neighbors shoved aside | Transform scale does not reflow | CLAIM(gXOY8Ts44dA@00:49, gXOY8Ts44dA@01:05) |
| 16 | 3D rotate plus perspective, one vanishing point | Flat 2D rotate, or 3D rotate with no perspective | Without perspective the flip has no depth | CLAIM(gXOY8Ts44dA@01:56, gXOY8Ts44dA@02:33) |
| 17 | Inner chips flying off on their own offsets, ease-in-out | The whole card tilting as one slab on a linear loop | Separate pieces are the point of the hover | CLAIM(gXOY8Ts44dA@04:10, gXOY8Ts44dA@09:00) |
| 18 | Two pages, one word changed, about 3 seconds each | One still with every effect turned on | The story is the change between states | CLAIM(acjm7wBcrMs@03:24, acjm7wBcrMs@10:14) |
| 19 | Elements snapped to the center guide, scaled as one group | Copies scattered off-axis at mismatched sizes | Alignment is what makes a stack look intentional | CLAIM(acjm7wBcrMs@06:07, acjm7wBcrMs@06:18) |
| 20 | Black-field clip above a matched-length plate, blend dropping the black, curves shifted | The source clip dropped on a light plate with its original color | Screen-style blend needs black, and an unrecolored reuse is a copy | CLAIM(v1hw3VUnUYc@01:27, v1hw3VUnUYc@03:11, v1hw3VUnUYc@04:00) |
| 21 | Stroke icon pulled from its frame and flattened to one outline | A filled icon, or a multi-part group, sent straight to a path animator | Path draw needs one continuous stroke | CLAIM(EEj3PYjwyC0@00:45, EEj3PYjwyC0@01:09) |
| 22 | Soft raised tile the same color as the page, two opposing shadows | A tile with a different fill and a single hard drop shadow | The soft look depends on matched color and a light-dark pair | CLAIM(fB7h2RxXpqA@02:02, fB7h2RxXpqA@02:07) |
| 23 | Smoke at low opacity, mask feathered until the edge is gone | Noise at full opacity with a sharp mask edge | Atmosphere should sit in the scene, not cut a hole in it | CLAIM(ptQ6Re6JvWM@06:51, ptQ6Re6JvWM@07:45) |
| 24 | Liquid cycling forward, ease-out, shown through a subtracted glyph | A rewind on the loop, or the mesh sitting beside the icon | Rewind reads as a glitch, and the glyph is the mask | CLAIM(K0Dh-8rHMLk@05:25, K0Dh-8rHMLk@08:11) |
