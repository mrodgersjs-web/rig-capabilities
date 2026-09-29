---
name: prototype-state-machine
tier: sub
parent: ds-motion-3d
---

# Prototype State Machine

Purpose: board the beats, name the layers, build variants, and wire only the gesture that should fire.

Load when: the task touches this part of motion and 3d, or a ds-motion-3d critique names it. Part of `ds-motion-3d`.

## Checklist
1. Work through every law below against the current artifact before calling the sub-topic done.
2. Cite the CLAIM when a law drives a decision; a law you cannot cite is labeled own reasoning.
3. Where creators disagree (see the SKILL.md), state both positions and test rather than assume.

## Laws owned here
| # | law | creators | citations | consensus | top-10 source |
|---|---|---|---|---|---|
| 1 | Draw every beat as a named state before you connect anything: one frame or segment per rest, hover, press, or destination. A component set, a variant list, or a timeline cut at the moment the action changes all count. Do not invent the path while you are wiring arrows. | Flux Academy, Jesse Showalter, Punit Chawla | CLAIM(20IfkyJigKg@00:49, 20IfkyJigKg@01:54, 4YFRYho3vuM@02:28, d5ngkWU2TY8@00:54, d5ngkWU2TY8@02:38, K0Dh-8rHMLk@04:08, P8hh8K1EuWE@01:14) | consensus | yes |
| 2 | Give every layer that must morph the same name in every state. A matcher only interpolates layers it can pair. A long chain with default names becomes unreadable, so rename before the chain grows. | Flux Academy | CLAIM(hHp4FGVcHjY@02:26, hHp4FGVcHjY@14:51, vCru1T5ajF8@13:25, 20IfkyJigKg@05:13) | single-source | yes |
| 3 | Leave the arriving property in the start state even when it is invisible: a fill at 0 percent, a mask parked just outside the shape, or the incoming chips sitting below a clipped frame. If the layer is missing from the previous frame, it pops or fades instead of traveling. | Flux Academy | CLAIM(hHp4FGVcHjY@02:21, hHp4FGVcHjY@02:45, vCru1T5ajF8@03:04, 20IfkyJigKg@16:45, 20IfkyJigKg@16:57) | single-source | yes |
| 4 | Connect drag or click only between neighboring states. A finger cannot jump from the far-left card to the far-right card in one swipe, so do not draw that arrow. | Flux Academy | CLAIM(4YFRYho3vuM@03:39, 4YFRYho3vuM@03:48, vCru1T5ajF8@11:38, vCru1T5ajF8@12:06) | single-source | yes |
| 5 | Put the prototype on the component, then drop instances into the screen. One timing fix on the main component updates every copy. | Flux Academy | CLAIM(hHp4FGVcHjY@06:02, hHp4FGVcHjY@09:46, 4YFRYho3vuM@04:17) | single-source | yes |
| 6 | Match the trigger to the act. Click, drag, hover, or a directional press should be what the person does. Use after-delay or on-load only for a settle or a loop that must start without a second tap. | Flux Academy, Jesse Showalter, Punit Chawla | CLAIM(hHp4FGVcHjY@04:14, hHp4FGVcHjY@04:31, vCru1T5ajF8@03:54, 20IfkyJigKg@07:44, d5ngkWU2TY8@04:36, fB7h2RxXpqA@08:12, K0Dh-8rHMLk@05:06, gXOY8Ts44dA@08:01) | consensus | yes |
| 7 | Preview in a named flow, name the fault (knob leaving the track, a radius pop, a linear loop), change that one property, and preview again. Do not lock the first easing guess. | Flux Academy, kwoo studio, Envato Tuts+ | CLAIM(hHp4FGVcHjY@10:41, hHp4FGVcHjY@10:49, 20IfkyJigKg@09:34, 20IfkyJigKg@16:26, -QuzxYtwkyU@09:46, 8D6b3McyhhU@03:49, 8D6b3McyhhU@04:00) | consensus | yes |
| 8 | Write the motion strategy before the timeline: a board of frames for a UI story, or research-backed intent for a brand system. Opening the editor with no path means you animate blind. | Flux Academy, kwoo studio | CLAIM(20IfkyJigKg@00:49, 20IfkyJigKg@02:00, -QuzxYtwkyU@12:06, -QuzxYtwkyU@12:26) | consensus | yes |
| 9 | When one control needs both hover and active, make those variants of one component. A new screen for every combination tangles the file. | Flux Academy | CLAIM(20IfkyJigKg@02:46, 20IfkyJigKg@03:27, 20IfkyJigKg@04:47) | single-source | yes |
| 10 | Send a back control to the resting state, not the hover you passed through. The closed card should not stay highlighted after the person leaves. | Flux Academy | CLAIM(20IfkyJigKg@18:29, 20IfkyJigKg@18:32) | single-source | yes |
| 11 | An interactive file has four parts: a state (a playable segment), a transition between states, an input the transition checks, and an interaction that fires the input. Cut segments where the picture actually changes, and set which state is initial. | Jesse Showalter | CLAIM(d5ngkWU2TY8@00:52, d5ngkWU2TY8@01:12, d5ngkWU2TY8@01:26, d5ngkWU2TY8@01:38, d5ngkWU2TY8@03:58) | single-source | yes |
| 12 | Loop an idle by playing one direction and reversing it, instead of authoring both ways. A boolean (still on the first side, or not) is enough to flip a toggle. Directional presses (left, right, up, down) each need their own scene. | Jesse Showalter | CLAIM(d5ngkWU2TY8@07:01, d5ngkWU2TY8@07:03, d5ngkWU2TY8@07:23, d5ngkWU2TY8@10:10, d5ngkWU2TY8@10:17) | single-source | yes |
| 20 | Build a carousel as an auto-layout stack inside a centered, clipping frame, then duplicate that frame once per resting position. Do not keyframe one card through every slot. | Flux Academy | CLAIM(4YFRYho3vuM@01:12, 4YFRYho3vuM@01:56, 4YFRYho3vuM@02:01, 4YFRYho3vuM@02:06) | single-source | yes |
| 21 | For a word that swaps inside a sentence, isolate it in a frame one line tall and as wide as the longest word, right-align the text, clip overflow, and auto-layout it with the static words set to hug and center so the line stays centered as width changes. | Flux Academy | CLAIM(vCru1T5ajF8@18:49, vCru1T5ajF8@19:28, vCru1T5ajF8@19:49, vCru1T5ajF8@20:20, vCru1T5ajF8@23:15, vCru1T5ajF8@23:24) | single-source | yes |
| 22 | Stack duplicate type or shapes, then step each lower layer by a fixed offset (about 4 px down and 4 px sideways) and a fixed rotation step (about 2 degrees) so a drag between two frames reads as depth. | Flux Academy | CLAIM(vCru1T5ajF8@14:38, vCru1T5ajF8@14:45, vCru1T5ajF8@15:14) | single-source | yes |
| 23 | Reveal a line by masking a colored rectangle over the vector. Park the rectangle just outside the line at the start and just past the end at the finish. Never pull the mask outside the component frame. | Flux Academy | CLAIM(vCru1T5ajF8@02:29, vCru1T5ajF8@03:04, vCru1T5ajF8@03:17) | single-source | yes |
| 24 | Put expanding rows in auto layout with a fixed width, vertical hug, and a constant gap (about 20 px). Fix the section height and clip content so opening one row pushes the others by the same amount. | Flux Academy | CLAIM(hHp4FGVcHjY@14:15, hHp4FGVcHjY@19:43, hHp4FGVcHjY@20:43, hHp4FGVcHjY@20:51, hHp4FGVcHjY@21:08) | single-source | yes |
| 25 | Make the tap target the whole row or control, not only the tiny icon, unless the icon is the only affordance. | Flux Academy | CLAIM(hHp4FGVcHjY@16:21, hHp4FGVcHjY@16:27) | single-source | yes |
| 26 | Fake a photo swap by stacking images in a vertical auto layout and shifting which image sits at the top, so the change reads as a scroll rather than a crossfade. | Flux Academy | CLAIM(20IfkyJigKg@12:57, 20IfkyJigKg@13:01, 20IfkyJigKg@13:25) | single-source | yes |
| 27 | Clip content to hide a part that should enter later (an arrow, a label). Move it outside the frame in the default variant and inside the frame in the hover variant. | Flux Academy | CLAIM(20IfkyJigKg@03:52, 20IfkyJigKg@04:08, 20IfkyJigKg@06:14) | single-source | yes |

## Anti-patterns for this sub-topic
- Connecting non-adjacent carousel states with one drag. CLAIM(4YFRYho3vuM@03:48)
- Deleting a layer in the start state and expecting a fade or a travel. CLAIM(hHp4FGVcHjY@02:45, 20IfkyJigKg@16:45)
- Returning a back control to the hover state. CLAIM(20IfkyJigKg@18:32)
